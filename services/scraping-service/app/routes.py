from fastapi import FastAPI, HTTPException, BackgroundTasks, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import logging
from .scraper.models import (
    ProductRequest, SearchRequest, ProductResponse, 
    BulkScrapeRequest, ErrorResponse, HealthResponse
)
from .scraper.factory import ScraperFactory
from .scraper.utils import logger

app = FastAPI(
    title="Scraping Service API",
    description="Service for scraping product data from UK retailers",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
@app.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    """Health check endpoint."""
    return HealthResponse()

# Product scraping endpoint
@app.post("/scrape/product", response_model=ProductResponse, responses={404: {"model": ErrorResponse}}, tags=["Scraping"])
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
@app.post("/search", response_model=List[ProductResponse], responses={404: {"model": ErrorResponse}}, tags=["Scraping"])
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
@app.post("/scrape/bulk", status_code=202, responses={404: {"model": ErrorResponse}}, tags=["Scraping"])
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

# List available stores endpoint
@app.get("/stores", tags=["System"])
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

# Tesco marketplace browse endpoint
@app.get("/browse/tesco/marketplace", response_model=List[ProductResponse], tags=["Browsing"])
async def browse_tesco_marketplace():
    """Browse Tesco marketplace for featured products."""
    try:
        scraper = ScraperFactory.get_scraper("tesco")
        # We need to cast the scraper to TescoScraper to access the browse_marketplace method
        from .scraper.tesco import TescoScraper
        if isinstance(scraper, TescoScraper):
            products = scraper.browse_marketplace()
            return products
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to initialize Tesco scraper correctly"
            )
    except Exception as e:
        logger.error(f"Error browsing Tesco marketplace: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error: {str(e)}"
        )