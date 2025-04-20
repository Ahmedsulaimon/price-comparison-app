import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:frontend/main.dart';
import 'package:frontend/screens/price_prediction_screen.dart';

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  group('Price Prediction Flow', () {
    testWidgets('Load and display predictions', (tester) async {
      // Start app
      await tester.pumpWidget(const MyApp());

      // Navigate to predictions page
      await tester.tap(find.text('Price Predictions'));
      await tester.pumpAndSettle();

      // Verify initial loading
      expect(find.byType(CircularProgressIndicator), findsOneWidget);
      await tester.pumpAndSettle(const Duration(seconds: 2));

      // Verify predictions are displayed
      expect(find.byType(PricePredictionPage), findsWidgets);
    });

    testWidgets('Search functionality works', (tester) async {
      await tester.pumpWidget(const MyApp());
      await tester.tap(find.text('Price Predictions'));
      await tester.pumpAndSettle();

      // Enter search query
      await tester.enterText(find.byType(TextField), 'Milk');
      await tester.pumpAndSettle(const Duration(milliseconds: 600));

      // Verify filtered results
      expect(find.textContaining('Milk', findRichText: true), findsWidgets);
    });
  });
}