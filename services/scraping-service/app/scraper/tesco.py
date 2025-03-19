from bs4 import BeautifulSoup
from typing import Dict, List, Any, Optional
from datetime import datetime
from .base import BaseScraper
from .extractors import ProductExtractor
from .utils import logger

class TescoScraper(BaseScraper):
    """Scraper for Tesco grocery products."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.base_url = "https://www.tesco.com"
        self.search_url = f"{self.base_url}/groceries/en-GB/search"
        self.marketplace_url = f"{self.base_url}/groceries/en-GB/shop/marketplace/all"
    
    def scrape_product(self, url: str) -> Dict[str, Any]:
        """Scrape product details from a Tesco product page."""
        soup = self.fetch_page(url)
        if not soup:
            return {
                "store": "Tesco",
                "url": url,
                "error": "Failed to fetch page",
                "timestamp": datetime.now().isoformat()
            }
        
        try:
            # These selectors need to be updated based on Tesco's actual HTML structure
            
            #<div class="styled__StyledNonInteractiveContainer-sc-1de15j6-7 klymXO ddsweb-rating__container" data-testid="star-rating" aria-label="Average customer rating 4 out of 5 stars"><svg class="ddsweb-rating__icon-active" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 12 12" fill="none"><path fill="var(--ddsweb-theme-colors-tesco-blue, #00539f)" stroke="var(--ddsweb-theme-colors-grayscale, #666666)" d="M6.24228 9.51529L6 9.38108L5.75772 9.51529L2.9631 11.0633L3.50417 7.74036L3.54466 7.49166L3.36886 7.31115L1.03607 4.91585L4.23368 4.42624L4.49754 4.38584L4.61078 4.14411L6 1.17863L7.38922 4.14411L7.50246 4.38584L7.76632 4.42624L10.9639 4.91585L8.63114 7.31115L8.45534 7.49166L8.49583 7.74035L9.0369 11.0633L6.24228 9.51529Z"></path></svg><svg class="ddsweb-rating__icon-active" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 12 12" fill="none"><path fill="var(--ddsweb-theme-colors-tesco-blue, #00539f)" stroke="var(--ddsweb-theme-colors-grayscale, #666666)" d="M6.24228 9.51529L6 9.38108L5.75772 9.51529L2.9631 11.0633L3.50417 7.74036L3.54466 7.49166L3.36886 7.31115L1.03607 4.91585L4.23368 4.42624L4.49754 4.38584L4.61078 4.14411L6 1.17863L7.38922 4.14411L7.50246 4.38584L7.76632 4.42624L10.9639 4.91585L8.63114 7.31115L8.45534 7.49166L8.49583 7.74035L9.0369 11.0633L6.24228 9.51529Z"></path></svg><svg class="ddsweb-rating__icon-active" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 12 12" fill="none"><path fill="var(--ddsweb-theme-colors-tesco-blue, #00539f)" stroke="var(--ddsweb-theme-colors-grayscale, #666666)" d="M6.24228 9.51529L6 9.38108L5.75772 9.51529L2.9631 11.0633L3.50417 7.74036L3.54466 7.49166L3.36886 7.31115L1.03607 4.91585L4.23368 4.42624L4.49754 4.38584L4.61078 4.14411L6 1.17863L7.38922 4.14411L7.50246 4.38584L7.76632 4.42624L10.9639 4.91585L8.63114 7.31115L8.45534 7.49166L8.49583 7.74035L9.0369 11.0633L6.24228 9.51529Z"></path></svg><svg class="ddsweb-rating__icon-active" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 12 12" fill="none"><path fill="var(--ddsweb-theme-colors-tesco-blue, #00539f)" stroke="var(--ddsweb-theme-colors-grayscale, #666666)" d="M6.24228 9.51529L6 9.38108L5.75772 9.51529L2.9631 11.0633L3.50417 7.74036L3.54466 7.49166L3.36886 7.31115L1.03607 4.91585L4.23368 4.42624L4.49754 4.38584L4.61078 4.14411L6 1.17863L7.38922 4.14411L7.50246 4.38584L7.76632 4.42624L10.9639 4.91585L8.63114 7.31115L8.45534 7.49166L8.49583 7.74035L9.0369 11.0633L6.24228 9.51529Z"></path></svg><svg class="ddsweb-rating__icon-inactive" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 12 12" fill="none"><path fill="var(--ddsweb-theme-colors-white, #ffffff)" stroke="var(--ddsweb-theme-colors-grayscale, #666666)" d="M6.24228 9.51529L6 9.38108L5.75772 9.51529L2.9631 11.0633L3.50417 7.74036L3.54466 7.49166L3.36886 7.31115L1.03607 4.91585L4.23368 4.42624L4.49754 4.38584L4.61078 4.14411L6 1.17863L7.38922 4.14411L7.50246 4.38584L7.76632 4.42624L10.9639 4.91585L8.63114 7.31115L8.45534 7.49166L8.49583 7.74035L9.0369 11.0633L6.24228 9.51529Z"></path></svg><p class="text__StyledText-sc-1jpzi8m-0 kiGrpI ddsweb-text styled__StyledHint-sc-1de15j6-8 MfAbW ddsweb-rating__hint">4 (1)</p></div>
            #<h3 class="component__StyledHeading-sc-1t0ixqu-0 iDJPjF ddsweb-heading styled-sc-mz7xly-0 kXoSwE styled__StyledTitle-sc-1a6zg7t-0 etoGWB b_hC4 ddsweb-title-link__container"><a class="styled__Anchor-sc-1i711qa-0 gRXcDF ddsweb-title-link__link ddsweb-link__anchor" href="/groceries/en-GB/products/325118760" aria-label="Ashley 18pc Plastic Food Bag Clips Set - 4 Sizes - Multicolour"><span class="styled__Text-sc-1i711qa-1 bsLJsh ddsweb-link__text">Ashley 18pc Plastic Food Bag Clips Set - 4 Sizes - Multicolour</span></a></h3>
            #<p class="text__StyledText-sc-1jpzi8m-0 eWKcpa ddsweb-text styled__StyledFootnote-sc-6tl8kn-3 cOHloe">Sold and sent by<span class="styled__Name-sc-6tl8kn-0 iWxIC">Rinkit</span></p>
            product = {
                "store": "Tesco",
                "url": url,
                "timestamp": datetime.now().isoformat(),
                "name": ProductExtractor.extract_title(
                    soup, 'h3.component__StyledHeading-sc-1t0ixqu-0 iDJPjF ddsweb-heading styled-sc-mz7xly-0 kXoSwE styled__StyledTitle-sc-1a6zg7t-0 etoGWB b_hC4 ddsweb-title-link__container'
                ),
                "price": ProductExtractor.extract_price(
                    soup, 'p.text__StyledText-sc-1jpzi8m-0 gyHOWz ddsweb-text styled__PriceText-sc-v0qv7n-1 cXlRF'
                ),
                "image_url": ProductExtractor.extract_image_url(
                    soup, 'img.styled__StyledImage-sc-1fweb41-1 hCXoFX'
                ),
                "shipping": ProductExtractor.extract_shipping_cost(
                    soup, 'p.text__StyledText-sc-1jpzi8m-0 eWKcpa ddsweb-text'
                ),
                "rating": ProductExtractor.extract_rating(
                    soup, 'div.styled__StyledNonInteractiveContainer-sc-1de15j6-7 klymXO ddsweb-rating__container'
                ),
                "manufacturer": ProductExtractor.extract_manufacturer(
                    soup, 'p.text__StyledText-sc-1jpzi8m-0 eWKcpa ddsweb-text styled__StyledFootnote-sc-6tl8kn-3 cOHloe'
                ),
                "description": ProductExtractor.extract_description(
                    soup, '.product-description'
                ),
                "currency": "GBP"
            }
            
            return {k: v for k, v in product.items() if v is not None}
            
        except Exception as e:
            logger.error(f"Error scraping product {url}: {e}")
            return {
                "store": "Tesco",
                "url": url,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
        

    
    def search_products(self, query: str, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search for products on Tesco based on a query."""
        search_url = f"{self.search_url}?query={query}"
        if category:
            search_url += f"&category={category}"
            
        soup = self.fetch_page(search_url)
        if not soup:
            return []
            
        products = []
        # Find product links on the search results page
        # Update this selector based on Tesco's actual HTML structure
        product_elements = soup.select("li.WL_DZ")
       #<p class="text__StyledText-sc-1jpzi8m-0 gyHOWz ddsweb-text styled__PriceText-sc-v0qv7n-1 cXlRF">£0.16</p>
        for product_element in product_elements[:10]:  # Limit to first 10 for testing
            try:
                product_link = ProductExtractor.extract_product_link(
                    product_element, 
                    self.base_url, 
                    "a.styled__ImageContainer-sc-1fweb41-0 irjUEM"
                )
                
                if product_link:
                    # Basic data extraction from search results
                    product = {
                        "store": "Tesco",
                        "url": product_link,
                        "name": ProductExtractor.extract_title(
                            product_element, "h3"
                        ),
                        "price": ProductExtractor.extract_price(
                            product_element, "p"
                        ),
                        "image_url": ProductExtractor.extract_image_url(
                            product_element, "img"
                        ),
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    # Remove None values
                    products.append({k: v for k, v in product.items() if v is not None})
                    
            except Exception as e:
                logger.error(f"Error extracting product from search results: {e}")
                
        return products
    
    def browse_marketplace(self) -> List[Dict[str, Any]]:
        """Browse the Tesco marketplace for featured products."""
        soup = self.fetch_page(self.marketplace_url)
        if not soup:
            return []
            
        products = []
        # Update this selector based on Tesco's actual HTML structure
       
        product_elements = soup.select("li.WL_DZ")
        
        for product_element in product_elements[:20]:  # Limit to first 20
            try:
                product_link = ProductExtractor.extract_product_link(
                    product_element, 
                    self.base_url, 
                    "a.styled__ImageContainer-sc-1fweb41-0.irjUEM"
                )
                
                if product_link:
                    # Basic data extraction
                    product = {
                        "store": "Tesco",
                        "url": product_link,
                        "name": ProductExtractor.extract_title(
                            product_element, "h3.component__StyledHeading-sc-1t0ixqu-0 iDJPjF ddsweb-heading styled-sc-mz7xly-0 kXoSwE styled__StyledTitle-sc-1a6zg7t-0 etoGWB b_hC4 ddsweb-title-link__container"
                        ),
                        "price": ProductExtractor.extract_price(
                            product_element, "p.text__StyledText-sc-1jpzi8m-0.gyHOWz.ddsweb-text.styled__PriceText-sc-v0qv7n-1.cXlRF"
                        ),
                        "image_url": ProductExtractor.extract_image_url(
                            product_element, "img.styled__StyledImage-sc-1fweb41-1.hCXoFX"
                        ),
                        "shipping": ProductExtractor.extract_shipping_cost(
                            product_element, "p.text__StyledText-sc-1jpzi8m-0.eWKcpa.ddsweb-text"
                        ),
                         "manufacturer": ProductExtractor.extract_manufacturer(
                            product_element, 'p.text__StyledText-sc-1jpzi8m-0 eWKcpa ddsweb-text styled__StyledFootnote-sc-6tl8kn-3 cOHloe'
                        ),
                         "rating": ProductExtractor.extract_rating(
                            product_element, 'div.styled__StyledNonInteractiveContainer-sc-1de15j6-7 klymXO ddsweb-rating__container'
                        ),
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    # Remove None values
                    products.append({k: v for k, v in product.items() if v is not None})
                    
            except Exception as e:
                logger.error(f"Error extracting product from marketplace: {e}")
                
        return products