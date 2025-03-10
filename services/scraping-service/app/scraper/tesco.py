from bs4 import BeautifulSoup
from typing import Dict, List, Any, Optional
from datetime import datetime
from .base import BaseScraper
from .extractors import ProductExtractor
from .utils import logger

class TescoScraper(BaseScraper):
    """Scraper for Tesco grocery products."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.base_url = "https://www.tesco.com"
        self.search_url = f"{self.base_url}/groceries/en-GB/search"
        self.marketplace_url = f"{self.base_url}/groceries/en-GB/shop/marketplace/all"
    
    def scrape_product(self, url: str) -> Dict[str, Any]:
        """Scrape product details from a Tesco product page."""
        soup = self.fetch_page(url)
        if not soup:
            return {
                "store": "Tesco",
                "url": url,
                "error": "Failed to fetch page",
                "timestamp": datetime.now().isoformat()
            }
        
        try:
            # These selectors need to be updated based on Tesco's actual HTML structure
            product = {
                "store": "Tesco",
                "url": url,
                "timestamp": datetime.now().isoformat(),
                "name": ProductExtractor.extract_title(
                    soup, 'span.styled__Text-sc-1i711qa-1 bsLJsh ddsweb-link__text'
                ),
                "price": ProductExtractor.extract_price(
                    soup, 'p.text__StyledText-sc-1jpzi8m-0 gyHOWz ddsweb-text styled__PriceText-sc-v0qv7n-1 cXlRF'
                ),
                "image_url": ProductExtractor.extract_image_url(
                    soup, 'img.styled__StyledImage-sc-1fweb41-1 hCXoFX'
                ),
                "shipping": ProductExtractor.extract_shipping_cost(
                    soup, 'p.text__StyledText-sc-1jpzi8m-0 eWKcpa ddsweb-text'
                ),
                "rating": ProductExtractor.extract_rating(
                    soup, 'span.star-rating__score'
                ),
                "manufacturer": ProductExtractor.extract_manufacturer(
                    soup, 'p.span.styled__Name-sc-6tl8kn-0.iWxIC'
                ),
                "description": ProductExtractor.extract_description(
                    soup, '.product-description'
                ),
                "currency": "GBP"
            }
            
            return {k: v for k, v in product.items() if v is not None}
            
        except Exception as e:
            logger.error(f"Error scraping product {url}: {e}")
            return {
                "store": "Tesco",
                "url": url,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def search_products(self, query: str, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search for products on Tesco based on a query."""
        search_url = f"{self.search_url}?query={query}"
        if category:
            search_url += f"&category={category}"
            
        soup = self.fetch_page(search_url)
        if not soup:
            return []
            
        products = []
        # Find product links on the search results page
        # Update this selector based on Tesco's actual HTML structure
        product_elements = soup.select("li.WL_DZ")
       #<p class="text__StyledText-sc-1jpzi8m-0 gyHOWz ddsweb-text styled__PriceText-sc-v0qv7n-1 cXlRF">£0.16</p>
        for product_element in product_elements[:10]:  # Limit to first 10 for testing
            try:
                product_link = ProductExtractor.extract_product_link(
                    product_element, 
                    self.base_url, 
                    "a.styled__ImageContainer-sc-1fweb41-0 irjUEM"
                )
                
                if product_link:
                    # Basic data extraction from search results
                    product = {
                        "store": "Tesco",
                        "url": product_link,
                        "name": ProductExtractor.extract_title(
                            product_element, "h3"
                        ),
                        "price": ProductExtractor.extract_price(
                            product_element, "p"
                        ),
                        "image_url": ProductExtractor.extract_image_url(
                            product_element, "img"
                        ),
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    # Remove None values
                    products.append({k: v for k, v in product.items() if v is not None})
                    
            except Exception as e:
                logger.error(f"Error extracting product from search results: {e}")
                
        return products
    
    def browse_marketplace(self) -> List[Dict[str, Any]]:
        """Browse the Tesco marketplace for featured products."""
        soup = self.fetch_page(self.marketplace_url)
        if not soup:
            return []
            
        products = []
        # Update this selector based on Tesco's actual HTML structure
       
        product_elements = soup.select("ul.YObNe")
        
        for product_element in product_elements[:200]:  # Limit to first 200
            try:
                product_link = ProductExtractor.extract_product_link(
                    product_element, 
                    self.base_url, 
                    "a.styled__ImageContainer-sc-1fweb41-0.irjUEM"
                )
                
                if product_link:
                    # Basic data extraction
                    product = {
                        "store": "Tesco",
                        "url": product_link,
                        "name": ProductExtractor.extract_title(
                            product_element, "h3.span.styled__Text-sc-1i711qa-1.bsLJsh.ddsweb-link__text"
                        ),
                        "price": ProductExtractor.extract_price(
                            product_element, "p.text__StyledText-sc-1jpzi8m-0.gyHOWz.ddsweb-text.styled__PriceText-sc-v0qv7n-1.cXlRF"
                        ),
                        "image_url": ProductExtractor.extract_image_url(
                            product_element, "img.styled__StyledImage-sc-1fweb41-1.hCXoFX"
                        ),
                        "shipping": ProductExtractor.extract_shipping_cost(
                            product_element, "p.text__StyledText-sc-1jpzi8m-0.eWKcpa.ddsweb-text"
                        ),
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    # Remove None values
                    products.append({k: v for k, v in product.items() if v is not None})
                    
            except Exception as e:
                logger.error(f"Error extracting product from marketplace: {e}")
                
        return products