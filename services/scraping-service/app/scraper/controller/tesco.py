
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


class TescoScraper:
    """Scraper for Tesco grocery products."""
    base_url = "https://www.tesco.com"
    groceries_url =  f"{base_url}/groceries/en-GB/shop/fresh-food/all"
    timeout = 45  # Optimal timeout balance
    
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
        options.set_preference("dom.disable_beforeunload", True)
        options.set_preference("browser.tabs.remote.autostart", False)
        options.set_preference("network.http.connection-timeout", 30)
        options.set_preference("general.useragent.override", 
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36")
        
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

            # More robust waiting strategy
            self.driver.implicitly_wait(10)

            for i in range(1, 4):
                self.driver.execute_script(f"window.scrollTo(0, document.body.scrollHeight * {i/4});")
                time.sleep(1.5)  # Slightly longer stabilization delay

            time.sleep(2)
            
            # Wait for critical elements to load
            WebDriverWait(self.driver, self.timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "li[data-testid]")))
            time.sleep(1)  # Small stabilization delay
            return BeautifulSoup(self.driver.page_source, "html.parser")
        except Exception as e:
            self.logger.warning(f"Page load failed: {str(e)}")
            raise



    def tesco_groceries(self) -> List[Dict[str, Any]]:
        """Browse Tesco groceries with accurate selectors and data extraction."""
        soup = self.fetch_page(self.groceries_url)
        if not soup:
            return []

        products = []
        product_elements = soup.select("li[data-testid]")  # This matches the HTML structure better

        for product_element in product_elements[:20]:  # Limit to first 20
            try:
                # First check if it's a product element (some li with data-testid might not be products)
                if not product_element.select_one("a[href^='/groceries/en-GB/products/']"):
                    continue
                    
                product_link = product_element.select_one("a[href^='/groceries/en-GB/products/']")
                full_url = self.base_url + product_link.get("href") if product_link else None
                
                # Get title using improved selector
                title = extract_title(product_element, "h3 a[aria-label]")
                
                # More specific price selectors
                regular_price = product_element.select_one("p.styled__PriceText-sc-v0qv7n-1")
                regular_price_text = regular_price.get_text().strip() if regular_price else None
                
                clubcard_price = product_element.select_one("p.styled__ContentText-sc-1d7lp92-9")
                clubcard_price_text = clubcard_price.get_text().strip() if clubcard_price else None
                
                # Extract image URL 
                img_element = product_element.select_one("img.styled__StyledImage-sc-1fweb41-1")
                img_url = img_element.get("src") if img_element else None
                
                if full_url:
                    product = {
                        "store": "Tesco",
                        "url": full_url,
                        "name": title,
                        "discount_price": clubcard_price_text,
                        "price": regular_price_text,
                        "image_url": img_url,
                        "timestamp": datetime.now().isoformat()
                    }
                    # Remove None values
                    products.append({k: v for k, v in product.items() if v is not None})

            except Exception as e:
                logger.error(f"Error extracting Tesco product: {e}", exc_info=True)

        def extract_title(element, selector="h3 a span"):
            """Extract product title using the provided selector."""
            try:
                title_tag = element.select_one(selector)
                if title_tag and title_tag.get('aria-label'):
                    return title_tag.get('aria-label').strip()
                elif title_tag and title_tag.get_text():
                    return title_tag.get_text().strip()
                return None
            except Exception as e:
                logger.error(f"Error extracting title: {e}")
                return None        

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



# from bs4 import BeautifulSoup
# from typing import Dict, List, Any, Optional
# from datetime import datetime
# from ..base import BaseScraper
# from ..extractors import ProductExtractor
# from ..utils import logger

# class TescoScraper(BaseScraper):
#     """Scraper for Tesco grocery products."""
    
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.base_url = "https://www.tesco.com"
        
#         self.groceries_url =  f"{self.base_url}/groceries/en-GB/shop/fresh-food/all"

#         self.session.cookies.update({'disable-banners': 'true'})

#     def _is_blocked(self, soup: BeautifulSoup) -> bool:
#         """Check if we're being blocked"""
#         return bool(soup.select_one('div.error-page'))

#     def tesco_groceries(self) -> List[Dict[str, Any]]:
#         """Browse the Tesco groceries for featured products."""
#         soup = self.fetch_page(self.groceries_url)

#         if not soup or self._is_blocked(soup):
#             logger.error("Blocked by Tesco or empty response")
#             return []
            
#         products = []
       
       
#         product_elements = soup.select("li.WL_DZ")

#         if not product_elements:
#             logger.warning("No products found - page structure may have changed")
#             return []
        
#         for product_element in product_elements[:20]:  # Limit to first 20
#             try:
#                 product_link = ProductExtractor.extract_product_link(
#                     product_element, 
#                     self.base_url, 
#                     "a.styled__ImageContainer-sc-1fweb41-0.irjUEM"
#                 )
#                 #<p title="£1.40 Clubcard Price" class="text__StyledText-sc-1jpzi8m-0 gljcji ddsweb-text styled__ContentText-sc-1d7lp92-9 ijspZf ddsweb-value-bar__content-text">£1.40 Clubcard Price</p>
#                 if product_link:
#                     # Basic data extraction
                    
#                     product = {
#                         "store": "Tesco",
#                         "url": product_link,
#                         "name": ProductExtractor.extract_title(
#                             product_element, "h3 a span"
#                         ),
#                         "discount_price" :ProductExtractor.extract_discounted_price(
#                             product_element,  "p.styled__ContentText-sc-1d7lp92-9"  # Clubcard price
#                         ),
#                         "price": ProductExtractor.extract_price(
#                             product_element, "p.text__StyledText-sc-1jpzi8m-0.gyHOWz.ddsweb-text.styled__PriceText-sc-v0qv7n-1.cXlRF"
#                         ),
#                         "image_url": ProductExtractor.extract_image_url(
#                             product_element, "img.styled__StyledImage-sc-1fweb41-1.hCXoFX"
#                         ),
#                         "shipping": ProductExtractor.extract_shipping_cost(
#                             product_element, "p.text__StyledText-sc-1jpzi8m-0.eWKcpa.ddsweb-text"
#                         ),
#                          "unit_price": ProductExtractor.extract_discounted_price(
#                             product_element,
#                             "p.styled__Subtext-sc-v0qv7n-2"  # Price per unit
#                         ),
#                         "rating": ProductExtractor.tesco_extract_rating(
#                             product_element,
#                             "div[data-testid='star-rating']"  # Actual rating container
#                         ),
#                         "badges": ProductExtractor._extract_tesco_badges(
#                             product_element,
#                         "span.styled__StyledMarketPlaceTag-sc-1hqhl0m-1"  
#                         ),
#                         "timestamp": datetime.now().isoformat()
#                     }
                    
#                     # Remove None values
#                     products.append({k: v for k, v in product.items() if v is not None})
                    
#             except Exception as e:
#                 logger.error(f"Error extracting featured groceries: {e}")
                
#         return products