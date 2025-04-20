final mockProduct = {
  'id': '1',
  'name': 'Test Product',
  'current_price': 2.99,
  'predicted_price': 3.10,
  'confidence': 0.85,
  'recommendation': 'Good time to buy',
  'image_url': 'https://example.com/image.jpg',
  'retailer': 'Test Retailer',
  'rating': 4.5,
  'unit_price': 0.99,
  'base_unit': 'kg'
};

final mockApiResponse = {
  'products': [mockProduct],
  'page': 1,
  'total_pages': 1,
  'total_items': 1
};