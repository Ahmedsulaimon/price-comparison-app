
import re
from flask import Blueprint, current_app, jsonify, request
import requests
from sqlalchemy import func, or_
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from app.extensions import db
from app.services.price_generator import PriceGenerator

from app.models import PriceHistory, Product, Retailer
from app.services.data_processing import PriceService

from app.ml_training.recommendation_engine import RecommendationEngine


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
    

@product_bp.route('/api/products/compare', methods=['GET'])
def compare_products():
    product_name = request.args.get('name')
    retailer = request.args.get('retailer')
    
    if not product_name:
        return jsonify({'error': 'Missing required parameter: name'}), 400
    
    try:
        # SQLite-compatible search (case-insensitive contains)
        search_pattern = f"%{product_name}%"
        
        with current_app.app_context():
            query = db.session.query(Product).filter(
                Product.name.ilike(search_pattern))
            
            if retailer:
                query = query.join(Retailer).filter(
                    func.lower(Retailer.name) == func.lower(retailer))
            
            query = query.order_by(Product.current_price.asc())
            
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
                    .all()
                
                result.append({
                    'id': str(p.product_id),
                    'name': p.name,
                    'retailer': p.retailer.name,
                    'price': float(p.current_price),
                    'rating': float(p.rating) if p.rating else None,
                    'unit_price': float(latest_price[0]) if latest_price and latest_price[0] else None,
                    'base_unit': p.base_unit,
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


@product_bp.route('/api/recommendations', methods=['GET'])
def get_recommendations():
    product_name = request.args.get('name')
    if not product_name:
        return jsonify({'error': 'Missing product name'}), 400

    try:
        engine = RecommendationEngine()
        results = engine.generate_recommendations(product_name)
        return jsonify(results)
    except Exception as e:
        current_app.logger.error(f"Recommendation error: {str(e)}")
        return jsonify({'error': 'Recommendation failed'}), 500



@product_bp.route('/api/predictions/all', methods=['GET'])
def get_all_predictions():
    try:
        page = request.args.get('page', default=1, type=int)
        per_page = request.args.get('per_page', default=20, type=int)
        search_query = request.args.get('search', default=None, type=str)
        
        with current_app.app_context():
            # Base query with search filter
            query = db.session.query(Product)
            
            if search_query:
                query = query.filter(
                    Product.name.ilike(f'%{search_query}%')
                )
            
            # Order and paginate
            products = query.order_by(Product.current_price.asc())\
                .paginate(page=page, per_page=per_page, error_out=False)
            
            if not products.items:
                return jsonify({'message': 'No products found'}), 404
                
            engine = RecommendationEngine()
            results = []
            
            for product in products.items:
                # Get minimal price history (last 14 days)
                history = db.session.query(PriceHistory)\
                    .filter_by(product_id=product.product_id)\
                    .order_by(PriceHistory.valid_from.desc())\
                    .limit(14)\
                    .all()
                
                product_data = {
                    'id': str(product.product_id),
                    'name': product.name,
                    'retailer': product.retailer.name,
                    'price': float(product.current_price),
                    'rating': float(product.rating) if product.rating else None,
                    'image_url': product.image_url,
                    'url': product.product_url,
                    'price_history': [{
                        'date': h.valid_from.isoformat(),
                        'price': float(h.price)
                    } for h in history]
                }
                
                # Generate prediction
                analyzed = engine._analyze_product(product_data)
                results.append({
                    'id': analyzed['id'],
                    'name': analyzed['name'],
                    'retailer': analyzed['retailer'],
                    'current_price': analyzed['price'],
                    'predicted_price': analyzed['prediction']['predicted_price'],
                    'confidence': analyzed['prediction']['confidence'],
                    'recommendation': analyzed['recommendation'],
                    'value_score': analyzed['value_score'],
                    'image_url': analyzed['image_url'],
                    'url': analyzed['url'],
                    'rating': analyzed['rating']
                })
            
            return jsonify({
                'products': results,
                'page': products.page,
                'per_page': products.per_page,
                'total_pages': products.pages,
                'total_items': products.total
            })
            
    except Exception as e:
        current_app.logger.error(f"Prediction error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

    
group_keywords = [
    {'keyword': 'onion', 'exclude': ['spring']},
    {'keyword': 'banana', 'exclude': ['muller corner','muller corner vanilla']},
    {'keyword': 'oranges'},
    {'keyword': 'skimmed milk', 'exclude': ['semi-skimmed', 'whole', 'semi skimmed']},
    {'keyword': 'semi skimmed milk', 'exclude': ['skimmed', 'whole']},
    {'keyword': 'whole milk', 'exclude': ['skimmed', 'semi-skimmed']},
    {'keyword': 'white potatoes', 'exclude': ['baked']},
    {'keyword': 'baked potatoes', 'exclude': ['white']},
    {'keyword': 'butter'},
    {'keyword': 'carrot'},
    {'keyword': 'cucumber'},
    {'keyword': 'pepper'},
    {'keyword': 'potatoes'},
    {'keyword': 'Bread'},
    {'keyword': 'chicken breast'},
    {'keyword': 'Granulated Sugar'},
    {'keyword': 'rice'},
    {'keyword': 'avocado'},
    {'keyword': 'Baked Beans'},
    {'keyword': 'Muller Corner'}
]



def serialize_product(p):
    latest_price = db.session.query(PriceHistory.unit_price) \
        .filter_by(product_id=p.product_id) \
        .order_by(PriceHistory.scraped_at.desc()).first()

    return {
        'id': str(p.product_id),
        'name': p.name,
        'retailer': p.retailer.name,
        'price': float(p.current_price),
        'rating': float(p.rating) if p.rating else None,
        'unit_price': float(latest_price[0]) if latest_price and latest_price[0] else None,
        'base_unit': p.base_unit,
        'image_url': p.image_url,
        'url': p.product_url,
        'badge': p.badges
    }

@product_bp.route("/api/products/grouped", methods=["GET"])
def grouped_products():
    try:
        result = []
        
        for group in group_keywords:
            keyword = group['keyword']
            excludes = group.get('exclude', [])
            
            # Start with basic case-insensitive contains
            query = db.session.query(Product)\
                     .filter(Product.name.ilike(f"%{keyword}%"))
            
            # Apply exclusions
            for exclusion in excludes:
                query = query.filter(~Product.name.ilike(f"%{exclusion}%"))
            
            # Get products sorted by price
            products = query.order_by(Product.current_price.asc()).all()
            
            if products:
                result.append({
                    'keyword': keyword,
                    'recommended': serialize_product(products[0]),
                    'others': [serialize_product(p) for p in products[1:]]
                })
        
        return jsonify(result if result else {"message": "No matching products found"})

    except Exception as e:
        current_app.logger.error(f"Grouped products error: {str(e)}", exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500

