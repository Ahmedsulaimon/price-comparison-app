import requests
from bs4 import BeautifulSoup
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from datetime import datetime
from .utils import RateLimiter, UserAgentRotator, logger
import time

class BaseScraper(ABC):
    """Abstract base class for scrapers."""
    
    def __init__(self, 
                 rate_limiter: Optional[RateLimiter] = None, 
                 user_agent_rotator: Optional[UserAgentRotator] = None):
        self.rate_limiter = rate_limiter or RateLimiter()
        self.user_agent_rotator = user_agent_rotator or UserAgentRotator()
        self.session = requests.Session()
    
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
        """Fetch a page and parse it with BeautifulSoup."""
        try:
            # Respect rate limits
            self.rate_limiter.wait()
           
            # Make the request
            response = self.session.get(url, headers=self.get_headers(), timeout=30)
            response.raise_for_status()
            
            # Parse HTML with BeautifulSoup
            return BeautifulSoup(response.text, 'lxml')
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching {url}: {e}")
            return None
    
    @abstractmethod
    def scrape_product(self, url: str) -> Dict[str, Any]:
        """Scrape product details from a specific URL."""
        pass
    
    @abstractmethod
    def search_products(self, query: str, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search for products based on a query and optional category."""
        pass