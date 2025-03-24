import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict, Any
from ..extractors import ProductExtractor
from ..utils import logger

class IcelandScraper:
    """Scraper for Iceland's grocery products using ScraperAPI."""

    base_url = "https://www.iceland.co.uk"
    groceries_url = f"{base_url}/fresh"

    def __init__(self):
        self.api_key = os.getenv("SCRAPER_API_KEY", "3d524fc75c4b6df70067d105b91be08c")

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

    def iceland_groceries(self) -> List[Dict[str, Any]]:
        """Browse the Iceland groceries for featured products."""
        soup = self.fetch_page(self.groceries_url)
        if not soup:
            return []

        products = []
        product_elements = soup.select("div[data-test-selector='product-list-item']")

        for product_element in product_elements[:10]:  # Limit to first 10 products
            try:
                product_link = ProductExtractor.extract_product_link(
                    product_element, 
                    self.base_url, 
                    "a[data-test-selector='product-list-item-name']"
                )
                
                if product_link:
                    # Count stars for rating
                    full_stars = len(product_element.find_all("use", {"xlink:href": "#review-star-fill"}))
                    half_stars = len(product_element.find_all("use", {"xlink:href": "#review-star-half"}))
                    rating = full_stars + (0.5 * half_stars) if (full_stars > 0 or half_stars > 0) else None
                 
                    product = {
                        "store": "Iceland",
                        "url": product_link,
                        "name": ProductExtractor.extract_title(
                            product_element, "a[data-test-selector='product-list-item-name']"
                        ),
                        "price": ProductExtractor.extract_price(
                            product_element, "span._105qcvc4cu" 
                        ),                         
                        "image_url": ProductExtractor.extract_image_url(
                            product_element,  "a picture img"          
                        ),
                        "rating": rating,
                        "size": ProductExtractor.extract_size(
                            product_element, "p._105qcvc4cu:contains('per')"
                        ),
                        "timestamp": datetime.now().isoformat(),
                    }
                    
                    # Remove None values
                    products.append({k: v for k, v in product.items() if v is not None})
                    
            except Exception as e:
                logger.error(f"Error extracting Iceland groceries: {e}")
        
        return products