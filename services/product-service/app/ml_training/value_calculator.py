# analyzers/value_calculator.py
class ValueCalculator:
    def calculate_value_score(self, product: dict) -> float:
        current_price = product['price']
        price_score = 1 / (1 + current_price)

        pred_score = self._get_prediction_score(product['prediction'])
        quality_score = self._get_quality_score(product)

        return round(0.6 * price_score + 0.3 * pred_score + 0.1 * quality_score, 2)

    def _get_prediction_score(self, prediction: dict) -> float:
        if prediction['current_price'] == 0:
           return 0
        price_trend = prediction['predicted_price'] / prediction['current_price']
        return round(prediction['confidence'] * (1 - price_trend), 2)

    def _get_quality_score(self, product: dict) -> float:
        if product.get('rating') is None:
            return 0.5
        return round(product['rating'] / 5, 2)
