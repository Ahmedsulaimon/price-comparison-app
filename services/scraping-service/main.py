
import logging
import os
import subprocess
import sys
import uvicorn
from fastapi import FastAPI
from app.scraper.middleware import Middleware
from app.scraper.routes.aldi_routes import router as aldi_product_router
from app.scraper.routes.tesco_routes import router as tesco_product_router
from app.scraper.routes.iceland_routes import router as iceland_product_router
from app.scraper.routes.sainsbury_routes import router as sainsbury_product_router
from app.scraper.routes.morrison_routes import router as morrison_product_router
from selenium import webdriver

from selenium.webdriver.chrome.service import Service


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('/app/app.log')
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Scraping Service API",
    description="Service for scraping product data from UK retailers",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Apply middleware
Middleware.setup_middleware(app)

# Include routers
app.include_router(aldi_product_router)
app.include_router(tesco_product_router)
app.include_router(iceland_product_router)
app.include_router(sainsbury_product_router)
app.include_router(morrison_product_router)



def main():
    """Main entry point for the application"""
    try:
        logger.info("Starting application...")
        logger.info(f"Current working directory: {os.getcwd()}")
        logger.info(f"Python path: {sys.path}")
       
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=5001,
            reload=True
        )
    except Exception as e:
        logger.error(f"Application startup failed: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()















# from fastapi import FastAPI
# from app.scraper.middleware import Middleware
# from app.scraper.routes.aldi_routes import  router as aldi_product_router
# from app.scraper.routes.tesco_routes import  router as tesco_product_router
# from app.scraper.routes.iceland_routes import  router as iceland_product_router
# from app.scraper.routes.sainsbury_routes import  router as sainsbury_product_router

# app = FastAPI(
#     title="Scraping Service API",
#     description="Service for scraping product data from UK retailers",
#     version="1.0.0",
#     docs_url="/docs",
#     redoc_url="/redoc"
# )

# # Apply middleware
# Middleware.setup_middleware(app)

# # Include routers
# app.include_router(aldi_product_router)
# app.include_router(tesco_product_router)
# app.include_router(iceland_product_router)
# app.include_router(sainsbury_product_router)

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(
#          "main:app",
#          host="0.0.0.0",
#          port=5001,
#          reload=True 
#          #if os.environ.get("ENVIRONMENT") == "development" else False
#      )









