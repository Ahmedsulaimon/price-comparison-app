from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import UUID, func, text
from app.extensions import db
import uuid
from sqlalchemy.dialects.postgresql import UUID

class Retailer(db.Model):
    __tablename__ = 'retailers'
    retailer_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    base_url = db.Column(db.String(255), nullable=False)
    provides_rating = db.Column(db.Boolean, default=False)
    products = db.relationship('Product', backref='retailer', lazy=True)

class Product(db.Model):
    __tablename__ = 'products'
    #   product_id = db.Column(UUID(as_uuid=True), primary_key=True, server_default=text('gen_random_uuid()'))
    product_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    retailer_id = db.Column(db.Integer, db.ForeignKey('retailers.retailer_id'))
    external_id = db.Column(db.String(255))
    name = db.Column(db.String(255), nullable=False)
    current_price = db.Column(db.Numeric(10,2), nullable=False)
    category = db.Column(db.String(100))
    brand = db.Column(db.String(100))
    size_description = db.Column(db.String(100))
    base_quantity = db.Column(db.Numeric(10,2))
    base_unit = db.Column(db.String(20))
    image_url = db.Column(db.String(255))
    product_url = db.Column(db.String(255), nullable=False)
    rating = db.Column(db.Numeric(3,2))  
    badges = db.Column(db.JSON)
    currency = db.Column(db.String(3), default='GBP')
    price_history = db.relationship('PriceHistory', backref='product', lazy='dynamic')

class PriceHistory(db.Model):
    __tablename__ = 'price_history'

    entry_id = db.Column(UUID(as_uuid=True), primary_key=True,  default=uuid.uuid4)
    product_id = db.Column(UUID(as_uuid=True), db.ForeignKey('products.product_id'), nullable=False)
    price = db.Column(db.Numeric(10,2), nullable=False)
    unit_price = db.Column(db.Numeric(10,2))
    is_offer = db.Column(db.Boolean, default=False)
    offer_description = db.Column(db.String(255))
    valid_from = db.Column(db.DateTime(timezone=True), nullable=False)
    valid_to = db.Column(db.DateTime(timezone=True))
    scraped_at = db.Column(db.DateTime(timezone=True), server_default=func.now())