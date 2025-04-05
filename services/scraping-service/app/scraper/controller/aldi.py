

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from ..extractors import ProductExtractor
import time
from tenacity import retry, stop_after_attempt, wait_fixed
from ...scraper.utils import logger

class AldiScraper:
    """Optimized Aldi scraper with accurate selectors"""
    
    base_url = "https://groceries.aldi.co.uk"
    groceries_url = f"{base_url}/en-GB/fresh-food"
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
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            # Wait for critical elements to load
            WebDriverWait(self.driver, self.timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.product-teaser-item")))
            time.sleep(1)  # Small stabilization delay
            return BeautifulSoup(self.driver.page_source, "html.parser")
        except Exception as e:
            self.logger.warning(f"Page load failed: {str(e)}")
            raise

    def get_next_page(self):
        """Handle pagination for different page structures"""
        try:
            soup = BeautifulSoup(self.driver.page_source, "html.parser")

            # Find the currently active page (e.g., <span> for page 4)
            current_page = soup.select_one("span.base-pagination__count--active")
            if not current_page:
                return False  # No more pages

            try:
                current_page_number = int(current_page["data-test"].replace("current-page", ""))
            except (KeyError, ValueError):
                return False  # If parsing fails, assume no more pages

            next_page_number = current_page_number + 1

            # Check if next page exists as an <a> tag
            next_page = soup.select_one(f'a[data-test="page-{next_page_number}"]')

            if next_page:
                next_page_url = urljoin(self.base_url, next_page["href"])
                self.driver.get(next_page_url)
                time.sleep(2)
                return True
            
            return False  # Stop if no next page link found

        except Exception as e:
            self.logger.error(f"Pagination error: {e}")
            return False

    def aldi_groceries(self) -> List[Dict[str, Any]]:
        """Scrape all Aldi groceries across multiple pages"""
        self.driver.get(self.groceries_url)
        all_products = []

        while True:
            soup = BeautifulSoup(self.driver.page_source, "html.parser")
            product_elements = soup.select("div.product-teaser-item")

            for product_element in product_elements:
                try:
                    product_link = ProductExtractor.extract_product_link(
                        product_element, self.base_url, "a.product-tile__link"
                    )
                    if product_link:
                        product = {
                            "store": "Aldi",
                            "url": product_link,
                            "name": ProductExtractor.extract_title(
                                product_element, "div.product-tile__name p"
                            ),
                            "brand": ProductExtractor.extract_manufacturer(
                                product_element, "div.product-tile__brandname p"
                            ),
                            "price": ProductExtractor.extract_price(
                                product_element, "span.base-price__regular span"
                            ),
                            "size": ProductExtractor.extract_size(
                                product_element, "div.product-tile__unit-of-measurement p"
                            ),
                            "image_url": ProductExtractor.extract_image_url(
                                product_element, "img.base-image"
                            ),
                            "provide_rating": False,
                            "external_id": ProductExtractor.extract_external_id(product_link),
                            "timestamp": datetime.now().isoformat()
                        }
                        all_products.append({k: v for k, v in product.items() if v is not None})

                except Exception as e:
                    logger.error(f"Error extracting product: {e}")

            if not self.get_next_page():
                break  # Stop if no next page

        return all_products

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