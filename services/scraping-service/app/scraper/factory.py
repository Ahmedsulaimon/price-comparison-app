from typing import Dict, Type
from .base import BaseScraper
from ..scraper.controller.tesco import TescoScraper
# Import other scrapers as you implement them

class ScraperFactory:
    """Factory class to create appropriate scraper instances."""
    
    # Registry of available scrapers
    _registry: Dict[str, Type[BaseScraper]] = {
        "tesco": TescoScraper,
        # Add more scrapers as implemented
    }
    
    @classmethod
    def get_scraper(cls, store_name: str, **kwargs) -> BaseScraper:
        """Return the appropriate scraper based on store name."""
        store_key = store_name.lower().replace(" ", "")
        
        if store_key in cls._registry:
            return cls._registry[store_key](**kwargs)
        else:
            available_stores = ", ".join(cls._registry.keys())
            raise ValueError(f"No scraper available for '{store_name}'. Available stores: {available_stores}")
    
    @classmethod
    def register_scraper(cls, store_name: str, scraper_class: Type[BaseScraper]) -> None:
        """Register a new scraper class."""
        cls._registry[store_name.lower().replace(" ", "")] = scraper_class
    
    @classmethod
    def get_available_stores(cls) -> list:
        """Return a list of all available stores."""
        return list(cls._registry.keys())