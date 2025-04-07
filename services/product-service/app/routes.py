
from flask import Blueprint, current_app, jsonify, request
import requests
from sqlalchemy import func
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from app.extensions import db
from app.services.price_generator import PriceGenerator

from app.models import PriceHistory, Product, Retailer
from app.services.data_processing import PriceService

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
                
                history = db.session.query(PriceHistory)\
                .filter_by(product_id=p.product_id)\
                .order_by(PriceHistory.valid_from.desc())\
                .limit(30)\
                .all()
                
                result.append({
                    'id': str(p.product_id),
                    'name': p.name,
                    'retailer': p.retailer.name,
                    'price': float(p.current_price),
                    'rating': float(p.rating) if p.rating else None,
                    'unit_price': float(latest_price[0]) if latest_price and latest_price[0] else None,
                    'base_unit' : p.base_unit,
                    'image_url': p.image_url,
                    'url': p.product_url,
                    'badge': p.badges,
                    'price_history': [{
                            'date': h.valid_from.isoformat(),
                            'price': float(h.price),
                            'unit_price': float(h.unit_price) if h.unit_price else None
                            } for h in history]
                })
            
            return jsonify(result)
            
    except Exception as e:
        current_app.logger.error(f"Comparison error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500
    

@product_bp.route('/api/generate-price-history', methods=['POST'])
def generate_price_history():
    try:
        # Get limit from either JSON body or query parameters
        limit = request.json.get('limit', 100) if request.is_json else request.args.get('limit', 100, type=int)
        
        # Validate limit
        if not 1 <= limit <= 1000:
            return jsonify({'error': 'Limit must be between 1 and 1000'}), 400
            
        PriceGenerator.generate_for_all_products(limit)
        return jsonify({
            'message': f'Price history generation started for {limit} products',
            'limit': limit
        }), 202
        
    except Exception as e:
        current_app.logger.error(f"Price generation error: {str(e)}", exc_info=True)
        return jsonify({'error': 'Failed to start generation'}), 500
    
 
