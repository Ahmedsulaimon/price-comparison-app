from fastapi import APIRouter, HTTPException, BackgroundTasks, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import logging
from ...scraper.models import (
    ProductRequest, SearchRequest, ProductResponse, 
    BulkScrapeRequest, ErrorResponse, HealthResponse
)
from ...scraper.factory import ScraperFactory
from ...scraper.utils import logger
from app.scraper.controller.tesco import TescoScraper


router = APIRouter(tags=["Scraping"])

# Health check endpoint
@router.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    """Health check endpoint."""
    return HealthResponse()


# List available stores endpoint
@router.get("/stores", tags=["System"])
async def list_available_stores():
    """List all available stores that can be scraped."""
    try:
        available_stores = ScraperFactory.get_available_stores()
        return {"stores": available_stores}
    except Exception as e:
        logger.error(f"Error listing stores: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error: {str(e)}"
        )


    
# Tesco fresh groceries browse endpoint
@router.get("/browse/tesco/freshgroceries", response_model=List[ProductResponse], tags=["Browsing"])
async def browse_tesco_groceries():
    """Browse Tesco groceries for featured products."""
    scraper = TescoScraper()
    try:
      
       products = scraper.tesco_groceries()
       if not products:
            raise HTTPException(status_code=404, detail="No products found.")
       return products

    except Exception as e:
        if hasattr(scraper, 'close'):
            scraper.close()
        logger.error(f"Error browsing Tesco fresh groceries: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error: {str(e)}"
        )    
    finally:
        scraper.close()  # Ensure Selenium WebDriver is properly closed

# # Tesco fresh groceries browse endpoint
# @router.get("/browse/tesco/freshgroceries", response_model=List[ProductResponse], tags=["Browsing"])
# async def browse_tesco_groceries():
#     """Browse Tesco groceries for featured products."""
#     try:
#         scraper = ScraperFactory.get_scraper("tesco")
#         # We need to cast the scraper to TescoScraper to access the browse_groceries method
#         from ...scraper.controller.tesco import TescoScraper
#         if isinstance(scraper, TescoScraper):
#             products = scraper.tesco_groceries()
#             return products
#         else:
#             raise HTTPException(
#                 status_code=500,
#                 detail="Failed to initialize Tesco scraper correctly"
#             )
#     except Exception as e:
#         logger.error(f"Error browsing Tesco fresh groceries: {e}")
#         raise HTTPException(
#             status_code=500,
#             detail=f"Unexpected error: {str(e)}"
#         )    