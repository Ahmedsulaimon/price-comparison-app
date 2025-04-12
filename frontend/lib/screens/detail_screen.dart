import 'package:flutter/material.dart';

import 'package:url_launcher/url_launcher.dart';

import '../services/api_service.dart';

class DetailScreen extends StatelessWidget {
  final ProductGroup productGroup;

   const DetailScreen({
    super.key,
    required this.productGroup,
  });
  
 Future<void> _launchURL(String url) async {
  final Uri uri = Uri.parse(url);
  if (!await launchUrl( uri,
        mode: LaunchMode.externalApplication,)) {
    throw 'Could not launch $url';
  }
}

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
           
        title: Text(productGroup.keyword, style: const TextStyle(
            color: Colors.white,
            fontWeight: FontWeight.bold

        )),
           centerTitle: true,
           backgroundColor: Colors.blueAccent,
      ),
      body: SingleChildScrollView(
        child: Column(
          children: [
            // Recommended Product (Full Width)
            Padding(
              padding: const EdgeInsets.all(16.0),
              child: GestureDetector(
                onTap: () => _launchURL(productGroup.recommended.url),
                child: Card(
                  elevation: 4,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      AspectRatio(
                        aspectRatio: 16/9,
                        child: ClipRRect(
                          borderRadius: const BorderRadius.vertical(top: Radius.circular(12)),
                          child: productGroup.recommended.imageUrl.isNotEmpty
                              ? Image.network(
                                  productGroup.recommended.imageUrl,
                                  fit: BoxFit.cover,
                                  width: double.infinity,
                                )
                              : Container(
                                  color: Colors.grey[200],
                                  child: const Center(child: Icon(Icons.image, size: 50)),
                                ),
                        ),
                      ),
                      Padding(
                        padding: const EdgeInsets.all(16.0),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              productGroup.recommended.name,
                              style: Theme.of(context).textTheme.titleLarge,
                            ),
                            const SizedBox(height: 8),
                            Row(
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              children: [
                                Text(
                                  '£${productGroup.recommended.price.toStringAsFixed(2)}',
                                  style: const TextStyle(
                                    fontSize: 20,
                                    fontWeight: FontWeight.bold,
                                  ),
                                ),
                                if (productGroup.recommended.rating != null)
                                  Row(
                                    children: [
                                      const Icon(Icons.star, color: Colors.amber, size: 20),
                                      const SizedBox(width: 4),
                                      Text(productGroup.recommended.rating!.toStringAsFixed(1)),
                                    ],
                                  ),
                              ],
                            ),
                            if (productGroup.recommended.unitPrice != null)
                              Padding(
                                padding: const EdgeInsets.only(top: 4),
                                child: Text(
                                  'Unit price: £${productGroup.recommended.unitPrice!.toStringAsFixed(2)}/${productGroup.recommended.baseUnit ?? 'unit'}',
                                  style: TextStyle(
                                    color: Colors.grey[600],
                                    fontSize: 14,
                                  ),
                                ),
                              ),
                            const SizedBox(height: 16),
                            SizedBox(
                              width: double.infinity,
                              child: ElevatedButton(
                                onPressed: () => _launchURL(productGroup.recommended.url),
                                child: const Text('View on Retailer Site'),
                              ),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),

            // Other Products Grid
            Padding(
              padding: const EdgeInsets.all(16.0),
              child: Text(
                'Other Options',
                style: Theme.of(context).textTheme.titleMedium,
              ),
            ),
            GridView.builder(
              physics: const NeverScrollableScrollPhysics(),
              shrinkWrap: true,
              padding: const EdgeInsets.symmetric(horizontal: 16),
              gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                crossAxisCount: 2,
                crossAxisSpacing: 16,
                mainAxisSpacing: 16,
                childAspectRatio: 0.7,
              ),
              itemCount: productGroup.others.length,
              itemBuilder: (context, index) {
                final product = productGroup.others[index];
                return GestureDetector(
                  onTap: () => _launchURL(product.url),
                  child: Card(
                    elevation: 2,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Expanded(
                          child: ClipRRect(
                            borderRadius: const BorderRadius.vertical(top: Radius.circular(12)),
                            child: product.imageUrl.isNotEmpty
                                ? Image.network(
                                    product.imageUrl,
                                    fit: BoxFit.cover,
                                    width: double.infinity,
                                  )
                                : Container(
                                    color: Colors.grey[200],
                                    child: const Center(child: Icon(Icons.image)),
                                  ),
                          ),
                        ),
                        Padding(
                          padding: const EdgeInsets.all(12.0),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                product.name,
                                maxLines: 2,
                                overflow: TextOverflow.ellipsis,
                                style: const TextStyle(fontWeight: FontWeight.bold),
                              ),
                              const SizedBox(height: 4),
                              Text(
                                '£${product.price.toStringAsFixed(2)}',
                                style: const TextStyle(fontSize: 16),
                              ),
                              if (product.unitPrice != null)
                                Text(
                                  '£${product.unitPrice!.toStringAsFixed(2)}/${product.baseUnit ?? 'unit'}',
                                  style: TextStyle(
                                    color: Colors.grey[600],
                                    fontSize: 12,
                                  ),
                                ),
                              const SizedBox(height: 4),
                              Text(
                                product.retailer,
                                style: TextStyle(
                                  color: Colors.grey[600],
                                  fontSize: 12,
                                ),
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                  ),
                );
              },
            ),
          ],
        ),
      ),
    );
  }
}