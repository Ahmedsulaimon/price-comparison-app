import logging
import re
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

class MorrisonScraper:
    """Optimized Morrisons scraper with accurate selectors"""
    
    base_url = "https://groceries.morrisons.com"
    groceries_url = f"{base_url}/categories"
    timeout = 30  # Optimal timeout balance

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
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight/3)")
            time.sleep(1)
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2)")
            time.sleep(1)
            
            # Wait for critical elements to load
            WebDriverWait(self.driver, self.timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-test^='fop-wrapper']")))
            time.sleep(1)  # Small stabilization delay
            return BeautifulSoup(self.driver.page_source, "html.parser")
        except Exception as e:
            self.logger.warning(f"Page load failed: {str(e)}")
            raise

    def morrison_groceries(self) -> List[Dict[str, Any]]:
        """Browse Morrisons groceries with updated selectors"""
        soup = self.fetch_page(self.groceries_url)
        if not soup:
            return []
            
        products = []
        
        # Updated selector for product elements
        product_elements = soup.select("div[data-test^='fop-wrapper']")
        
        for product_element in product_elements:  # Limit to first 20
            try:
                product_link = ProductExtractor.extract_product_link(
                product_element, 
                self.base_url, 
               "a[data-test='fop-product-link']"
            )
                product = {
                    "store": "Morrisons",
                    "url": product_link,
                    "name": ProductExtractor.extract_title(
                        product_element, "h3[data-test='fop-title']"
                    ),
                    "brand": "Morrisons",  # Most products are Morrisons brand
                    "price": ProductExtractor.extract_price(
                        product_element, "span[data-test='fop-price']"
                    ),
                    "discount_price": ProductExtractor.extract_discounted_price(
                        product_element, "span[data-test='fop-offer-text']"
                    ),
                    "size": ProductExtractor.extract_size(
                        product_element, "span.sc-1sjeki5-0"  # Size element
                    ),
                    "unit_price": ProductExtractor.extract_discounted_price(
                        product_element, "span[data-test='fop-price-per-unit']"
                    ),
                    "image_url": ProductExtractor.extract_image_url(
                        product_element, "img[data-test='lazy-load-image']"
                    ),
                    "rating": self._extract_morrisons_rating(
                        product_element, "div[data-test='rating-badge']"
                    ),
                     "external_id": ProductExtractor.extract_external_id(product_link),
                     "provide_rating": False,
                  
                    "timestamp": datetime.now().isoformat()
                }
                
                # Remove None values
                products.append({k: v for k, v in product.items() if v is not None})
                
            except Exception as e:
                logger.error(f"Error extracting Morrisons product: {e}")
                
        return products
    
    def _extract_morrisons_rating(self, soup_element, selector):
        """Extract Morrisons-specific rating using the provided HTML structure"""
        try:
            rating_container = soup_element.select_one(selector)
            if not rating_container:
                return None
            
            # First approach: Try to extract from aria-label using the salt-vc span
            salt_vc = rating_container.select_one("span.salt-vc")
            if salt_vc and salt_vc.text:
                rating_match = re.search(r'(\d+\.\d+) out of 5', salt_vc.text)
                if rating_match:
                    return float(rating_match.group(1))
            
            # Second approach: Count filled and half-filled stars
            filled_stars = len(rating_container.select("svg[data-test='icon__reviews']"))
            
            # Check for partial stars (half stars)
            partial_containers = rating_container.select("span[data-test='partial-rating']")
            half_stars = 0
            
            if partial_containers:
                # If there's a partial rating container, count it as 0.5
                half_stars = 0.5
            
            if filled_stars > 0 or half_stars > 0:
                # Subtract 1 from filled stars if there's a partial rating because the
                # partial container also contains a filled star in the HTML
                if half_stars > 0 and filled_stars > 0:
                    return float(filled_stars - 1 + half_stars)
                return float(filled_stars + half_stars)
            
            # Fall back to regex on the entire HTML if needed
            html_str = str(rating_container)
            rating_match = re.search(r'Rating, (\d+\.\d+) out of 5', html_str)
            if rating_match:
                return float(rating_match.group(1))
            
        except Exception as e:
            self.logger.warning(f"Error extracting rating: {e}")
        
        return None
    

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