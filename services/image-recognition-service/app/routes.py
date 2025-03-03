from flask import Flask, request, jsonify
from app.recognition import recognize_image

app = Flask(__name__)

@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "healthy"})

@app.route("/recognize", methods=["POST"])
def recognize():
    if not request.json or 'image' not in request.json:
        return jsonify({"error": "No image data provided"}), 400
    
    result = recognize_image(request.json['image'])
    return jsonify(result)