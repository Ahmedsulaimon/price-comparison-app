import os
import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Any, Optional
from datetime import datetime
from ..base import BaseScraper
from ..extractors import ProductExtractor
from ..utils import logger

class SainsburyScraper:
    """Scraper for Sainsbury grocery products."""
    
    def __init__(self):      
        self.api_key = os.getenv("SCRAPER_API_KEY", "3d524fc75c4b6df70067d105b91be08c")
        self.base_url = "https://www.sainsburys.co.uk"
        self.groceries_url =  f"{self.base_url}/shop/gb/groceries/new---trending/aldi-price-match"
    
    
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
  
    

    def sainsbury_groceries(self) -> List[Dict[str, Any]]:
        """Browse the Sainsbury groceries for featured products."""
        soup = self.fetch_page(self.groceries_url)
        if not soup:
            return []

        products = []

        # Sainsbury's product container
        product_elements = soup.select("li.gridItem")

        for product_element in product_elements[:10]:  # Limit to first 40
            try:
                product_link = ProductExtractor.extract_product_link(
                    product_element, 
                    self.base_url, 
                    "h3 a"  # Extract product URL
                )

                if product_link:
                    # Extract product data
                    product = {
                        "store": "Sainsbury",
                        "url": product_link,
                        "name": ProductExtractor.extract_title(
                            product_element, "h3 a"  
                        ),
                        "price": ProductExtractor.extract_price(
                            product_element, "p.pricePerUnit"  
                        ),
                        "size": ProductExtractor.extract_size(
                            product_element, "p.pricePerMeasure"  
                        ),
                        "image_url": ProductExtractor.extract_image_url(
                            product_element, "h3 a img"  
                        ),
                        "rating": ProductExtractor.extract_rating(
                            product_element, "div.reviews img", attr="alt"  
                        ),
                       
                        "timestamp": datetime.now().isoformat()
                    }

                    # Remove None values
                    products.append({k: v for k, v in product.items() if v is not None})

            except Exception as e:
                logger.error(f"Error extracting featured groceries: {e}")

        return products
