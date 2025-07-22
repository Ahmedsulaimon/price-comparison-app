from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List
from selenium import webdriver
from ...scraper.models import (
    ProductRequest, SearchRequest, ProductResponse, 
    BulkScrapeRequest, ErrorResponse, HealthResponse
)
from ...scraper.factory import ScraperFactory
from ...scraper.utils import logger
from app.scraper.controller.aldi import AldiScraper


router = APIRouter(tags=["Scraping"])



# Tesco fresh groceries browse endpoint
@router.get("/browse/aldi/freshgroceries", response_model=List[ProductResponse], tags=["Browsing"])
async def browse_aldi_groceries():
    """Browse Aldi groceries for featured products using Selenium."""
    
    scraper = AldiScraper()
    
    try:
        products = scraper.aldi_groceries()
        if not products:
            raise HTTPException(status_code=404, detail="No products found.")
        return products

    except Exception as e:
        if hasattr(scraper, 'close'):
            scraper.close()
        logger.error(f"Error browsing Aldi fresh groceries: {e}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

    finally:
        scraper.close()  # Ensure Selenium WebDriver is properly closed
