import os
from time import sleep
from sqlalchemy import exc
from app import create_app
from app.extensions import db
from app.config import Config
from app.services.data_processing import PriceService


def initialize_database(app):
    """Handle database initialization with retries"""
    with app.app_context():
        retries = 5
        while retries > 0:
            try:
                db.create_all()
                # from app.database.db_setup import initialize_retailers
                # initialize_retailers(db)
                print("Database initialized successfully")
                return True
            except exc.OperationalError:
                retries -= 1
                sleep(5)
                if retries == 0:
                    app.logger.error("Database connection failed after 5 attempts")
                    raise

if __name__ == '__main__':
    app = create_app(Config)
    
    # Initialize database
    initialize_database(app)
    
    # Start services
    price_service = PriceService(db)
    price_service.start_scheduler(app)
    
    app.run(
        host=os.getenv('HOST', '0.0.0.0'),
        port=int(os.getenv('PORT', 5000)),
        debug=os.getenv('DEBUG', False)
    )