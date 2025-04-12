from flask import Flask, request, jsonify
import requests

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
