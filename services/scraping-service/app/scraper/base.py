import random
import requests
from bs4 import BeautifulSoup
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from datetime import datetime
from .utils import RateLimiter, UserAgentRotator, logger
import time

class BaseScraper(ABC):
    """Abstract base class for scrapers."""
    
    def __init__(self,  proxies=None, 
        rate_limiter: Optional[RateLimiter] = None, 
        user_agent_rotator: Optional[UserAgentRotator] = None):

        self.rate_limiter = rate_limiter or RateLimiter()
        self.user_agent_rotator = user_agent_rotator or UserAgentRotator()
        self.session = requests.Session()
        self.base_url = "https://www.tesco.com"

        self.proxies = proxies or []
        self.current_proxy = None
    
    def rotate_proxy(self):
        if self.proxies:
            self.current_proxy = random.choice(self.proxies)
            self.session.proxies = {'http': self.current_proxy, 'https': self.current_proxy}
    
    def get_headers(self) -> Dict[str, str]:
        """Get request headers with a random user agent."""
        return {
            'User-Agent': self.user_agent_rotator.get_random_user_agent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            
        }
    
    def fetch_page(self, url: str) -> Optional[BeautifulSoup]:
        """More robust page fetching with retries and better headers"""
        headers = self.get_headers()
        headers.update({
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Referer': self.base_url,
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
        })

        for attempt in range(3):  # Retry up to 3 times
            try:
                self.rate_limiter.wait()
                
                # Add random delay between 1-3 seconds
                time.sleep(random.uniform(1, 3))
                
                response = self.session.get(
                    url,
                    headers=headers,
                    timeout=30,
                    allow_redirects=True,
                    cookies={'notice_behavior': 'expressed,eu'},  # Bypass cookie notice
                )
                
                # Check for soft bans (403, 429)
                if response.status_code in [403, 429]:
                    logger.warning(f"Blocked detected, waiting longer...")
                    time.sleep(random.uniform(10, 20))
                    continue
                    
                response.raise_for_status()
                
                # Verify we got actual product content
                if "product" not in response.text.lower():
                    raise ValueError("Page doesn't contain product data")
                    
                return BeautifulSoup(response.text, 'lxml')
                
            except Exception as e:
                logger.warning(f"Attempt {attempt+1} failed: {str(e)}")
                if attempt == 2:  # Last attempt
                    logger.error(f"Failed to fetch {url} after 3 attempts")
                    return None
                time.sleep(random.uniform(5, 10))
    # @abstractmethod
    # def scrape_product(self, url: str) -> Dict[str, Any]:
    #     """Scrape product details from a specific URL."""
    #     pass
    
    # @abstractmethod
    # def search_products(self, query: str, category: Optional[str] = None) -> List[Dict[str, Any]]:
    #     """Search for products based on a query and optional category."""
    #     pass