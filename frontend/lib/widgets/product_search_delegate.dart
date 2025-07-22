import 'package:flutter/material.dart';
import '../services/api_service.dart';

class ProductSearchDelegate extends SearchDelegate {
  final ApiService apiService;

  ProductSearchDelegate(this.apiService);

  @override
  List<Widget> buildActions(BuildContext context) {
    return [
      IconButton(
        icon: const Icon(Icons.clear),
        onPressed: () {
          query = '';
        },
      ),
    ];
  }

  @override
  Widget buildLeading(BuildContext context) {
    return IconButton(
      icon: const Icon(Icons.arrow_back),
      onPressed: () {
        close(context, null);
      },
    );
  }

  @override
  Widget buildResults(BuildContext context) {
    return FutureBuilder<List<dynamic>>(
      future: apiService.searchPredictions(query),
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting) {
          return const Center(child: CircularProgressIndicator());
        } else if (snapshot.hasError) {
          return Center(child: Text('Error: ${snapshot.error}'));
        } else if (!snapshot.hasData || snapshot.data!.isEmpty) {
          return const Center(child: Text('No products found'));
        }

        return ListView.builder(
          itemCount: snapshot.data!.length,
          itemBuilder: (context, index) {
            final product = snapshot.data![index];
            return _buildProductCard(product);
          },
        );
      },
    );
  }

  @override
  Widget buildSuggestions(BuildContext context) {
    return buildResults(context);
  }

   Widget _buildProductCard(Map<String, dynamic> product) {
    final confidence = (product['confidence'] as num).toDouble();
    
    return Card(
      margin: const EdgeInsets.all(8.0),
      child: ListTile(
        leading: product['image_url'] != null
            ? Image.network(
                product['image_url'], 
                width: 50, 
                height: 50,
                fit: BoxFit.cover,
              )
            : const Icon(Icons.shopping_basket, size: 50),
        title: Text(product['name']),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('£${product['current_price'].toStringAsFixed(2)}'),
            Text(
              'Predicted: £${product['predicted_price'].toStringAsFixed(2)}',
              style: TextStyle(
                color: _getPredictionColor(
                  product['predicted_price'],
                  product['current_price'],
                ),
              ),
            ),
          ],
        ),
        trailing: Chip(
          label: Text('${(confidence * 100).toStringAsFixed(0)}%'),
          backgroundColor: _getConfidenceColor(confidence),
        ),
        onTap: () {
          // You can add navigation to detailed view here if needed
        },
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
}