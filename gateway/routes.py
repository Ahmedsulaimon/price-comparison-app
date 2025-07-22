from flask import Flask, request, jsonify
import requests
from datetime import datetime
import logging

app = Flask(__name__)

@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "healthy"})

@app.route("/grouped-products", methods=["GET"])
def grouped_products_proxy():
    try:
        response = requests.get("http://product-service:5000/api/products/grouped")
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Service communication error: {str(e)}"}), 502


#price prediction

@app.route("/products-prediction", methods=["GET"])
def products_prediction_proxy():
    try:
        # Forward pagination parameters
        page = request.args.get('page', default=1, type=int)
        per_page = request.args.get('per_page', default=20, type=int)
        search_query = request.args.get('search', default=None, type=str)
        
        # Add timeout and forward all query params
        response = requests.get(
            "http://product-service:5000/api/predictions/all",
            params={
                'page': page,
                'per_page': per_page,
                'search' : search_query
            },
            timeout=10  # 10 seconds timeout
        )
        
        # Log successful requests
        logging.info(f"Prediction request served at {datetime.utcnow()}")
        
        return jsonify(response.json())
        
    except requests.exceptions.Timeout:
        logging.error("Product service timeout")
        return jsonify({
            "error": "Product prediction service timed out",
            "status": 504
        }), 504
        
    except requests.exceptions.ConnectionError:
        logging.error("Cannot connect to product service")
        return jsonify({
            "error": "Cannot connect to prediction service",
            "status": 503
        }), 503
        
    except requests.exceptions.RequestException as e:
        logging.error(f"Prediction service error: {str(e)}")
        return jsonify({
            "error": "Prediction service unavailable",
            "details": str(e),
            "status": 502
        }), 502
        
    except Exception as e:
        logging.critical(f"Unexpected error: {str(e)}")
        return jsonify({
            "error": "Internal server error",
            "status": 500
        }), 500