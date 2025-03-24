from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List
from ...scraper.models import (
    ProductRequest, SearchRequest, ProductResponse, 
    BulkScrapeRequest, ErrorResponse, HealthResponse
)
from ...scraper.factory import ScraperFactory
from ...scraper.utils import logger
from app.scraper.controller.aldi import AldiScraper


router = APIRouter(tags=["Scraping"])


# Background task for bulk scraping
async def scrape_products_background(urls: List[str], store: str):
    """Background task to scrape multiple products."""
    try:
        scraper = ScraperFactory.get_scraper(store)
        for url in urls:
            try:
                product_data = scraper.scrape_product(url)
                # Here you would typically save to database
                logger.info(f"Scraped: {product_data.get('name', 'Unknown product')}")
            except Exception as e:
                logger.error(f"Error scraping {url}: {e}")
    except Exception as e:
        logger.error(f"Error in background scraping task: {e}")

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

# Product search endpoint
@router.post("/search", response_model=List[ProductResponse], responses={404: {"model": ErrorResponse}}, tags=["Scraping"])
async def search_products(request: SearchRequest):
    """Search for products based on query and store."""
    try:
        scraper = ScraperFactory.get_scraper(request.store)
        products = scraper.search_products(
            request.query, 
            category=request.category
        )
        
        if not products:
            return []
            
        return products
    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error searching products: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error: {str(e)}"
        )

# Bulk scraping endpoint
@router.post("/scrape/bulk", status_code=202, responses={404: {"model": ErrorResponse}}, tags=["Scraping"])
async def bulk_scrape(request: BulkScrapeRequest, background_tasks: BackgroundTasks):
    """Start a background task to scrape multiple products."""
    try:
        # Validate store before starting the task
        ScraperFactory.get_scraper(request.store)
        
        background_tasks.add_task(scrape_products_background, request.urls, request.store)
        return {"status": "Scraping task started", "urls_count": len(request.urls)}
    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error initiating bulk scrape: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error: {str(e)}"
        )


    
# Tesco fresh groceries browse endpoint
@router.get("/browse/aldi/freshgroceries", response_model=List[ProductResponse], tags=["Browsing"])
async def browse_aldi_groceries():
    """Browse aldi groceries for featured products."""
    try:
        scraper = AldiScraper
        products = scraper.aldi_groceries()
        if not products:
            raise HTTPException(status_code=404, detail="No products found.")
        return products

    except Exception as e:
        logger.error(f"Error browsing aldi fresh groceries: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error: {str(e)}"
        )    