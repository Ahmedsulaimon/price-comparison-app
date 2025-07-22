# tests/test_routes.py
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
from app.models import Product, Retailer, PriceHistory
from app.extensions import db
import uuid

def test_sync_products(client, sample_product_data):
    # Setup test retailer
    retailer = Retailer(name='test_retailer', base_url='http://test.com')
    db.session.add(retailer)
    db.session.commit()

    # Mock the scraping service response
    mock_response = [sample_product_data]
    
    with patch('requests.Session.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = mock_response
        
        response = client.post('/api/sync-products')
        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == 'Sync completed'
        assert len(data['results']) == 4  # 4 retailers in the route
        
        # Verify product was created
        product = Product.query.first()
        assert product.name == 'Test Product'
        assert float(product.current_price) == 1.99

def test_generate_price_history(client):
    # Create test product with price history
    retailer = Retailer(name='test_retailer', base_url='http://test.com')
    product = Product(
        name='Test Product',
        current_price=1.99,
        product_url='http://test.com',
        retailer=retailer
    )
    db.session.add(retailer)
    db.session.add(product)
    db.session.commit()
    
    # Add initial price history
    history = PriceHistory(
        product_id=product.product_id,
        price=1.99,
        unit_price=1.99,
        valid_from=datetime.utcnow() - timedelta(days=1),
        scraped_at=datetime.utcnow()
    )
    db.session.add(history)
    db.session.commit()
    
    with patch('app.routes.PriceGenerator.generate_for_all_products') as mock_gen:
        response = client.post('/api/generate-price-history', json={'limit': 10})
        assert response.status_code == 202
        mock_gen.assert_called_once_with(10)

def test_compare_products(client):
    # Setup test data
    retailer1 = Retailer(name='Retailer A', base_url='http://a.com')
    retailer2 = Retailer(name='Retailer B', base_url='http://b.com')
    
    product1 = Product(
        name='Test Product A',
        current_price=1.99,
        product_url='http://a.com/1',
        retailer=retailer1
    )
    product2 = Product(
        name='Test Product B',
        current_price=2.99,
        product_url='http://b.com/1',
        retailer=retailer2
    )
    
    db.session.add_all([retailer1, retailer2, product1, product2])
    db.session.commit()
    
    # Test without retailer filter
    response = client.get('/api/products/compare?name=Test Product')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 2
    assert data[0]['price'] == 1.99  # Should be sorted by price
    
    # Test with retailer filter
    response = client.get('/api/products/compare?name=Test Product&retailer=Retailer B')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 1
    assert data[0]['retailer'] == 'Retailer B'

def test_get_recommendations(client):
    with patch('app.routes.RecommendationEngine') as mock_engine:
        mock_instance = mock_engine.return_value
        mock_instance.generate_recommendations.return_value = {'recommendations': []}
        
        response = client.get('/api/recommendations?name=Test Product')
        assert response.status_code == 200
        mock_instance.generate_recommendations.assert_called_once_with('Test Product')

def test_get_all_predictions(client):
    # Setup test data
    retailer = Retailer(name='Test Retailer', base_url='http://test.com')
    product = Product(
        name='Test Product',
        current_price=1.99,
        product_url='http://test.com/1',
        retailer=retailer
    )
    db.session.add(retailer)
    db.session.add(product)
    db.session.commit()
    
    with patch('app.routes.RecommendationEngine') as mock_engine:
        mock_instance = mock_engine.return_value
        mock_instance._analyze_product.return_value = {
            'id': str(product.product_id),
            'name': 'Test Product',
            'retailer': 'Test Retailer',
            'price': 1.99,
            'prediction': {'predicted_price': 1.89, 'confidence': 0.8},
            'recommendation': 'buy',
            'value_score': 85,
            'image_url': None,
            'url': 'http://test.com/1',
            'rating': None
        }
        
        response = client.get('/api/predictions/all?page=1&per_page=10')
        assert response.status_code == 200
        data = response.get_json()
        assert len(data['products']) == 1
        assert data['products'][0]['name'] == 'Test Product'

def test_grouped_products(client):
    # Setup test data
    retailer = Retailer(name='Test Retailer', base_url='http://test.com')
    product1 = Product(
        name='Test Banana Product',
        current_price=0.99,
        product_url='http://test.com/1',
        retailer=retailer
    )
    product2 = Product(
        name='Test Onion Product',
        current_price=1.99,
        product_url='http://test.com/2',
        retailer=retailer
    )
    db.session.add_all([retailer, product1, product2])
    db.session.commit()
    
    response = client.get('/api/products/grouped')
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert any(group['keyword'] == 'banana' for group in data)
    assert any(group['keyword'] == 'onion' for group in data)