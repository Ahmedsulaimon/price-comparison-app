# analyzers/price_analyzer.py
import requests
from .price_predictor import PricePredictor
from .value_calculator import ValueCalculator

class PriceAnalyzer:
    def __init__(self):
        self.base_url = "http://localhost:5000"
        self.predictor = PricePredictor()
        self.calculator = ValueCalculator()

    def get_best_deals(self, product_name: str) -> list:
        products = self._fetch_products(product_name)
        analyzed_products = [self._analyze_product(p) for p in products]
        return sorted(analyzed_products, key=lambda x: x['value_score'], reverse=True)

    def _fetch_products(self, product_name: str):
        response = requests.get(
            f"{self.base_url}/api/products/compare",
            params={'name': product_name}
        )
        return response.json()

    def _analyze_product(self, product: dict) -> dict:
        prediction = self.predictor.predict_next_week_prices(product['price_history'])
        product['prediction'] = prediction
        product['value_score'] = self.calculator.calculate_value_score(product)
        product['recommendation'] = self._generate_natural_recommendation(product)
        return product

    def _generate_natural_recommendation(self, product: dict) -> str:
        pred = product['prediction']
        diff = pred['predicted_price'] - product['price']
        confidence = pred['confidence']

        if diff < -0.05 and confidence > 0.7:
            return f"Good time to buy ( {abs(diff):.2f} expected drop, {confidence*100:.0f}% confidence)"
        elif diff > 0.05 and confidence > 0.6:
            return f"Consider waiting ( {diff:.2f} expected rise, {confidence*100:.0f}% confidence)"
        elif 0 <= diff <= 0.05:
            return "Stable pricing expected, buy anytime"
        return "No strong recommendation"
