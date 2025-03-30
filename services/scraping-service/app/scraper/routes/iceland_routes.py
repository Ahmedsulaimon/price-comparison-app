from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List
from ...scraper.models import (
    ProductRequest, SearchRequest, ProductResponse, 
    BulkScrapeRequest, ErrorResponse, HealthResponse
)
from ...scraper.factory import ScraperFactory
from ...scraper.utils import logger
from app.scraper.controller.iceland import IcelandScraper


router = APIRouter(tags=["Scraping"])



# Health check endpoint
@router.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    """Health check endpoint."""
    return HealthResponse()

# Product scraping endpoint
@router.post("/scrape/product", response_model=ProductResponse, responses={404: {"model": ErrorResponse}}, tags=["Scraping"])
async def scrape_product(request: ProductRequest):
    """Scrape a single product by URL."""
    try:
        scraper = ScraperFactory.get_scraper(request.store)
        product_data = scraper.scrape_product(str(request.url))
        
        if "error" in product_data:
            raise HTTPException(
                status_code=404,
                detail=f"Failed to scrape product: {product_data['error']}"
            )
            
        return product_data
    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error scraping product: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error: {str(e)}"
        )


    
# Iceland fresh groceries browse endpoint
@router.get("/browse/iceland/freshgroceries", response_model=List[ProductResponse], tags=["Browsing"])
async def browse_iceland_groceries():
    """Browse Iceland groceries for featured products"""
    scraper = IcelandScraper()

    try:
        
        products = scraper.iceland_groceries()
        if not products:
            raise HTTPException(status_code=404, detail="No products found.")
        return products

    except Exception as e:
        if hasattr(scraper, 'close'):
            scraper.close()
        logger.error(f"Error browsing Iceland fresh groceries: {e}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
    finally:
        scraper.close()