import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/product.dart';

class ApiService {
  static const String baseUrl = 'http://10.0.2.2:5003'; 
  
  // Added client as a class member to enable dependency injection for testing
  http.Client _client = http.Client();
  
  // Setter to allow replacing the client with a mock for testing
  set client(http.Client client) {
    _client = client;
  }

  Future<List<ProductGroup>> fetchGroupedProducts() async {
    final response = await _client.get(Uri.parse('$baseUrl/grouped-products'));
    
    if (response.statusCode == 200) {
      final List<dynamic> data = json.decode(response.body);
      return data.map((item) => ProductGroup.fromJson(item)).toList();
    } else {
      throw Exception('Failed to load grouped products');
    }
  }
  
  //price prediction  
  Future<Map<String, dynamic>> getPredictions({int page = 1, String? searchQuery}) async {
    final uri = Uri.parse('$baseUrl/products-prediction?page=$page')
      .replace(queryParameters: {
        'page': page.toString(),
        if (searchQuery != null && searchQuery.isNotEmpty) 'search': searchQuery,
      });
    
    final response = await _client.get(uri);
    
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Failed to load predictions');
    }
  }

  //product search
  Future<List<dynamic>> searchPredictions(String query) async {
    try {
      final response = await _client.get(
        Uri.parse('$baseUrl/products-prediction?search=$query'),
      );
      
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return data['products'] as List;
      }
      throw Exception('Failed to search predictions');
    } catch (e) {
      throw Exception('Search error: $e');
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