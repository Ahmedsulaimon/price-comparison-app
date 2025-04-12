import 'package:flutter/material.dart';
import 'package:frontend/screens/detail_screen.dart';
import 'package:frontend/screens/price_prediction_screen.dart';
import 'package:frontend/services/api_service.dart';
import 'package:frontend/widgets/persistent_app_bar.dart';


class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  late Future<List<ProductGroup>> futureGroups;
  int _currentIndex = 0;

  @override
  void initState() {
    super.initState();
    futureGroups = ApiService().fetchGroupedProducts();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      
      appBar: PersistentAppBar(
        title: 'Fresh Groceries',
        currentIndex: _currentIndex,
        onTabTapped: _onTabTapped,
      ),
      body: _buildCurrentPage(),
    );
  }

  Widget _buildCurrentPage() {
    if (_currentIndex == 1) {
      return const PricePredictionPage();
    }

    return FutureBuilder<List<ProductGroup>>(
      future: futureGroups,
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting) {
          return const Center(child: CircularProgressIndicator());
        } else if (snapshot.hasError) {
          return Center(child: Text('Error: ${snapshot.error}'));
        } else if (!snapshot.hasData || snapshot.data!.isEmpty) {
          return const Center(child: Text('No products found'));
        }

        final groups = snapshot.data!;
        final products = groups.map((g) => g.recommended).toList();

        return GridView.builder(
          padding: const EdgeInsets.all(8),
          gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
            crossAxisCount: 2,
            crossAxisSpacing: 8,
            mainAxisSpacing: 8,
            childAspectRatio: 0.7,
          ),
          itemCount: products.length,
          itemBuilder: (context, index) {
            final product = products[index];
            return GestureDetector(
              onTap: () => Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (context) => DetailScreen(productGroup: groups[index]),
                ),
              ),
              child: Card(
                elevation: 2,
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Expanded(
                      child: ClipRRect(
                        borderRadius: const BorderRadius.vertical(top: Radius.circular(12)),
                        child: product.imageUrl.isNotEmpty
                            ? Image.network(product.imageUrl, fit: BoxFit.cover, width: double.infinity)
                            : Container(color: Colors.grey[300], child: const Center(child: Icon(Icons.image)))
                      ),
                    ),
                    Padding(
                      padding: const EdgeInsets.all(8.0),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(product.name, maxLines: 2, overflow: TextOverflow.ellipsis, style: const TextStyle(fontWeight: FontWeight.bold)),
                          const SizedBox(height: 4),
                          Text('£${product.price.toStringAsFixed(2)}'),
                          if (product.unitPrice != null)
                            Text('Unit: £${product.unitPrice!.toStringAsFixed(2)}'),
                          if (product.rating != null)
                            Row(
                              children: [
                                const Icon(Icons.star, size: 14, color: Colors.amber),
                                Text(product.rating!.toStringAsFixed(1))
                              ],
                            ),
                          Text(product.retailer, style: const TextStyle(fontSize: 12, color: Colors.grey)),
                        ],
                      ),
                    )
                  ],
                ),
              ),
            );
          },
        );
      },
    );
  }

  void _onTabTapped(int index) {
    setState(() {
      _currentIndex = index;
    });
  }
}