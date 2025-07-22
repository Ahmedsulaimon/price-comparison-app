from typing import Optional
from bs4 import BeautifulSoup


@staticmethod
def extract_price(soup: BeautifulSoup, selector: str = 'span.price') -> Optional[float]:
    """Extract product price using the provided selector. Converts pence to pounds when needed."""
    price_tag = soup.select_one(selector)
    if price_tag:
        price_text = price_tag.text.strip().lower()
        # Check if it's in pence (e.g., '52p')
        is_pence = 'p' in price_text

        # Remove non-numeric characters except '.' (e.g., £, p, whitespace)
        price_clean = ''.join(filter(lambda x: x.isdigit() or x == '.', price_text))

        try:
            price = float(price_clean)
            # Convert pence to pounds
            return round(price / 100, 2) if is_pence else round(price, 2)
        except ValueError:
            return None
    return None


