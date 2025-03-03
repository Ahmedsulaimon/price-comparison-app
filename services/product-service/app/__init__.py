from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import exc
from time import sleep
from config import Config

# Create database instance
db = SQLAlchemy()

def create_app():
    """Application factory function"""
    app = Flask(__name__)
    
    # Load configuration from config.py
   
    app.config.from_object(Config)
    
    # Initialize database with app
    db.init_app(app)
    
    # Initialize CORS 
    from flask_cors import CORS
    CORS(app)
    
    # Database connection retry logic
    retries = 5
    while retries > 0:
        try:
            with app.app_context():
                db.create_all()
                break
        except exc.OperationalError:
            retries -= 1
            sleep(5)
            if retries == 0:
                raise RuntimeError("Failed to connect to database after 5 attempts")
            
    # Import routes after app creation to avoid circular imports
    from .routes import product_bp
    app.register_blueprint(product_bp)

    return app