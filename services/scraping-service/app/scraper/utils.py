import time
import random
import logging

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
    """Handles rate limiting for scraping requests to avoid overloading servers."""
    
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


class UserAgentRotator:
    """Rotates user agents to avoid detection."""
    
    def __init__(self):
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36'
        ]
    
    def get_random_user_agent(self) -> str:
        """Return a random user agent from the list."""
        return random.choice(self.user_agents)