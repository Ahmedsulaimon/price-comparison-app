
class Product {
  final String id;
  final String name;
  final String retailer;
  final double price;
  final double? rating;
  final double? unitPrice;
  final String? baseUnit;
  final String imageUrl;
  final String url;
  final String? badge;

  Product({
    required this.id,
    required this.name,
    required this.retailer,
    required this.price,
    this.rating,
    this.unitPrice,
    this.baseUnit,
    required this.imageUrl,
    required this.url,
    this.badge,
  });



  factory Product.fromJson(Map<String, dynamic> json) {
    return Product(
      id: json['id']?.toString() ?? '', // Handle potential null
      name: json['name']?.toString() ?? 'No name',
      retailer: json['retailer']?.toString() ?? 'Unknown retailer',
      price: (json['price'] as num?)?.toDouble() ?? 0.0,
      rating: (json['rating'] as num?)?.toDouble(),
      unitPrice: (json['unit_price'] as num?)?.toDouble(),
      baseUnit: json['base_unit']?.toString(),
      imageUrl: json['image_url']?.toString() ?? '',
      url: json['url']?.toString() ?? '',
      badge: json['badge']?.toString(),
    );
  }
}