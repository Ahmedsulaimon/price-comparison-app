import 'dart:async';

import 'package:flutter/material.dart';
import 'package:frontend/services/api_service.dart';
import 'package:frontend/widgets/product_search_delegate.dart';

class PricePredictionPage extends StatefulWidget {
  const PricePredictionPage({super.key});

  @override
  State<PricePredictionPage> createState() => _PricePredictionPageState();
}

class _PricePredictionPageState extends State<PricePredictionPage> {
  final ApiService _apiService = ApiService();
  final ScrollController _scrollController = ScrollController();
  final TextEditingController _searchController = TextEditingController();
  final List<dynamic> _products = [];
  int _currentPage = 1;
  bool _isLoading = false;
  bool _hasMore = true;
  String _searchQuery = '';
  Timer? _searchDebounce;

  @override
  void initState() {
    super.initState();
    _loadPredictions();
    _scrollController.addListener(_scrollListener);
    _searchController.addListener(_onSearchChanged);
  }

  void _onSearchChanged() {
    if (_searchDebounce?.isActive ?? false) _searchDebounce?.cancel();
    
    _searchDebounce = Timer(const Duration(milliseconds: 500), () {
      if (_searchQuery != _searchController.text) {
        setState(() {
          _searchQuery = _searchController.text;
          _products.clear();
          _currentPage = 1;
          _hasMore = true;
          _loadPredictions();
        });
      }
    });
  }

  Future<void> _loadPredictions() async {
    if (_isLoading || !_hasMore) return;

    setState(() => _isLoading = true);
    
    try {
      final response = await _apiService.getPredictions(
        page: _currentPage,
        searchQuery: _searchQuery.isNotEmpty ? _searchQuery : null,
      );
      
      setState(() {
        _products.addAll(response['products']);
        _currentPage++;
        _hasMore = _currentPage <= response['total_pages'];
        _isLoading = false;
      });
    } catch (e) {
      setState(() => _isLoading = false);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error loading predictions: $e')),
        );
      }
    }
  }

  void _scrollListener() {
    if (_scrollController.position.pixels == 
        _scrollController.position.maxScrollExtent) {
      _loadPredictions();
    }
  }


  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Price Predictions'),
        actions: [
          IconButton(
            icon: const Icon(Icons.search),
            onPressed: () {
              showSearch(
                context: context,
                delegate: ProductSearchDelegate(_apiService),
              );
            },
          ),
        ],
      ),
      body: Column(
        children: [
            const Row(
                children: [
                  Icon(Icons.warning_amber, color: Colors.amber, size: 40),
                  SizedBox(width: 8),
                   Text("Predicted forecasts are estimates, not guarantees.",
             style: TextStyle(
              fontWeight: FontWeight.bold
              
             ),),
                ],),
          Padding(
            padding: const EdgeInsets.all(8.0),
            child: TextField(
              controller: _searchController,
              decoration: InputDecoration(
                hintText: 'Search products...',
                prefixIcon: const Icon(Icons.search),
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(8.0),
                ),
              ),
              onChanged: (value) {
                // Handled by the listener
              },
            ),
          ),
          
          Expanded(
            child: _products.isEmpty && !_isLoading
                ? const Center(child: Text('No predictions available'))
                : ListView.builder(
                    controller: _scrollController,
                    itemCount: _products.length + (_hasMore ? 1 : 0),
                    itemBuilder: (context, index) {
                      if (index >= _products.length) {
                        return const Center(child: Padding(
                          padding: EdgeInsets.all(16.0),
                          child: CircularProgressIndicator(),
                        ));
                      }
                      
                      final product = _products[index];
                      return _buildPredictionCard(product);
                    },
                  ),
          ),
        ],
      ),
    );
  }


  Widget _buildPredictionCard(Map<String, dynamic> product) {

     final confidence = product['confidence'] is int 
      ? (product['confidence'] as int).toDouble()
      : product['confidence'] as double;

    return Card(
      margin: const EdgeInsets.all(8.0),
      child: Padding(
        padding: const EdgeInsets.all(12.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                if (product['image_url'] != null)
                  Image.network(
                    product['image_url'],
                    width: 80,
                    height: 80,
                    fit: BoxFit.cover,
                  ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        product['name'],
                        style: const TextStyle(
                          fontWeight: FontWeight.bold,
                          fontSize: 16,
                        ),
                      ),
                      Text(product['retailer']),
                    ],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Current: £${product['current_price'].toStringAsFixed(2)}',
                      style: const TextStyle(fontSize: 14),
                    ),
                    Text(
                      'Next Week\'s Prediction: £${product['predicted_price'].toStringAsFixed(2)}',
                      style: TextStyle(
                        fontSize: 14,
                        color: _getPredictionColor(
                          product['predicted_price'],
                          product['current_price'],
                        ),
                      ),
                    ),
                    Text('Retailer: ${product['retailer']}', style: const TextStyle(
                      fontSize: 14,
                      fontWeight: FontWeight.bold,
                      color: Colors.grey
                      ),)
                  ],
                ),
                Chip(
                    label: Text('${(confidence * 100).toStringAsFixed(0)}%'),
                    backgroundColor: _getConfidenceColor(confidence),
                  ),
              ],
            ),
            const SizedBox(height: 8),
            Text(
              product['recommendation'],
              style: const TextStyle(fontStyle: FontStyle.italic),
            ),
            if (product['rating'] != null) ...[
              const SizedBox(height: 8),
              Row(
                children: [
                  const Icon(Icons.star, color: Colors.amber, size: 16),
                  Text(product['rating'].toStringAsFixed(1)),
                ],
              ),
            ],
          ],
        ),
      ),
    );
  }

  Color _getPredictionColor(double predicted, double current) {
    final difference = predicted - current;
    if (difference > 0.05) return Colors.red;
    if (difference < -0.05) return Colors.green;
    return Colors.blue;
  }

  Color _getConfidenceColor(double confidence) {
  if (confidence > 0.8) return Colors.green.shade200;
  if (confidence > 0.5) return Colors.blue.shade200;
  return Colors.orange.shade200;
}

   @override
  void dispose() {
    _searchDebounce?.cancel();
    _searchController.dispose();
    _scrollController.dispose();
    super.dispose();
  }

}