import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/product.dart';

class ApiService {
  static const String baseUrl = 'http://10.0.2.2:5003'; // Update with your gateway's IP if on device

  Future<List<ProductGroup>> fetchGroupedProducts() async {
    final response = await http.get(Uri.parse('$baseUrl/grouped-products'));

    if (response.statusCode == 200) {
      final List<dynamic> data = json.decode(response.body);
      return data.map((item) => ProductGroup.fromJson(item)).toList();
    } else {
      throw Exception('Failed to load grouped products');
    }
  }
}

class ProductGroup {
  final String keyword;
  final Product recommended;
  final List<Product> others;

  ProductGroup({required this.keyword, required this.recommended, required this.others});

  factory ProductGroup.fromJson(Map<String, dynamic> json) {
    return ProductGroup(
      keyword: json['keyword'] as String,
      recommended: Product.fromJson(json['recommended']),
      others: (json['others'] as List)
          .map((item) => Product.fromJson(item))
          .toList(),
    );
  }
}
