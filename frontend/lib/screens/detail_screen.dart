import 'package:flutter/material.dart';

import 'package:url_launcher/url_launcher.dart';

import '../models/product.dart';
import '../services/api_service.dart';

class DetailScreen extends StatefulWidget {
  final ProductGroup productGroup;

   const DetailScreen({
    super.key,
    required this.productGroup,
  });

  @override
  State<DetailScreen> createState() => _DetailScreenState();
}

class _DetailScreenState extends State<DetailScreen> {
 String? _filter;
 
 Future<void> _launchURL(String url) async {
  final Uri uri = Uri.parse(url);
  if (!await launchUrl( uri,
        mode: LaunchMode.externalApplication,)) {
    throw 'Could not launch $url';
  }
}

 List<Product> get _filteredProducts {
    if (_filter == 'best_rated') {
      return widget.productGroup.others
          .where((p) => p.rating != null)
          .toList()
          ..sort((a, b) => (b.rating ?? 0).compareTo(a.rating ?? 0));
    }
    return widget.productGroup.others;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
           
        title: Text(widget.productGroup.keyword, style: const TextStyle(
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
                onTap: () => _launchURL(widget.productGroup.recommended.url),
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
                          child: widget.productGroup.recommended.imageUrl.isNotEmpty
                              ? Image.network(
                                  widget.productGroup.recommended.imageUrl,
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
                              widget.productGroup.recommended.name,
                              style: Theme.of(context).textTheme.titleLarge,
                            ),
                            const SizedBox(height: 8),
                            Row(
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              children: [
                                Text(
                                  '£${widget.productGroup.recommended.price.toStringAsFixed(2)}',
                                  style: const TextStyle(
                                    fontSize: 20,
                                    fontWeight: FontWeight.bold,
                                  ),
                                ),
                                if (widget.productGroup.recommended.rating != null)
                                  Row(
                                    children: [
                                      const Icon(Icons.star, color: Colors.amber, size: 20),
                                      const SizedBox(width: 4),
                                      Text(widget.productGroup.recommended.rating!.toStringAsFixed(1)),
                                    ],
                                  ),
                              ],
                            ),
                            if (widget.productGroup.recommended.unitPrice != null)
                              Padding(
                                padding: const EdgeInsets.only(top: 4),
                                child: Text(
                                  'Unit price: £${widget.productGroup.recommended.unitPrice!.toStringAsFixed(2)}/${widget.productGroup.recommended.baseUnit ?? 'unit'}',
                                  style: TextStyle(
                                    color: Colors.grey[600],
                                    fontSize: 14,
                                  ),
                                ),
                              ),
                              const SizedBox(height: 8),
                                Text(
                              widget.productGroup.recommended.retailer,
                              style: const TextStyle(
                                color: Colors.grey,
                                fontWeight: FontWeight.bold
                              )
                            ),

                            const SizedBox(height: 16),
                            SizedBox(
                              width: double.infinity,
                              child: ElevatedButton(
                                onPressed: () => _launchURL(widget.productGroup.recommended.url),
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
             
            // // Filterable Other Products Section
            Padding(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('Other Options', style: Theme.of(context).textTheme.titleMedium),
                  const SizedBox(height: 8),
                  SingleChildScrollView(
                    scrollDirection: Axis.horizontal,
                    child: Row(
                      children: [
                        FilterChip(
                          label: const Text('All'),
                          selected: _filter == null,
                          onSelected: (_) => setState(() => _filter = null),
                        ),
                        const SizedBox(width: 8),
                        FilterChip(
                          label: const Text('Best Rated'),
                          selected: _filter == 'best_rated',
                          onSelected: (_) => setState(() => _filter = 'best_rated'),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),

            // Products Grid
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
              itemCount: _filteredProducts.length,
              itemBuilder: (context, index) {
                final product = _filteredProducts[index];
                return GestureDetector(
                  onTap: () => _launchURL(product.url),
                  child: Card(
                    elevation: 2,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Stack(
                      children: [
                        Column(
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

                             Expanded(child: Padding(
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
                                
                                  Text(
                                    '£${product.price.toStringAsFixed(2)}',
                                    style: const TextStyle(fontSize: 16),
                                  ),
                                  if (product.unitPrice != null)
                                    Text(
                                      '£${product.unitPrice!.toStringAsFixed(2)}/${product.baseUnit ?? 'unit'}',
                                      style: TextStyle(
                                        color: Colors.grey[600],
                                        fontSize: 10,
                                        fontWeight: FontWeight.bold
                                      ),
                                    ),
                                 
                                  Text(
                                    product.retailer,
                                    style: TextStyle(
                                      color: Colors.grey[600],
                                      fontSize: 12,
                                      fontWeight: FontWeight.bold
                                    ),
                                  ),
                                ],
                            ), ),)
                          ],
                        ),
                        if (product.rating != null && product.rating! >= 4.0)
                          Positioned(
                            top: 8,
                            left: 8,
                            child: Container(
                              padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                              decoration: BoxDecoration(
                                color: Colors.amber[700],
                                borderRadius: BorderRadius.circular(12),
                              ),
                              child: Row(
                                mainAxisSize: MainAxisSize.min,
                                children: [
                                  const Icon(Icons.star, color: Colors.white, size: 14),
                                  const SizedBox(width: 2),
                                  Text(
                                    product.rating!.toStringAsFixed(1),
                                    style: const TextStyle(
                                      color: Colors.white,
                                      fontSize: 12,
                                      fontWeight: FontWeight.bold,
                                    ),
                                  ),
                                ],
                              ),
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