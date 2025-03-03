
from datetime import datetime, timedelta

import os


import sys
sys.path.insert(0, os.getcwd()+"/")
from app import db
import models
# Contains business logic and data operations
class PriceService:
    @staticmethod
    def add_price_history(product_id, price):
        """Record price changes over time"""
        history = models.PriceHistory(
            product_id=product_id,
            price=price,
            timestamp=datetime.utcnow()
        )
        db.session.add(history)
        db.session.commit()

    @staticmethod
    def get_price_trend(product_id, days=30):
        """Calculate 30-day price trend"""
        cutoff = datetime.utcnow() - timedelta(days=days)
        history = models.PriceHistory.query.filter(
            models.PriceHistory.product_id == product_id,
            models.PriceHistory.timestamp >= cutoff
        ).order_by(models.PriceHistory.timestamp).all()
        
        return [{
            'price': entry.price,
            'date': entry.timestamp.isoformat()
        } for entry in history]