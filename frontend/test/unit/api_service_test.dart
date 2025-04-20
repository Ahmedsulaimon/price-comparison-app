import 'dart:convert';

import 'package:flutter_test/flutter_test.dart';
import 'package:http/testing.dart';
import 'package:mockito/annotations.dart';
import 'package:mockito/mockito.dart';
import 'package:http/http.dart' as http;
import 'package:frontend/services/api_service.dart';
//import 'package:frontend/models/product.dart';


// This creates a mock class of http.Client
@GenerateMocks([http.Client])
//import 'api_service_test.mocks.dart'; // This file will be generated

void main() {
  group('ApiService', () {
    late ApiService apiService;
    late MockClient mockClient;
    
    setUp(() {
      // Use the generated MockClient from mockito instead of http's MockClient
      mockClient = MockClient as MockClient;
      apiService = ApiService();
      apiService.client = mockClient;
    });

    group('fetchGroupedProducts', () {
      test('returns a list of ProductGroup when API call succeeds', () async {
        // Arrange
        final responseData = [
          {
            'keyword': 'milk',
            'recommended': {
              'id': '1',
              'name': 'Whole Milk',
              'price': 1.99,
              'image_url': 'http://example.com/milk.jpg',
              'store': 'Tesco'
            },
            'others': [
              {
                'id': '2',
                'name': 'Semi-Skimmed Milk',
                'price': 1.89,
                'image_url': 'http://example.com/semi-milk.jpg',
                'store': 'Asda'
              }
            ]
          }
        ];

        when(mockClient.get(Uri.parse('${ApiService.baseUrl}/grouped-products')))
            .thenAnswer((_) async => http.Response(json.encode(responseData), 200));

        // Act
        final result = await apiService.fetchGroupedProducts();

        // Assert
        expect(result, isA<List<ProductGroup>>());
        expect(result.length, 1);
        expect(result[0].keyword, 'milk');
        expect(result[0].recommended.name, 'Whole Milk');
        expect(result[0].others.length, 1);
      });

      test('throws an exception when API call fails', () async {
        // Arrange
        when(mockClient.get(Uri.parse('${ApiService.baseUrl}/grouped-products')))
            .thenAnswer((_) async => http.Response('Not found', 404));

        // Act & Assert
        expect(apiService.fetchGroupedProducts(), throwsException);
      });
    });

    group('getPredictions', () {
      test('returns predictions with default parameters', () async {
        // Arrange
        final responseData = {
          'products': [
            {
              'id': '1',
              'name': 'Product 1',
              'price': 2.99
            }
          ],
          'total_pages': 5,
          'current_page': 1
        };

        when(mockClient.get(Uri.parse('${ApiService.baseUrl}/products-prediction?page=1')))
            .thenAnswer((_) async => http.Response(json.encode(responseData), 200));

        // Act
        final result = await apiService.getPredictions();

        // Assert
        expect(result, isA<Map<String, dynamic>>());
        expect(result['products'], isA<List>());
        expect(result['total_pages'], 5);
        expect(result['current_page'], 1);
      });

      test('returns predictions with search query', () async {
        // Arrange
        final responseData = {
          'products': [
            {
              'id': '1',
              'name': 'Milk',
              'price': 2.99
            }
          ],
          'total_pages': 1,
          'current_page': 1
        };

        final uri = Uri.parse('${ApiService.baseUrl}/products-prediction?page=1')
            .replace(queryParameters: {
              'page': '1',
              'search': 'milk',
            });

        when(mockClient.get(uri))
            .thenAnswer((_) async => http.Response(json.encode(responseData), 200));

        // Act
        final result = await apiService.getPredictions(searchQuery: 'milk');

        // Assert
        expect(result, isA<Map<String, dynamic>>());
        expect(result['products'], isA<List>());
        expect((result['products'] as List).length, 1);
        expect((result['products'] as List)[0]['name'], 'Milk');
      });

      test('throws an exception when API call fails', () async {
        // Arrange
        when(mockClient.get(Uri.parse('${ApiService.baseUrl}/products-prediction?page=1')))
            .thenAnswer((_) async => http.Response('Server error', 500));

        // Act & Assert
        expect(apiService.getPredictions(), throwsException);
      });
    });

    group('searchPredictions', () {
      test('returns search results when API call succeeds', () async {
        // Arrange
        final responseData = {
          'products': [
            {
              'id': '1',
              'name': 'Bread',
              'price': 1.49
            },
            {
              'id': '2',
              'name': 'Bread Rolls',
              'price': 1.29
            }
          ],
          'total_pages': 1,
          'current_page': 1
        };

        when(mockClient.get(Uri.parse('${ApiService.baseUrl}/products-prediction?search=bread')))
            .thenAnswer((_) async => http.Response(json.encode(responseData), 200));

        // Act
        final result = await apiService.searchPredictions('bread');

        // Assert
        expect(result, isA<List>());
        expect(result.length, 2);
        expect(result[0]['name'], 'Bread');
        expect(result[1]['name'], 'Bread Rolls');
      });

      test('throws an exception when API call fails', () async {
        // Arrange
        when(mockClient.get(Uri.parse('${ApiService.baseUrl}/products-prediction?search=error')))
            .thenAnswer((_) async => http.Response('Not found', 404));

        // Act & Assert
        expect(apiService.searchPredictions('error'), throwsException);
      });
    });
  });
}