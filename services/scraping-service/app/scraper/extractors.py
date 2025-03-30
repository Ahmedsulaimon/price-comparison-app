import re
from bs4 import BeautifulSoup
from typing import Optional
from ..scraper.utils import logger
from fastapi import logger

class ProductExtractor:
    """Helper class for extracting product details from HTML."""
    
    @staticmethod
    def extract_title(soup: BeautifulSoup, selector: str = "h3 a span") -> Optional[str]:
        """Extract product title using the provided selector."""
        title_tag = soup.select_one(selector)
        return title_tag.text.strip() if title_tag else None
        
    
    @staticmethod
    def extract_discounted_price(soup: BeautifulSoup, selector: str = "span.base-price__comparison-price") -> Optional[float]:
        """Extract product discount using the provided selector."""
        discount_tag = soup.select_one(selector)
        return discount_tag.text.strip() if discount_tag else None
    
    @staticmethod
    def extract_price(soup: BeautifulSoup, selector: str = 'span.price') -> Optional[float]:
        """Extract product discount using the provided selector."""
        price_tag = soup.select_one(selector)
        if price_tag:
            price_text = price_tag.text.strip()
            # Remove currency symbols and convert to float
            price = ''.join(filter(lambda x: x.isdigit() or x == '.', price_text))
            try:
                return float(price)
            except ValueError:
                return None
        return None
    
    @staticmethod
    def extract_size(soup: BeautifulSoup, selector: str = 'span.price') -> Optional[float]:
        """Extract product size using the provided selector."""
        size_tag = soup.select_one(selector)
        return size_tag.text.strip() if size_tag else None
    
    @staticmethod
    def extract_iceland_size(soup: BeautifulSoup, selector: str) -> Optional[str]:
        """Extract size from product name."""
        name_tag = soup.select_one(selector)
        if name_tag:
            name_text = name_tag.text.strip()
            # Look for size patterns like "600g" or "2 Litres"
            size_match = re.search(r'(\d+\s*(g|kg|ml|l|litre|litres))', name_text, re.IGNORECASE)
            if size_match:
                return size_match.group(1)
        return None
    
    # @staticmethod
    # def extract_image_url(soup: BeautifulSoup, selector: str = 'img') -> Optional[str]:
    #     """Extract product image URL, prioritizing <img> src, then <source> srcset."""
        
    #     # Find the img tag inside picture
    #     img_tag = soup.select_one(selector)
        
    #     if img_tag:
    #         # Prefer the 'src' attribute from the img tag
    #         if img_tag.has_attr('src'):
    #             return img_tag['src']
        
    #     # If img tag is missing, check <source> inside <picture>
    #     picture_tag = soup.select_one('picture source')
    #     if picture_tag and picture_tag.has_attr('srcset'):
    #         # Take the first URL from srcset
    #         srcset_urls = picture_tag['srcset'].split(',')
    #         if srcset_urls:
    #             return srcset_urls[0].split(' ')[0]  # Get the first URL before space
        
    #     return None

    @staticmethod
    def extract_image_url(soup: BeautifulSoup, selector: str = 'img[src]') -> Optional[str]:
        """Extract product image URL with better handling of lazy loading."""
        # First try the direct img src
        img_tag = soup.select_one(selector)
        if img_tag and img_tag.has_attr('src'):
            src = img_tag['src']
            if src and not src.startswith('data:'):  # Skip placeholder images
                return src
        
        # Then try the picture > source srcset
        source_tag = soup.select_one('picture source[srcset]')
        if source_tag:
            srcset = source_tag['srcset']
            if srcset:
                # Get the first URL from srcset (highest resolution usually first)
                first_url = srcset.split(',')[0].strip().split(' ')[0]
                if first_url and not first_url.startswith('data:'):
                    return first_url
        
        # Finally, check for lazy-loaded images (data-src attributes)
        lazy_img = soup.select_one('img[data-src]')
        if lazy_img and lazy_img.has_attr('data-src'):
            return lazy_img['data-src']
        
        return None

    
    @staticmethod
    def extract_shipping_cost(soup: BeautifulSoup, selector: str = 'span.shipping-cost') -> Optional[str]:
        """Extract shipping cost using the provided selector."""
        shipping_tag = soup.select_one(selector)
        return shipping_tag.text.strip() if shipping_tag else None
    
    @staticmethod
    def extract_rating(soup: BeautifulSoup, selector: str, attr: str = "alt") -> Optional[float]:
        """Extract the product rating from the image alt attribute."""
        rating_element = soup.select_one(selector)
        if rating_element and rating_element.has_attr(attr):
            try:
                rating_text = rating_element[attr]
                # Handle both "4.4548" and "4_5" formats
                if '_' in rating_text:  # Like "4_5" meaning 4.5
                    parts = rating_text.split('_')
                    return float(f"{parts[0]}.{parts[1]}")
                return float(rating_text)
            except (ValueError, IndexError):
                return None
        return None
    
    def _extract_morrisons_rating(soup: BeautifulSoup, selector: str):
        """Extract Morrisons-specific rating"""
        try:
            rating_container = soup.select_one(selector)
            if not rating_container:
                return None
                
            # Extract the rating value from the aria-label
            rating_text = rating_container.get('aria-label', '')
            if not rating_text:
                return None
                
            # Extract the numeric rating (e.g., "3.3" from "Rating, 3.3 out of 5 from 32 reviews")
            match = re.search(r'(\d+\.\d+)', rating_text)
            if match:
                return float(match.group(1))
                
            # Alternative approach: Count the filled stars
            filled_stars = len(soup.select("svg[data-test='icon__reviews']"))
            half_stars = len(soup.select("svg[data-test='icon__reviews_outline']")) / 2
            if filled_stars > 0:
                return float(filled_stars + half_stars)
                
        except Exception as e:
             logger.warning(f"Error extracting rating: {e}")
        return None
    
    @staticmethod
    def extract_review_count(soup: BeautifulSoup, selector: str = "div.reviews a.numberOfReviews") -> Optional[int]:
        """Extract the number of reviews from text like 'Reviews (908)'"""
        reviews_element = soup.select_one(selector)
        if reviews_element:
            try:
                reviews_text = reviews_element.get_text(strip=True)
                # Extract number from text like "Reviews (908)"
                match = re.search(r'\((\d+)\)', reviews_text)
                if match:
                    return int(match.group(1))
            except (ValueError, AttributeError):
                return None
        return None
    def _extract_tesco_badges(soup: BeautifulSoup, selector: str = "div.reviews a.numberOfReviews") -> Optional[str]:
        """Extract Tesco-specific badges like 'New' or 'Sponsored'."""
        badges = soup.select_one(selector)
        if badges:
            return ", ".join(badge.get_text(strip=True) for badge in badges)
        return None
    @staticmethod
    def tesco_extract_rating(soup: BeautifulSoup, selector: str) -> Optional[float]:
        """Extract rating from Tesco's star rating component."""
        rating_container = soup.select_one(selector)
        if rating_container:
            rating_text = rating_container.get('aria-label', '')
            if rating_text:
                try:
                    # Extract numeric value from text like "Average customer rating 4.7 out of 5 stars"
                    match = re.search(r'(\d+\.\d+)', rating_text)
                    if match:
                        return float(match.group(1))
                except (ValueError, AttributeError):
                    return None
        return None
    
    @staticmethod
    def extract_manufacturer(soup: BeautifulSoup, selector: str = 'span.manufacturer') -> Optional[str]:
        """Extract manufacturer using the provided selector."""
        manufacturer_tag = soup.select_one(selector)
        return manufacturer_tag.text.strip() if manufacturer_tag else None
    
    @staticmethod
    def extract_description(soup: BeautifulSoup, selector: str = 'div.product-description') -> Optional[str]:
        """Extract product description using the provided selector."""
        desc_tag = soup.select_one(selector)
        return desc_tag.text.strip() if desc_tag else None
    
    @staticmethod
    def extract_product_link(soup: BeautifulSoup, base_url: str, selector: str = 'a.product-link') -> Optional[str]:
        """Extract product link using the provided selector."""
        link_tag = soup.select_one(selector)
        if link_tag and 'href' in link_tag.attrs:
            href = link_tag['href']
            # Add base URL if the href is relative
            if href.startswith('/'):
                return base_url + href
            return href
        return None