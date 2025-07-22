# product_service.py
from rapidfuzz import process, fuzz

class ProductMatcher:
    def __init__(self):
        self.stop_words = {'corner', 'with', 'flakes', 'yogurt', 'juice'}
        self.category_keywords = {
            'onion': ['onion', 'bulb', 'allium'],
            'banana': ['banana'],
             'oranges' : ['oranges'],
             'milk' : ['skimmed milk', 'semi-skimmed milk', 'whole milk'],
             'butter' : ['butter'],
             'carrot' : ['carrot'],
             'cucumber' : ['cucumber'],
             'pepper': ['yellow', 'red'],
             'potatoes' : ['baking potatoes', 'white potatoes'],
             'Bread': ['Bread'],
             'chicken breast' : ['chicken breast'],
             'Granulated Sugar' : ['Granulated Sugar'],
             'rice': ['rice'],
             'avocado' : ['avocado'],
             'Baked Beans': ['Baked Beans'],
             'Muller Corner': ['Muller Corner Vanilla Yogurt with Chocolate Balls','Muller Corner Banana Yogurt with Chocolate Flakes'],

        }

    def is_main_product(self, product_name: str, search_term: str) -> bool:
        """Verify if product matches the core search intent"""
        # Clean input
        clean_name = self._preprocess_name(product_name)
        clean_search = self._preprocess_name(search_term)
        
        # Exact match check
        if clean_search in clean_name.split():
            return True
            
        # Semantic similarity check
        category_words = self.category_keywords.get(clean_search, [])
        return any(word in clean_name for word in category_words)

    def _preprocess_name(self, name: str) -> str:
        """Normalize product names for matching"""
        name = name.lower()
        # Remove brand names and irrelevant words
        return ' '.join([word for word in name.split() 
                       if word not in self.stop_words and not word.isnumeric()])

    def best_match(self, products: list, search_term: str) -> list:
        """Fuzzy match products to search intent"""
        matches = []
        for product in products:
            score = fuzz.token_set_ratio(
                self._preprocess_name(product['name']),
                self._preprocess_name(search_term)
            )
            if score > 65:  # Threshold determined through testing
                matches.append((product, score))
        
        return sorted(matches, key=lambda x: x[1], reverse=True)