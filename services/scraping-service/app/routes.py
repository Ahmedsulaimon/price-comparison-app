from flask import Blueprint, jsonify, request
from app.scraper import WebScraper

scraper_bp = Blueprint('scraper', __name__)

@scraper_bp.route('/api/scrape', methods=['POST'])
def scrape_url():
    data = request.get_json()
    
    if not data or 'url' not in data:
        return jsonify({
            'success': False,
            'error': 'URL is required'
        }), 400
    
    url = data['url']
    result = WebScraper.scrape_product_info(url)
    
    if result['success']:
        return jsonify(result), 200
    else:
        return jsonify(result), 500

@scraper_bp.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok'}), 200