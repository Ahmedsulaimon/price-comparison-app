from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "healthy"})

@app.route("/process-image", methods=["POST"])
def process_image():
    if not request.json or 'image' not in request.json:
        return jsonify({"error": "No image data provided"}), 400
    
    # Forward the request to the image recognition service
    try:
        response = requests.post(
            "http://image-recognition-service:5002/recognize",
            json=request.json
        )
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Service communication error: {str(e)}"}), 502