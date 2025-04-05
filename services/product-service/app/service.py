from datetime import datetime, timedelta
import re
from sqlalchemy import func
import requests
from apscheduler.schedulers.background import BackgroundScheduler
from flask import current_app

from app.extensions import db

class PriceService:
    def __init__(self, db):
        self.db = db
        self.scheduler = BackgroundScheduler()

    @staticmethod
    def normalize_size(size_str):
        units_mapping = {
            'g': 'grams', 'gram': 'grams', 'kg': 'kilograms',
            'l': 'liters', 'ml': 'milliliters',
            'ea': 'units', 'pack': 'units'
        }
        
        match = re.match(r"([\d\.]+)\s*(\D+)", size_str or '')
        if match:
            quantity, unit = match.groups()
            return {
                'base_quantity': float(quantity),
                'base_unit': units_mapping.get(unit.lower().strip(), 'units')
            }
        return {'base_quantity': None, 'base_unit': None}
    
  

    @staticmethod
    def normalize_unit_price(unit_str):
        if not unit_str:
            return None, None

        try:
            clean_str = ' '.join(str(unit_str).strip().lower().split())

            # Each tuple contains (regex pattern, is_pence)
            patterns = [
                (r'£([\d.]+)\s*per\s*([\w/]+)', False),  # £1.45 per 1L
                (r'([\d.]+)p\s*per\s*([\w/]+)', True),   # 20p per 100ml
                (r'£([\d.]+)\s*/\s*([\w/]+)', False),    # £0.20/100ml
                (r'([\d.]+)\s*p\s*/\s*([\w/]+)', True),  # 20 p / 100ml
                (r'([\d.]+)\s*per\s*([\w/]+)', False),   # 1.45 per litre (assume pounds unless marked p)
            ]

            for pattern, is_pence in patterns:
                match = re.search(pattern, clean_str)
                if match:
                    price = float(match.group(1))
                    unit = match.group(2).lower()

                    if is_pence:
                        price = price / 100
                    return price, unit

        except (ValueError, AttributeError, TypeError) as e:
            # Use logging if this isn't inside Flask
             current_app.logger.error(f"Failed to parse unit price '{unit_str}': {str(e)}")

        return None, None

    @staticmethod
    def process_scraped_product(data, retailer_name):  
        from app.models import Retailer, Product, PriceHistory  

        if 'name' not in data or not data['name']:
            raise ValueError("Product name is required")
        
        # Get or create retailer
        retailer = db.session.query(Retailer).filter_by(name=retailer_name).first()
        if not retailer:
            retailer = Retailer(name=retailer_name, base_url=data.get('base_url', ''))
            db.session.add(retailer)
            db.session.commit()
        
        # Create/update product
        product = db.session.query(Product).filter_by(
            retailer_id=retailer.retailer_id,
            product_url=data['url']
        ).first()

        size_info = PriceService.normalize_size(data.get('size'))
        unit_price, _ = PriceService.normalize_unit_price(data.get('unit_price'))

        if not product:
            product = Product(
                retailer_id=retailer.retailer_id,
                external_id=data['external_id'],
                product_url=data['url'],
                name=data['name'],
                current_price=data['price'],
                currency=data.get('currency', 'GBP'),
                image_url=data.get('image_url'),
                brand=data.get('brand'),
                size_description=data.get('size'),
                base_quantity=size_info['base_quantity'],
                base_unit=size_info['base_unit'],
                rating=data.get('rating'),
                badges=data.get('badges'),
                category=PriceService.detect_category(data['name'])
            )
            db.session.add(product)
        else:
            product.current_price = data['price']
            product.base_quantity = size_info['base_quantity']
            product.base_unit = size_info['base_unit']
        
        db.session.commit()

        # Record price history if changed
        if not product.price_history or product.current_price != data['price']:
            PriceService.add_price_history(product.product_id, data, unit_price)

        return product

    @staticmethod
    def add_price_history(product_id, data, unit_price=None):
        from app.models import PriceHistory
        from datetime import datetime, timedelta
        
        if unit_price is None:
            unit_price, _ = PriceService.normalize_unit_price(data.get('unit_price'))
        
        history = PriceHistory(
            product_id=product_id,
            price=data['price'],
            unit_price=unit_price,
            is_offer=bool(data.get('discount_price')),
            offer_description=data.get('discount_price'),
            valid_from=datetime.utcnow(),
            valid_to=None, 
        )
        db.session.add(history)
        db.session.commit()

    @staticmethod
    def detect_category(product_name):
        categories = {
            'fruit': {'apple', 'banana', 'berry', 'orange', 'grape'},
            'vegetable': {'carrot', 'potato', 'tomato', 'lettuce', 'onion'},
            'dairy': {'milk', 'cheese', 'yogurt', 'butter', 'cream'},
            'bakery': {'bread', 'crumpet', 'roll', 'cake', 'pastry'},
            'poultry': {'meat', 'beef', 'chicken', 'pork', 'sausage', 'bacon'}
        }
        lower_name = product_name.lower()
        for cat, keywords in categories.items():
            if any(kw in lower_name for kw in keywords):
                return cat
        return 'others'

    def start_scheduler(self, app):
        def sync_job():
            with app.app_context():
                self.regular_sync()

        self.scheduler.add_job(
            func=sync_job,
            trigger='interval',
            seconds=app.config['SYNC_INTERVAL']
        )
        self.scheduler.start()

    def regular_sync(self):
        retailers = current_app.config['RETAILERS']
        for retailer_name, url in retailers.items():
            try:
                response = requests.get(url)
                response.raise_for_status()
                for product_data in response.json():
                  
                    PriceService.process_scraped_product(product_data, retailer_name)
            except Exception as e:
                current_app.logger.error(f"Sync failed for {retailer_name}: {str(e)}")