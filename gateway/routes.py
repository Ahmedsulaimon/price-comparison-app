from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "healthy"})

@app.route("/api/products/grouped", methods=["GET"])
def proxy_grouped_products():
    category = request.args.get("category")
    min_rating = request.args.get("min_rating")
    try:
        response = requests.get(
            "http://product-service:5001/api/products/grouped",
            params={"category": category, "min_rating": min_rating}
        )
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Gateway error: {str(e)}"}), 502
