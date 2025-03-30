import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException
from ..extractors import ProductExtractor
import time
from tenacity import retry, stop_after_attempt, wait_fixed
from ...scraper.utils import logger

class IcelandScraper:
    """Scraper for Iceland's grocery products """

    base_url = "https://www.iceland.co.uk"
    groceries_url = f"{base_url}/fresh"
    timeout = 30  
    def __init__(self, headless=True):
            self.logger = logging.getLogger(__name__)
            self.driver = self._init_firefox(headless)
            
    def _init_firefox(self, headless):
        """Initialize Firefox with optimized settings"""
        options = FirefoxOptions()
        if headless:
            options.add_argument("--headless")
        
        # Essential Firefox preferences
        options.set_preference("dom.webdriver.enabled", False)
        options.set_preference("useAutomationExtension", False)
        options.set_preference("permissions.default.image", 2)  # Disable images
        options.set_preference("general.useragent.override", 
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        
        service = Service(executable_path='/usr/local/bin/geckodriver')
        try:
            driver = webdriver.Firefox(service=service, options=options)
            driver.set_page_load_timeout(self.timeout)
            return driver
        except WebDriverException as e:
            self.logger.error(f"Firefox initialization failed: {str(e)}")
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(3))
    def fetch_page(self, url):
        """Reliable page fetching with proper waiting"""
        try:
            self.driver.get(url)
             # Scroll to load lazy-loaded images
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            # Wait for critical elements to load
            WebDriverWait(self.driver, self.timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-test-selector='product-list-item']")))
            time.sleep(1)  # Small stabilization delay
            return BeautifulSoup(self.driver.page_source, "html.parser")
        except Exception as e:
            self.logger.warning(f"Page load failed: {str(e)}")
            raise
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
                    rating = 0.0
                    star_elements = product_element.select('svg[viewBox="0 0 24 24"] use')
                    
                    for star in star_elements:
                        if '#review-star-fill' in star.get('xlink:href', ''):
                            rating += 1.0
                        elif '#review-star-half' in star.get('xlink:href', ''):
                            rating += 0.5

                    product = {
                        "store": "Iceland",
                        "url": product_link,
                        "name": ProductExtractor.extract_title(
                            product_element, "a[data-test-selector='product-list-item-name']"
                        ),
                        "price": ProductExtractor.extract_price(
                            product_element, "span._105qcvc4il" 
                        ),                         
                        "image_url": ProductExtractor.extract_image_url(
                            product_element,  "picture img"          
                        ),
                        "rating": rating,
                        "unit_price": ProductExtractor.extract_discounted_price(
                            product_element,
                           "p._105qcvc4mg"
                        ),
                        "size": ProductExtractor.extract_iceland_size(
                            product_element,  "a[data-test-selector='product-list-item-name']"
                        ),
                        "timestamp": datetime.now().isoformat(),
                    }
                    
                    # Remove None values
                    products.append({k: v for k, v in product.items() if v is not None})
                    
            except Exception as e:
                logger.error(f"Error extracting Iceland groceries: {e}")
        
        return products
    
    def close(self):
        """Ensure proper resource cleanup"""
        if hasattr(self, 'driver'):
            try:
                self.driver.quit()
            except Exception as e:
                self.logger.error(f"Error closing driver: {str(e)}")

    def __enter__(self):
        """Support context manager protocol"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Ensure resources are cleaned up"""
        self.close()