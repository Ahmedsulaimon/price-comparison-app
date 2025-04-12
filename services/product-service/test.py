# # import re


    



# import numpy as np
# import pandas as pd
# from datetime import datetime, timedelta
# from faker import Faker
# import psycopg2
# import random
# import math

# # Configuration
# DB_CONFIG = {
#     'dbname': 'your_dbname',
#     'user': 'your_user',
#     'password': 'your_password',
#     'host': 'localhost'
# }

# NUM_PRODUCTS = 100  # Number of products to generate history for
# START_DATE = datetime(2023, 1, 1)
# END_DATE = datetime(2024, 1, 1)
# FLUCTUATION_RANGE = 0.2  # ±20% price fluctuation

# def generate_price_pattern(base_price, start_date, end_date):
#     """Generate realistic price fluctuations with seasonal patterns"""
#     dates = pd.date_range(start_date, end_date, freq='D')
#     days = (end_date - start_date).days
#     x = np.linspace(0, 4 * math.pi, days)
    
#     # Base components
#     seasonal = np.sin(x) * 0.1  # Seasonal variation
#     trend = np.linspace(0, 0.05, days)  # Gradual price increase
#     noise = np.random.normal(0, 0.02, days)  # Random noise
    
#     # Special events (sales)
#     sale_days = random.sample(range(days), 5)
#     sale_effect = np.zeros(days)
#     for day in sale_days:
#         sale_duration = random.randint(3, 7)
#         sale_effect[day:day+sale_duration] = -0.15  # 15% discount
    
#     combined = base_price * (1 + seasonal + trend + noise + sale_effect)
#     return pd.Series(combined, index=dates)

# def generate_unit_price(price, size_description):
#     """Generate realistic unit prices based on product size"""
#     if not size_description:
#         return None
    
#     # Extract numeric quantity from size description
#     try:
#         quantity = float(''.join(filter(str.isdigit, size_description.split()[0])))
#         return round(price / quantity, 2)
#     except:
#         return None

# def insert_price_history(product_id, prices):
#     """Insert generated prices into database"""
#     conn = psycopg2.connect(**DB_CONFIG)
#     cur = conn.cursor()
    
#     try:
#         for date, price in prices.items():
#             cur.execute("""
#                 INSERT INTO price_history 
#                 (product_id, price, valid_from, scraped_at)
#                 VALUES (%s, %s, %s, %s)
#                 """, (
#                     product_id,
#                     round(float(price), 2),
#                     date,
#                     date + timedelta(hours=12)  # Simulate daily scrape time
#                 ))
#         conn.commit()
#     finally:
#         cur.close()
#         conn.close()

# def main():
#     fake = Faker()
    
#     # Get products from database
#     conn = psycopg2.connect(**DB_CONFIG)
#     products = pd.read_sql("""
#         SELECT product_id, current_price, size_description 
#         FROM products 
#         LIMIT %s
#         """, conn, params=(NUM_PRODUCTS,))
#     conn.close()

#     # Generate price history for each product
#     for _, product in products.iterrows():
#         print(f"Generating history for {product['product_id']}")
#         prices = generate_price_pattern(
#             product['current_price'], 
#             START_DATE, 
#             END_DATE
#         )
        
#         # Add unit price calculations
#         prices = prices.apply(
#             lambda p: (p, generate_unit_price(p, product['size_description'])))
        
#         insert_price_history(product['product_id'], prices)

# if __name__ == "__main__":
#     main()