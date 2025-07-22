# analyzers/recommendation_engine.py
from .price_analyzer import PriceAnalyzer

class RecommendationEngine:
    def generate_recommendations(self, product_name: str) -> list:
        analyzer = PriceAnalyzer()
        return analyzer.get_best_deals(product_name)
        
    def _analyze_product(self, product: dict) -> dict:
        """Modified to work with both API and direct calls"""
        analyzer = PriceAnalyzer()
        return analyzer._analyze_product(product)