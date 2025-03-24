import os
import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Any, Optional
from datetime import datetime
from ..base import BaseScraper
from ..extractors import ProductExtractor
from ..utils import logger

class AldiScraper:
    """Scraper for Aldi grocery products."""
    
    def __init__(self):   
        self.api_key = os.getenv("SCRAPER_API_KEY", "3d524fc75c4b6df70067d105b91be08c")
        self.base_url = "https://groceries.aldi.co.uk"
        self.groceries_url =  f"{self.base_url}/en-GB/fresh-food"


    def fetch_page(self, url: str) -> BeautifulSoup:
        """Fetches the page using ScraperAPI and returns parsed HTML."""
        try:
            params = {
                "api_key": self.api_key,
                "url": url,
                "country_code": "uk",
                "device_type": "desktop",
                'output_format': 'json', 
                'autoparse': 'true'
            }
            response = requests.get("https://api.scraperapi.com", params=params)

            if response.status_code == 200:
                return BeautifulSoup(response.text, "html.parser")
            else:
                logger.error(f"ScraperAPI failed: {response.status_code} {response.text}")
                return None

        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
            return None
    
    
    def scrape_product(self, url: str) -> Dict[str, Any]:
        """Scrape product details from a Aldi product page."""
        soup = self.fetch_page(url)
        if not soup:
            return {
                "store": "Aldi",
                "url": url,
                "error": "Failed to fetch page",
                "timestamp": datetime.now().isoformat()
            }
        
        try:
        
            product = {
                "store": "Aldi",
                "url": url,
                "timestamp": datetime.now().isoformat(),
                "name": ProductExtractor.extract_title(
                    soup, "h1"
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
                    soup, 'div.styled__StyledNonInteractiveContainer-sc-1de15j6-7 klymXO ddsweb-rating__container'
                ),
                "manufacturer": ProductExtractor.extract_manufacturer(
                    soup, 'p.text__StyledText-sc-1jpzi8m-0 eWKcpa ddsweb-text styled__StyledFootnote-sc-6tl8kn-3 cOHloe'
                ),
                "description": ProductExtractor.extract_description(
                    soup, 'span.styled__Block-mfe-pdp__sc-1od89q4-1 bICtby'
                ),
                "currency": "GBP"
            }
            
            return {k: v for k, v in product.items() if v is not None}
            
        except Exception as e:
            logger.error(f"Error scraping product {url}: {e}")
            return {
                "store": "Aldi",
                "url": url,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
        

    def aldi_groceries(self) -> List[Dict[str, Any]]:
        """Browse the Aldi groceries for featured products."""
        soup = self.fetch_page(self.groceries_url)
        if not soup:
            return []
            
        products = []
    
        # Aldi's product container
        product_elements = soup.select("div[data-qa='search-result']")

        for product_element in product_elements[:40]:  # Limit to first 40
            try:
                product_link = ProductExtractor.extract_product_link(
                    product_element, 
                    self.base_url, 
                    "a.p.text-default-font"  
                )
                
                if product_link:
                    # Extract product data
                    product = {
                        "store": "Aldi",
                        "url": product_link,
                        "name": ProductExtractor.extract_title(
                            product_element, "a.p.text-default-font"  
                        ),
                        "price": ProductExtractor.extract_price(
                            product_element, "div.product-tile-price span.h4 span"  
                        ),
                        "size": ProductExtractor.extract_size(
                            product_element, "div.text-center.p-3 div.text-gray-small"  
                        ),
                        "image_url": ProductExtractor.extract_image_url(
                            product_element, "div.image-tile img.product-image" 
                        ),
                        "shipping": ProductExtractor.extract_shipping_cost(
                            product_element, "div.drs-fee.text-center span"  
                        ),
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    # Remove None values
                    products.append({k: v for k, v in product.items() if v is not None})
                    
            except Exception as e:
                logger.error(f"Error extracting featured groceries: {e}")
                
        return products

    
