# analyzers/recommendation_engine.py
from .price_analyzer import PriceAnalyzer

class RecommendationEngine:
    def generate_recommendations(self, product_name: str) -> list:
        analyzer = PriceAnalyzer()
        return analyzer.get_best_deals(product_name)
