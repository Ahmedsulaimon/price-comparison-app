from flask import Flask

from app.config import Config
from app.extensions import db, cors

def create_app(config_class=Config):
    """Application factory function"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    cors.init_app(app)
    
    # Register blueprints
    from . import models
    from app.routes import product_bp
    app.register_blueprint(product_bp)
    
    return app