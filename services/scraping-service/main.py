import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from app.routes import scraper_bp

def create_app():
    app = Flask(__name__)
    
    # Register blueprints
    app.register_blueprint(scraper_bp)
    
    return app

app = create_app()

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=5001,
        debug=True
    )