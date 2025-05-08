import requests
from .price_predictor import PricePredictor
from .value_calculator import ValueCalculator

class PriceAnalyzer:
    def __init__(self):
        # Initialize with API base URL and helper classes
        self.base_url = "http://localhost:5000"  # Base API endpoint
        self.predictor = PricePredictor()  # Price prediction module
        self.calculator = ValueCalculator()  # Value scoring module

    def get_best_deals(self, product_name: str) -> list:
        """Get sorted list of best deals for a product"""
        products = self._fetch_products(product_name)  # Fetch raw product data
        analyzed_products = [self._analyze_product(p) for p in products]  # Analyze each product
        return sorted(analyzed_products, 
                    key=lambda x: x['value_score'],  # Sort by value score
                    reverse=True)  # Highest scores first

    def _fetch_products(self, product_name: str):
        """Fetch products from API"""
        response = requests.get(
            f"{self.base_url}/api/products/compare",
            params={'name': product_name}  # Search parameter
        )
        return response.json()  # Return parsed JSON response

    def _analyze_product(self, product: dict) -> dict:
        """Enhance product data with analysis"""
        prediction = self.predictor.predict_next_week_prices(
            product['price_history'])  # Get price prediction
        product['prediction'] = prediction  # Add prediction data
        product['value_score'] = self.calculator.calculate_value_score(product)  # Calculate value
        product['recommendation'] = self._generate_natural_recommendation(product)  # Generate advice
        return product  # Return enriched product data
    
#I then generate a natural language recommendation using 
# thresholds for confidence and price movement. 
# For example, if the predicted price drops significantly and 
# confidence is above 70 %, the system returns:
# “Good time to buy (expected drop: £0.10, 82% confidence)”
# Otherwise, it might say “Stable pricing expected” or 
# even “Consider waiting”—offering actionable advice for 
# real-world decisions.
# This module is entirely decoupled, meaning I can later plug in 
# a more advanced model like ARIMA or LSTM with zero changes to 
# the rest of the app, which makes my app sustainable.

    def _generate_natural_recommendation(self, product: dict) -> str:
        """Generate human-readable recommendation"""
        pred = product['prediction']
        diff = pred['predicted_price'] - product['price']  # Price difference
        confidence = pred['confidence']  # Prediction confidence

        # Recommendation logic:
        if diff < -0.05 and confidence > 0.7:
            return f"Good time to buy ( {abs(diff):.2f} expected drop, {confidence*100:.0f}% confidence)"
        elif diff > 0.05 and confidence > 0.6:
            return f"Consider waiting ( {diff:.2f} expected rise, {confidence*100:.0f}% confidence)"
        elif 0 <= diff <= 0.05:
            return "Stable pricing expected, buy anytime"
        return "No strong recommendation"  # Default fallback