from pydantic import BaseModel, HttpUrl, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class ProductRequest(BaseModel):
    """Request model for product scraping."""
    url: HttpUrl
    store: str

class SearchRequest(BaseModel):
    """Request model for product search."""
    query: str
    store: str
    category: Optional[str] = None

class ProductResponse(BaseModel):
    """Response model for product data."""
    store: str
    url: str
    name: Optional[str] = None
    discount_price: Optional[str] = None
    price: Optional[float] = None
    size:  Optional[str] = None
    image_url: Optional[str] = None
    badges: Optional[str] = None
    brand: Optional[str] = None
    unit_price: Optional[str] = None
    currency: str = "GBP"
    shipping: Optional[str] = None
    rating: Optional[float] = None
    manufacturer: Optional[str] = None
    provide_rating: Optional[bool] = None
    external_id: Optional[str] = None
    description: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    
    class Config:
        json_schema_extra = {
            "example": {
                "store": "Tesco",
                "url": "https://www.tesco.com/groceries/en-GB/products/123456789",
                "name": "Organic Bananas 5 Pack",
                "discount": "1.20 clubcard",
                "badges": "https://example.com/image.jpg",
                "brand": "......",
                "unit_price": 1.49,
                "price": 1.49,
                "size": "500g",
                "image_url": "https://example.com/image.jpg",
                "currency": "GBP",
                "shipping": "Free delivery",
                "rating": 4.5,
                "provide_rating": True,
                "external_id": "34566543",
                "manufacturer": "Tesco",
                "description": "Organic bananas, perfect for a healthy snack.",
                "timestamp": "2023-09-08T12:34:56.789Z"
            }
        }

class BulkScrapeRequest(BaseModel):
    """Request model for bulk scraping."""
    urls: List[str]
    store: str

class ErrorResponse(BaseModel):
    """Response model for errors."""
    error: str
    detail: Optional[str] = None
    
    class Config:
        schema_extra = {
            "example": {
                "error": "Store not found",
                "detail": "The requested store 'unknown' is not available."
            }
        }

class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str = "ok"
    version: str = "1.0.0"
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())