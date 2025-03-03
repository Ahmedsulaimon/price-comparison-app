import requests
from bs4 import BeautifulSoup

class WebScraper:
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
                'image_url': WebScraper._extract_image(soup),
                'description': WebScraper._extract_description(soup)
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
        title_tag = soup.select_one('h1') or soup.select_one('.product-title')
        return title_tag.text.strip() if title_tag else 'Title not found'
    
    @staticmethod
    def _extract_price(soup):
        # Example implementation - adjust selectors for target sites
        price_tag = soup.select_one('.price') or soup.select_one('[data-price]')
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
        img_tag = soup.select_one('.product-image img') or soup.select_one('[data-main-image]')
        return img_tag.get('src') if img_tag else None
    
    @staticmethod
    def _extract_description(soup):
        # Example implementation - adjust selectors for target sites
        desc_tag = soup.select_one('.product-description') or soup.select_one('#description')
        return desc_tag.text.strip() if desc_tag else 'Description not found'