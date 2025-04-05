import os
from flask import Blueprint, current_app, jsonify, request
import requests
from sqlalchemy import func
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from app.extensions import db

import sys
sys.path.insert(0, os.getcwd()+"/")

from app.models import PriceHistory, Product, Retailer
from app.service import PriceService

product_bp = Blueprint('product', __name__)



@product_bp.route('/api/sync-products', methods=['POST'])
def sync_products():
    retailers = {
        'sainsbury': 'http://scraping-service:5001/browse/sainsbury/freshgroceries',
        'aldi': 'http://scraping-service:5001/browse/aldi/freshgroceries', 
        'morrison': 'http://scraping-service:5001/browse/morrison/freshgroceries',
        'iceland': 'http://scraping-service:5001/browse/iceland/freshgroceries'
    }

    # Configure retry strategy with longer timeouts
    retry_strategy = Retry(
        total=3,
        backoff_factor=2,
        status_forcelist=[500, 502, 503, 504]
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    http = requests.Session()
    http.mount("http://", adapter)

    results = []
    
    # Process retailers sequentially
    for retailer_name, url in retailers.items():
        try:
            current_app.logger.info(f"Starting sync for {retailer_name}")
            
            # Extended timeout for scraping operations
            response = http.get(url, timeout=70)  # 30 second timeout
            response.raise_for_status()
            
            products = response.json()
            processed_count = 0
            
            for product_data in products:
                try:
                    if 'name' not in product_data:
                        current_app.logger.warning(f"Skipping product from {retailer_name} - missing name")
                        continue
                        
                    PriceService.process_scraped_product(product_data, retailer_name)
                    processed_count += 1
                    
                except ValueError as e:
                    current_app.logger.error(f"Invalid product data from {retailer_name}: {str(e)}")
                    continue
            
            results.append({
                'retailer': retailer_name,
                'status': 'success',
                'products_processed': processed_count
            })
            current_app.logger.info(f"Completed sync for {retailer_name} - {processed_count} products")
            
        except requests.RequestException as e:
            error_msg = str(e)
            if hasattr(e, 'response') and e.response:
                error_msg = f"{e.response.status_code} {e.response.text}"
                
            current_app.logger.error(f"Failed sync for {retailer_name}: {error_msg}")
            results.append({
                'retailer': retailer_name,
                'status': 'failed',
                'error': error_msg
            })
            continue

    return jsonify({
        'message': 'Sync completed',
        'results': results
    }), 200


@product_bp.route('/api/products/compare', methods=['GET'])
def compare_products():
    product_name = request.args.get('name')
    retailer = request.args.get('retailer')
    
    if not product_name:
        return jsonify({'error': 'Missing required parameter: name'}), 400
    
    try:
        with current_app.app_context():
            # Base query
            query = db.session.query(Product).filter(
                func.lower(Product.name).contains(func.lower(product_name)))
            
            if retailer:
                query = query.join(Retailer).filter(
                    func.lower(Retailer.name) == func.lower(retailer))
            
            products = query.all()
            
            if not products:
                return jsonify({'message': 'No matching products found'}), 404
                
            result = []
            for p in products:
                # Get most recent price history
                latest_price = db.session.query(PriceHistory.unit_price)\
                    .filter_by(product_id=p.product_id)\
                    .order_by(PriceHistory.scraped_at.desc())\
                    .first()
                
                result.append({
                    'id': str(p.product_id),
                    'name': p.name,
                    'retailer': p.retailer.name,
                    'price': float(p.current_price),
                    'rating': float(p.rating) if p.rating else None,
                    'unit_price': float(latest_price[0]) if latest_price and latest_price[0] else None,
                    'image_url': p.image_url
                })
            
            return jsonify(result)
            
    except Exception as e:
        current_app.logger.error(f"Comparison error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500