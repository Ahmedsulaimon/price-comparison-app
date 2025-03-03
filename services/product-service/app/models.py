
from datetime import datetime


from app import db
#Define database schema using SQLAlchemy ORM
class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    price = db.Column(db.Float, nullable=False)
    store = db.Column(db.String(80), nullable=False)
    historical_prices = db.relationship('PriceHistory', backref='product', lazy=True)

class PriceHistory(db.Model):
    __tablename__ = 'price_history'
    
    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    product_id =db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)