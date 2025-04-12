# analyzers/price_predictor.py
import numpy as np

class PricePredictor:
    def predict_next_week_prices(self, price_history: list) -> dict:
        prices = [h['price'] for h in price_history[-14:] if 'price' in h]

        if not prices:
            return {'predicted_price': 0.0, 'confidence': 0.0, 'current_price': 0.0}

        if len(prices) < 7:
            return {'predicted_price': prices[-1], 'confidence': 0, 'current_price': prices[-1]}

        weights = [0.7, 0.8, 0.9, 1.0, 0.9, 0.8, 0.7]
        weighted_sum = sum(p * w for p, w in zip(prices[-7:], weights))
        predicted = weighted_sum / sum(weights)

        confidence = 1 - (np.std(prices[-7:]) / np.mean(prices[-7:]))
        return {
            'predicted_price': round(predicted, 2),
            'confidence': round(min(max(confidence, 0), 1), 2),
            'current_price': prices[-1]
}

