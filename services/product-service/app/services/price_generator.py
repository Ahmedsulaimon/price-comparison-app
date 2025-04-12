# app/services/price_generator.py
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from flask import current_app
from sqlalchemy import func
from app.extensions import db
from app.models import Product, PriceHistory

class PriceGenerator:
    @staticmethod
    def generate_price_history(product, days=365, fluctuation=0.2):
        """Generate synthetic price history maintaining unit price ratios"""
        try:
            # Get most recent valid unit price from history
            latest_history = db.session.query(PriceHistory)\
                .filter_by(product_id=product.product_id)\
                .order_by(PriceHistory.scraped_at.desc())\
                .first()
            
            if not latest_history or latest_history.unit_price is None:
                current_app.logger.warning(f"No unit price available for {product.product_id}, skipping")
                return
                
            base_price = float(latest_history.price)
            base_unit_price = float(latest_history.unit_price)
            unit_price_ratio = base_unit_price / base_price
            
            # Generate date range
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            dates = pd.date_range(start_date, end_date, freq='D')
            
            # Generate price components
            seasonal = np.sin(np.linspace(0, 4 * np.pi, days)) * 0.1
            trend = np.linspace(0, 0.05, days)
            noise = np.random.normal(0, 0.02, days)
            sale_effect = PriceGenerator._generate_sale_effect(days)
            
            # Generate prices maintaining unit price ratio
            prices = base_price * (1 + seasonal + trend + noise + sale_effect)
            unit_prices = prices * unit_price_ratio
            
            # Create history entries
            histories = []
            for date, price, unit_price in zip(dates, prices, unit_prices):
                histories.append(PriceHistory(
                    product_id=product.product_id,
                    price=round(float(price), 2),
                    unit_price=round(float(unit_price), 2),
                    valid_from=date,
                    scraped_at=date + timedelta(hours=12),
                    is_offer=False
                ))
            
            db.session.bulk_save_objects(histories)
            db.session.commit()
            current_app.logger.info(f"Generated {len(histories)} historical prices for {product.name}")
            
        except Exception as e:
            current_app.logger.error(f"Price generation failed: {str(e)}")
            db.session.rollback()

    @staticmethod
    def _generate_sale_effect(days):
        """Generate random sale events (same as before)"""
        sale_effect = np.zeros(days)
        for _ in range(np.random.randint(3, 6)):
            day = np.random.randint(0, days-7)
            duration = np.random.randint(3, 7)
            sale_effect[day:day+duration] = -0.15
        return sale_effect

    @staticmethod
    def generate_for_all_products(limit=100):
        """Generate history for products with existing unit prices"""
        products = db.session.query(Product)\
            .join(PriceHistory)\
            .filter(PriceHistory.unit_price.isnot(None))\
            .limit(limit)\
            .all()
            
        for product in products:
            current_app.logger.info(f"Generating history for {product.name}")
            PriceGenerator.generate_price_history(product)