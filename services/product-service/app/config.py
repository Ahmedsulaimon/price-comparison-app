import os
#Centralize all service settings
class Config:
    """config file"""
    # Load from environment variables with fallback values
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL','postgresql://postgres:password@database:5432/product_db') 
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SYNC_INTERVAL = 3600  # Sync every hour
    SCRAPER_SERVICE_URL = 'http://scraping-service:5001'
    RETAILERS = {
        'sainsbury': 'http://localhost:5001/browse/sainsbury/freshgroceries',
        'aldi': 'http://localhost:5001/browse/aldi/freshgroceries',
        'morrison': 'http://localhost:5001/browse/morrison/freshgroceries',
        'iceland': 'http://localhost:5001/browse/iceland/freshgroceries'
    }
    #API routing
    API_PREFIX = '/api/v1'
    #connection pooling
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,  # Helps with connection recycling
        'pool_recycle': 3600    # Recycle connections every hour
    }