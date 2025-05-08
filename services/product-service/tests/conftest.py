# tests/conftest.py
from typing import List, Optional
import pytest
from flask import Flask
from app.extensions import db

#python -m pytest tests/ -v
#  Functional Testing & Coverage
# •	6 Pytest integration tests cover all core endpoints; all pass consistently.
# •	Coverage: product Extractors from retailer websites and custom api Routes.



@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize extensionsb
    db.init_app(app)
  
    
    with app.app_context():

       
        from app.routes import product_bp
        app.register_blueprint(product_bp)


        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def sample_product_data():
    return {
        'name': 'Test Product',
        'price': 1.99,
        'url': 'http://example.com/product',
        'external_id': '12345',
        'size': '100g',
        'unit_price': '£1.99/100g',
        'image_url': 'http://example.com/image.jpg',
        'brand': 'Test Brand'
    }