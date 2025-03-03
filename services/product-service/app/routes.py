import os
from flask import Blueprint, jsonify, request
from app import db

import sys
sys.path.insert(0, os.getcwd()+"/")

import models
import service

product_bp = Blueprint('product', __name__)
@product_bp.route('/api/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = models.Product.query.get_or_404(product_id)
    trend = service.PriceService.get_price_trend(product_id)
    
    return jsonify({
        'id': product.id,
        'name': product.name,
        'current_price': product.price,
        'price_history': trend
    })

@product_bp.route('/api/products', methods=['POST'])
def create_product():
    data = request.get_json()
    new_product = models.Product(
        name=data['name'],
        price=data['price'],
        store=data['store']
    )
    db.session.add(new_product)
    db.session.commit()
    
    # Record initial price
    service.PriceService.add_price_history(new_product.id, data['price'])
    
    return jsonify({'message': 'Product created', 'id': new_product.id}), 201