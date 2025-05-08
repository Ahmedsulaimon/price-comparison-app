





# analyzers/price_predictor.py
import numpy as np

class PricePredictor:
    def predict_next_week_prices(self, price_history: list) -> dict:
        """Predict next week's price based on historical data"""
        # Extract recent prices (last 14 days max)
        prices = [h['price'] for h in price_history[-14:] if 'price' in h]

        # Handle edge cases:
        if not prices:  # No price history
            return {'predicted_price': 0.0, 'confidence': 0.0, 'current_price': 0.0}
        if len(prices) < 7:  # Insufficient data
            return {'predicted_price': prices[-1], 'confidence': 0, 'current_price': prices[-1]}

        # Weighted average prediction (recent prices weighted higher)
        weights = [0.7, 0.8, 0.9, 1.0, 0.9, 0.8, 0.7]  # 7-day weighting curve
        weighted_sum = sum(p * w for p, w in zip(prices[-7:], weights))
        predicted = weighted_sum / sum(weights)  # Normalize weighted sum

        # Calculate confidence (1 - coefficient of variation)
        confidence = 1 - (np.std(prices[-7:]) / np.mean(prices[-7:]))

        return {
            'predicted_price': round(predicted, 2),  # Rounded prediction
            'confidence': round(min(max(confidence, 0), 1), 2),  # Clamped 0-1
            'current_price': prices[-1]  # Most recent price
        }
