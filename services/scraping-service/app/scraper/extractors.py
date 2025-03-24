from bs4 import BeautifulSoup
from typing import Optional

class ProductExtractor:
    """Helper class for extracting product details from HTML."""
    
    @staticmethod
    def extract_title(soup: BeautifulSoup, selector: str = "h3 a span") -> Optional[str]:
        """Extract product title using the provided selector."""
        title_tag = soup.select_one(selector)
        return title_tag.text.strip() if title_tag else None
    
    @staticmethod
    def extract_discounted_price(soup: BeautifulSoup, selector: str = 'a p p') -> Optional[float]:
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
    def extract_image_url(soup: BeautifulSoup, selector: str = 'img.product-image') -> Optional[str]:
        """Extract product image URL using the provided selector."""
        img_tag = soup.select_one(selector)
        # Check for src or srcset attributes
        if img_tag:
            if 'src' in img_tag.attrs:
                return img_tag.get('src')
            elif 'srcset' in img_tag.attrs:
                # Get the first URL from srcset
                srcset = img_tag.get('srcset')
                urls = srcset.split(',')
                if urls:
                    return urls[0].split(' ')[0]
        return None
    
    @staticmethod
    def extract_shipping_cost(soup: BeautifulSoup, selector: str = 'span.shipping-cost') -> Optional[str]:
        """Extract shipping cost using the provided selector."""
        shipping_tag = soup.select_one(selector)
        return shipping_tag.text.strip() if shipping_tag else None
    
    @staticmethod
    def extract_rating(product_element, selector: str, attr: str = "alt") -> Optional[float]:
        """Extract the product rating from the image alt attribute."""
        rating_element = product_element.select_one(selector)
        if rating_element and rating_element.has_attr(attr):
            try:
                return float(rating_element[attr])
            except ValueError:
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