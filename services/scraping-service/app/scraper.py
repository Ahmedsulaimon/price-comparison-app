import requests
from bs4 import BeautifulSoup
import time
import random
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union
import json
import os
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("scraper.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("scraper")

class RateLimiter:
#     """Handles rate limiting for scraping requests to avoid overloading servers."""
    
    def __init__(self, requests_per_minute: int = 20):
        self.requests_per_minute = requests_per_minute
        self.minimum_interval = 60.0 / requests_per_minute
        self.last_request_time = 0
    
    def wait(self):
        """Wait appropriate time to respect rate limits."""
        current_time = time.time()
        elapsed = current_time - self.last_request_time
        
        if elapsed < self.minimum_interval:
            sleep_time = self.minimum_interval - elapsed
            # Add small random jitter to avoid patterns
            sleep_time += random.uniform(0.1, 0.3)
            time.sleep(sleep_time)

        self.last_request_time = time.time()    

     
  
class WebScraper:
    def __init__(self, *args, **kwargs):
         super().__init__(*args, **kwargs)
         self.base_url = "https://www.tesco.com"
         self.marketplace_url = f"{self.base_url}/groceries/en-GB/shop/marketplace/all"

    @staticmethod
    def scrape_product_info(url):
        """
        Scrape basic product information from a provided URL
        """
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'lxml')
            
            # Example implementation - this would need to be customized for specific sites
            product_data = {
                'title': WebScraper._extract_title(soup),
                'price': WebScraper._extract_price(soup),
                'shipping': WebScraper._extract_shipping_cost(soup),
                'image_url': WebScraper._extract_image(soup),
                'rating': WebScraper._extract_rating(soup),
                'manufacturer': WebScraper._extract_manufacturer(soup),
                'description': WebScraper._extract_description(soup),
                'product_link': WebScraper._extract_product_link(soup)
            }
            
            return {
                'success': True,
                'data': product_data
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
  
    @staticmethod
    def _extract_title(soup):
        # Example implementation - adjust selectors for target sites
        title_tag =  soup.select_one('h3.span.styled__Text-sc-1i711qa-1 bsLJsh ddsweb-link__text')
        return title_tag.text.strip() if title_tag else 'Title not found'
    @staticmethod
    def _extract_product_link(soup):
        # Example implementation - adjust selectors for target sites
         product_link = soup.select_one("a.styled__ImageContainer-sc-1fweb41-0 irjUEM")
         if product_link and 'href' in product_link.attrs:
          product_url = self.ase_url + product_link['href']
       
         return product_url.text.strip() if  product_url else None
    
    @staticmethod
    def _extract_shipping_cost(soup):
        # Example implementation - adjust selectors for target sites
        shipping_tag =  soup.select_one('p.text__StyledText-sc-1jpzi8m-0 eWKcpa ddsweb-text')
        return shipping_tag.text.strip() if shipping_tag else 'shipping cost not found'
    
    @staticmethod
    def _extract_price(soup):
        # Example implementation - adjust selectors for target sites
        
        price_tag =  soup.select_one('p.text__StyledText-sc-1jpzi8m-0 gyHOWz ddsweb-text styled__PriceText-sc-v0qv7n-1 cXlRF')
        if price_tag:
            price_text = price_tag.text.strip()
            # Remove currency symbols and convert to float
            price = ''.join(filter(lambda x: x.isdigit() or x == '.', price_text))
            try:
                return float(price)
            except ValueError:
                return 0.0
        return 0.0
    
    @staticmethod
    def _extract_image(soup):
        # Example implementation - adjust selectors for target sites
        img_tag = soup.select_one('img.styled__StyledImage-sc-1fweb41-1 hCXoFX') 
        return img_tag.get('src') if img_tag else "img not found"
    
    def _extract_rating(soup):
         rating_element = soup.select_one("span.star-rating__score")
         return rating_element.text.strip() if rating_element else None
    
    def _extract_manufacturer(soup):
         maufacturer_tag = soup.select_one("p.span.styled__Name-sc-6tl8kn-0 iWxIC")
         return  maufacturer_tag.text.strip() if  maufacturer_tag else None
    
    @staticmethod
    def _extract_description(soup):
        # Example implementation - adjust selectors for target sites
        desc_tag = soup.select_one('.product-description') or soup.select_one('#description')
        return desc_tag.text.strip() if desc_tag else None

# File: services/scraping-service/app/scraper.py
# import requests
# from bs4 import BeautifulSoup
# import time
# import random
# import logging
# from abc import ABC, abstractmethod
# from typing import Dict, List, Any, Optional, Union
# import json
# import os
# from datetime import datetime

# # Configure logging
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#     handlers=[
#         logging.FileHandler("scraper.log"),
#         logging.StreamHandler()
#     ]
# )
# logger = logging.getLogger("scraper")

# class RateLimiter:
#     """Handles rate limiting for scraping requests to avoid overloading servers."""
    
#     def __init__(self, requests_per_minute: int = 20):
#         self.requests_per_minute = requests_per_minute
#         self.minimum_interval = 60.0 / requests_per_minute
#         self.last_request_time = 0
    
#     def wait(self):
#         """Wait appropriate time to respect rate limits."""
#         current_time = time.time()
#         elapsed = current_time - self.last_request_time
        
#         if elapsed < self.minimum_interval:
#             sleep_time = self.minimum_interval - elapsed
#             # Add small random jitter to avoid patterns
#             sleep_time += random.uniform(0.1, 0.3)
#             time.sleep(sleep_time)
            
#         self.last_request_time = time.time()


# class UserAgentRotator:
#     """Rotates user agents to avoid detection."""
    
#     def __init__(self):
#         self.user_agents = [
#             'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
#             'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
#             'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
#             'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36'
#         ]
    
#     def get_random_user_agent(self) -> str:
#         """Return a random user agent from the list."""
#         return random.choice(self.user_agents)


# class BaseScraper(ABC):
#     """Abstract base class for scrapers."""
    
#     def __init__(self, 
#                  rate_limiter: Optional[RateLimiter] = None, 
#                  user_agent_rotator: Optional[UserAgentRotator] = None):
#         self.rate_limiter = rate_limiter or RateLimiter()
#         self.user_agent_rotator = user_agent_rotator or UserAgentRotator()
#         self.session = requests.Session()
    
#     def get_headers(self) -> Dict[str, str]:
#         """Get request headers with a random user agent."""
#         return {
#             'User-Agent': self.user_agent_rotator.get_random_user_agent(),
#             'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
#             'Accept-Language': 'en-US,en;q=0.5',
#             'Connection': 'keep-alive',
#             'Upgrade-Insecure-Requests': '1',
#         }
    
#     def fetch_page(self, url: str) -> Optional[BeautifulSoup]:
#         """Fetch a page and parse it with BeautifulSoup."""
#         try:
#             # Respect rate limits
#             self.rate_limiter.wait()
            
#             # Make the request
#             response = self.session.get(url, headers=self.get_headers(), timeout=30)
#             response.raise_for_status()
            
#             # Parse HTML with BeautifulSoup
#             return BeautifulSoup(response.text, 'html.parser')
        
#         except requests.exceptions.RequestException as e:
#             logger.error(f"Error fetching {url}: {e}")
#             return None
    
#     @abstractmethod
#     def scrape_product(self, url: str) -> Dict[str, Any]:
#         """Scrape product details from a specific URL."""
#         pass
    
#     @abstractmethod
#     def search_products(self, query: str, category: Optional[str] = None) -> List[Dict[str, Any]]:
#         """Search for products based on a query and optional category."""
#         pass


# class TescoScraper(BaseScraper):
#     """Scraper for Tesco grocery products."""
    
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.base_url = "https://www.tesco.com"
#         self.search_url = f"{self.base_url}/groceries/en-GB/shop/marketplace/all"
      
    
#     def scrape_product(self, url: str) -> Dict[str, Any]:
#         """Scrape product details from a Tesco product page."""
#         soup = self.fetch_page(url)
#         if not soup:
#             return {}
#         <h3 class="component__StyledHeading-sc-1t0ixqu-0 iDJPjF ddsweb-heading styled-sc-mz7xly-0 kXoSwE styled__StyledTitle-sc-1a6zg7t-0 etoGWB b_hC4 ddsweb-title-link__container"><a class="styled__Anchor-sc-1i711qa-0 gRXcDF ddsweb-title-link__link ddsweb-link__anchor" href="/groceries/en-GB/products/325491413" aria-label="Tefal 6.5L Digital Dual Air Fryer - Easy Fry &amp; Grill XXL" data-di-id="di-id-c0600096-4a69a9c6"><span class="styled__Text-sc-1i711qa-1 bsLJsh ddsweb-link__text">Tefal 6.5L Digital Dual Air Fryer - Easy Fry &amp; Grill XXL</span></a></h3>
#         try:
#             # These selectors will need to be updated based on Tesco's actual HTML structure
#             product = {
#                 "store": "Tesco",
#                 "url": url,
#                 "timestamp": datetime.now().isoformat(),
#                 "name": soup.select_one("h1.product-details-tile__title").text.strip() if soup.select_one("h1.product-details-tile__title") else "",
#                 "price": self._extract_price(soup),
#                 "image_url": self._extract_image_url(soup),
#                 "product_id": self._extract_product_id(url),
#                 "currency": "GBP",
#                 "category": self._extract_category(soup),
#                 "rating": self._extract_rating(soup),
#                 "size": self._extract_size(soup),
#                 "brand": self._extract_brand(soup),
#             }
#             return product
            
#         except Exception as e:
#             logger.error(f"Error scraping product {url}: {e}")
#             return {
#                 "store": "Tesco",
#                 "url": url,
#                 "error": str(e),
#                 "timestamp": datetime.now().isoformat()
#             }
    
#     def search_products(self, query: str, category: Optional[str] = None) -> List[Dict[str, Any]]:
#         """Search for products on Tesco based on a query."""
#         search_params = {"query": query}
#         if category:
#             search_params["category"] = category
            
#         search_url = f"{self.search_url}?query={query}"
#         soup = self.fetch_page(search_url)
#         if not soup:
#             return []
            
#         products = []
#         # Find product links on the search results page
#         product_elements = soup.select("li.product-list--list-item")
        
#         for product_element in product_elements[:30]:  # Limit to first 10 for testing
#             try:
#                 product_link = product_element.select_one("a.product-image-wrapper")
#                 if product_link and 'href' in product_link.attrs:
#                     product_url = self.base_url + product_link['href']
#                     # Basic data extraction from search results
#                     product = {
#                         "store": "Tesco",
#                         "url": product_url,
#                         "name": product_element.select_one("h3").text.strip() if product_element.select_one("h3") else "",
#                         "price": self._extract_search_price(product_element),
#                         "image_url": self._extract_search_image(product_element),
#                     }
#                     products.append(product)
#             except Exception as e:
#                 logger.error(f"Error extracting product from search results: {e}")
                
#         return products
    
#     # Helper methods for extraction
#     def _extract_price(self, soup: BeautifulSoup) -> str:
#         price_element = soup.select_one("span.value")
#         if price_element:
#             return price_element.text.strip()
#         return ""
    
#     def _extract_image_url(self, soup: BeautifulSoup) -> str:
#         img_element = soup.select_one("img.styled__StyledImage-sc-1fweb41-1 hCXoFX")
#         if img_element and 'src' in img_element.attrs:
#             return img_element['src']
#         return ""
    
#     def _extract_product_id(self, url: str) -> str:
#         # Extract product ID from URL if possible
#         try:
#             return url.split('/')[-1]
#         except:
#             return ""
    
#     def _extract_category(self, soup: BeautifulSoup) -> str:
#         breadcrumb = soup.select("ol.breadcrumbs li")
#         if breadcrumb and len(breadcrumb) > 1:
#             return breadcrumb[-2].text.strip()
#         return ""
    
#     def _extract_rating(self, soup: BeautifulSoup) -> str:
#         rating_element = soup.select_one("span.star-rating__score")
#         if rating_element:
#             return rating_element.text.strip()
#         return ""
    
#     def _extract_size(self, soup: BeautifulSoup) -> str:
#         size_element = soup.select_one("div.product-info__quantity")
#         if size_element:
#             return size_element.text.strip()
#         return ""
    
#     def _extract_brand(self, soup: BeautifulSoup) -> str:
#         brand_element = soup.select_one("div.product-info__producer")
#         if brand_element:
#             return brand_element.text.strip()
#         return ""
    
#     def _extract_search_price(self, element) -> str:
#         price_element = element.select_one("span.value")
#         if price_element:
#             return price_element.text.strip()
#         return ""
    
#     def _extract_search_image(self, element) -> str:
#         img_element = element.select_one("img")
#         if img_element and 'src' in img_element.attrs:
#             return img_element['src']
#         return ""


# class AldiBriefScraper(BaseScraper):
#     """Simplified/brief scraper for Aldi products to demonstrate structure."""
    
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.base_url = "https://groceries.aldi.co.uk"
#         self.search_url = f"{self.base_url}/search"
    
#     def scrape_product(self, url: str) -> Dict[str, Any]:
#         # Implementation would be similar to TescoScraper
#         soup = self.fetch_page(url)
#         if not soup:
#             return {}
        
#         # Simplified placeholder
#         return {
#             "store": "Aldi",
#             "url": url,
#             "timestamp": datetime.now().isoformat(),
#             # Additional fields would be extracted here
#         }
    
#     def search_products(self, query: str, category: Optional[str] = None) -> List[Dict[str, Any]]:
#         # Implementation would be similar to TescoScraper
#         return []


# class BootsScraper(BaseScraper):
#     """Scraper for Boots pharmacy products."""
    
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.base_url = "https://www.boots.com"
#         self.search_url = f"{self.base_url}/search"
    
#     def scrape_product(self, url: str) -> Dict[str, Any]:
#         # Implementation would be similar to TescoScraper but with Boots-specific selectors
#         soup = self.fetch_page(url)
#         if not soup:
#             return {}
        
#         # Placeholder
#         return {
#             "store": "Boots",
#             "url": url,
#             "timestamp": datetime.now().isoformat(),
#             # Additional fields would be extracted here
#         }
    
#     def search_products(self, query: str, category: Optional[str] = None) -> List[Dict[str, Any]]:
#         # Implementation would be similar to TescoScraper but with Boots-specific selectors
#         return []


# class SportDirectScraper(BaseScraper):
#     """Scraper for SportsDirect shoes and clothing."""
    
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.base_url = "https://www.sportsdirect.com"
#         self.search_url = f"{self.base_url}/search"
    
#     def scrape_product(self, url: str) -> Dict[str, Any]:
#         # Implementation would be similar to TescoScraper but with SportsDirect-specific selectors
#         soup = self.fetch_page(url)
#         if not soup:
#             return {}
        
#         # Placeholder
#         return {
#             "store": "SportsDirect",
#             "url": url,
#             "timestamp": datetime.now().isoformat(),
#             # Additional fields would be extracted here
#         }
    
#     def search_products(self, query: str, category: Optional[str] = None) -> List[Dict[str, Any]]:
#         # Implementation would be similar to TescoScraper but with SportsDirect-specific selectors
#         return []


# # Factory to return the appropriate scraper based on store name
# class ScraperFactory:
#     """Factory class to create appropriate scraper instances."""
    
#     @staticmethod
#     def get_scraper(store_name: str, **kwargs) -> BaseScraper:
#         """Return the appropriate scraper based on store name."""
#         scrapers = {
#             "tesco": TescoScraper,
#             "aldi": AldiBriefScraper,
#             "boots": BootsScraper,
#             "sportsdirect": SportDirectScraper,
#             # Add more scrapers as implemented
#         }
        
#         store_name = store_name.lower().replace(" ", "")
#         if store_name in scrapers:
#             return scrapers[store_name](**kwargs)
#         else:
#             raise ValueError(f"No scraper available for {store_name}")


# # API Integration Example - could be moved to a separate module
# class RetailerAPI:
#     """Base class for retailer API integrations."""
    
#     def __init__(self, api_key: Optional[str] = None):
#         self.api_key = api_key or os.environ.get("RETAILER_API_KEY", "")
#         self.session = requests.Session()
    
#     def get_headers(self) -> Dict[str, str]:
#         """Get request headers for API calls."""
#         return {
#             "Authorization": f"Bearer {self.api_key}",
#             "Content-Type": "application/json",
#             "Accept": "application/json"
#         }


# class TescoAPI(RetailerAPI):
#     """API integration for Tesco (if available)."""
    
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.base_url = "https://api.tesco.com/v1"  # Placeholder URL
    
#     def search_products(self, query: str, category: Optional[str] = None) -> List[Dict[str, Any]]:
#         """Search for products using Tesco API."""
#         try:
#             params = {"query": query}
#             if category:
#                 params["category"] = category
                
#             response = self.session.get(
#                 f"{self.base_url}/products/search",
#                 headers=self.get_headers(),
#                 params=params
#             )
#             response.raise_for_status()
#             return response.json().get("products", [])
            
#         except requests.exceptions.RequestException as e:
#             logger.error(f"Error calling Tesco API: {e}")
#             return []
    
#     def get_product(self, product_id: str) -> Dict[str, Any]:
#         """Get product details by ID using Tesco API."""
#         try:
#             response = self.session.get(
#                 f"{self.base_url}/products/{product_id}",
#                 headers=self.get_headers()
#             )
#             response.raise_for_status()
#             return response.json()
            
#         except requests.exceptions.RequestException as e:
#             logger.error(f"Error calling Tesco API for product {product_id}: {e}")
#             return {}


# # Data Manager to handle normalized product data
# class ProductDataManager:
#     """Manages the normalization and storage of product data."""
    
#     def normalize_product(self, product: Dict[str, Any], store: str) -> Dict[str, Any]:
#         """Normalize product data from different sources to a common schema."""
#         # Basic normalization - in a real app, this would be more robust
#         normalized = {
#             "store": store,
#             "product_id": product.get("product_id", ""),
#             "name": product.get("name", ""),
#             "url": product.get("url", ""),
#             "image_url": product.get("image_url", ""),
#             "price": self._normalize_price(product.get("price", "")),
#             "currency": product.get("currency", "GBP"),
#             "brand": product.get("brand", ""),
#             "category": product.get("category", ""),
#             "rating": self._normalize_rating(product.get("rating", "")),
#             "size": product.get("size", ""),
#             "timestamp": product.get("timestamp", datetime.now().isoformat())
#         }
#         return normalized
    
#     def _normalize_price(self, price: Union[str, float]) -> float:
#         """Convert price string to float."""
#         if isinstance(price, float):
#             return price
            
#         try:
#             # Remove currency symbols and commas
#             price_str = str(price).replace("£", "").replace("$", "").replace(",", "")
#             # Extract first number if there are multiple
#             price_str = price_str.split()[0]
#             return float(price_str)
#         except (ValueError, TypeError):
#             return 0.0
    
#     def _normalize_rating(self, rating: Union[str, float]) -> float:
#         """Normalize rating to a 0-5 scale."""
#         try:
#             if isinstance(rating, float):
#                 return min(5.0, max(0.0, rating))
                
#             # Extract first number if there are multiple
#             rating_str = str(rating).split()[0]
#             rating_val = float(rating_str)
            
#             # Normalize to 0-5 scale if needed
#             if rating_val > 5.0:
#                 return rating_val / 20.0 * 5.0  # Assuming 0-100 scale
#             return rating_val
#         except (ValueError, TypeError):
#             return 0.0