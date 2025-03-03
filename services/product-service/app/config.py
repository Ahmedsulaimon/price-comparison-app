import os
#Centralize all service settings
class Config:
    # Load from environment variables with fallback values
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL','postgresql://postgres:password@database:5432/product_db') 
    SQLALCHEMY_TRACK_MODIFICATIONS = False
   
    #API routing
    API_PREFIX = '/api/v1'
    #connection pooling
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,  # Helps with connection recycling
        'pool_recycle': 3600    # Recycle connections every hour
    }