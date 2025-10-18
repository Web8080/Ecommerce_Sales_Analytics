"""
Synthetic E-Commerce Data Generator
Generates realistic e-commerce data with:
- 50,000+ customers
- 1,000+ products
- 500,000+ transactions
- Realistic patterns (seasonality, customer behavior, missing data)
"""

import pandas as pd
import numpy as np
from faker import Faker
from datetime import datetime, timedelta
import random
from pathlib import Path
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))
from config import DATA_CONFIG, PATHS, PRODUCT_CATEGORIES, PAYMENT_METHODS, COUNTRIES

# Initialize
fake = Faker()
Faker.seed(42)
np.random.seed(42)
random.seed(42)

print(" Starting E-Commerce Data Generation...")
print(f"Target: {DATA_CONFIG['num_customers']:,} customers, {DATA_CONFIG['num_products']:,} products, {DATA_CONFIG['num_transactions']:,} transactions\n")


def generate_customers(n=50000):
    """Generate customer data with realistic attributes"""
    print(f" Generating {n:,} customers...")
    
    customers = []
    for i in range(n):
        # Create customer segments (VIP, Regular, Occasional)
        segment = np.random.choice(['VIP', 'Regular', 'Occasional'], p=[0.05, 0.45, 0.50])
        
        customer = {
            'customer_id': f'CUST{i+1:06d}',
            'first_name': fake.first_name(),
            'last_name': fake.last_name(),
            'email': fake.email(),
            'phone': fake.phone_number() if random.random() > 0.10 else None,  # 10% missing
            'registration_date': fake.date_between(start_date='-3y', end_date='-1y'),
            'country': np.random.choice(COUNTRIES, p=[0.45, 0.15, 0.10, 0.08, 0.07, 0.06, 0.05, 0.04]),
            'state': fake.state() if random.random() > 0.05 else None,  # 5% missing
            'city': fake.city(),
            'zip_code': fake.zipcode() if random.random() > 0.08 else None,  # 8% missing
            'customer_segment': segment,
            'age': int(np.random.normal(38, 12)),
            'gender': np.random.choice(['Male', 'Female', 'Other'], p=[0.48, 0.48, 0.04])
        }
        customers.append(customer)
        
        if (i + 1) % 10000 == 0:
            print(f"   Generated {i+1:,} customers")
    
    df = pd.DataFrame(customers)
    
    # Save to CSV
    output_path = PATHS['data_raw'] / 'customers.csv'
    df.to_csv(output_path, index=False)
    print(f" Saved to {output_path}\n")
    
    return df


def generate_products(n=1000):
    """Generate product catalog with categories and pricing"""
    print(f" Generating {n:,} products...")
    
    products = []
    for i in range(n):
        category = np.random.choice(PRODUCT_CATEGORIES)
        
        # Category-based pricing
        price_ranges = {
            'Electronics': (50, 2000),
            'Clothing': (15, 300),
            'Home & Garden': (20, 500),
            'Sports & Outdoors': (25, 800),
            'Books & Media': (10, 100),
            'Toys & Games': (15, 200),
            'Beauty & Health': (10, 150),
            'Food & Beverages': (5, 80),
            'Automotive': (30, 1500),
            'Office Supplies': (5, 300)
        }
        
        min_price, max_price = price_ranges[category]
        base_price = round(np.random.uniform(min_price, max_price), 2)
        
        product = {
            'product_id': f'PROD{i+1:05d}',
            'product_name': fake.catch_phrase()[:50],
            'category': category,
            'subcategory': fake.word().capitalize(),
            'brand': fake.company()[:30] if random.random() > 0.05 else None,  # 5% missing
            'price': base_price,
            'cost': round(base_price * np.random.uniform(0.4, 0.7), 2),  # 30-60% margin
            'weight_kg': round(np.random.uniform(0.1, 20), 2),
            'stock_quantity': int(np.random.uniform(0, 1000)),
            'rating': round(np.random.uniform(3.0, 5.0), 1) if random.random() > 0.10 else None,  # 10% missing
            'num_reviews': int(np.random.exponential(50)),
            'launch_date': fake.date_between(start_date='-5y', end_date='today')
        }
        products.append(product)
        
        if (i + 1) % 200 == 0:
            print(f"   Generated {i+1:,} products")
    
    df = pd.DataFrame(products)
    
    # Save to CSV
    output_path = PATHS['data_raw'] / 'products.csv'
    df.to_csv(output_path, index=False)
    print(f" Saved to {output_path}\n")
    
    return df


def generate_transactions(customers_df, products_df, n=500000):
    """Generate transaction data with realistic patterns"""
    print(f" Generating {n:,} transactions...")
    
    start_date = datetime.strptime(DATA_CONFIG['start_date'], '%Y-%m-%d')
    end_date = datetime.strptime(DATA_CONFIG['end_date'], '%Y-%m-%d')
    
    transactions = []
    
    # Customer behavior patterns
    customer_behavior = {
        'VIP': {'transaction_prob': 0.30, 'avg_items': 3, 'discount_prob': 0.15},
        'Regular': {'transaction_prob': 0.15, 'avg_items': 2, 'discount_prob': 0.08},
        'Occasional': {'transaction_prob': 0.05, 'avg_items': 1.5, 'discount_prob': 0.05}
    }
    
    transaction_id = 1
    
    # Generate transactions with realistic timing
    for _, customer in customers_df.iterrows():
        segment = customer['customer_segment']
        behavior = customer_behavior[segment]
        
        # Customer registration date is their first possible purchase
        customer_start = max(customer['registration_date'], start_date.date())
        
        # Number of transactions for this customer
        days_active = (end_date.date() - customer_start).days
        if days_active <= 0:
            continue
            
        num_transactions = int(np.random.poisson(days_active * behavior['transaction_prob'] / 30))
        
        if num_transactions == 0:
            continue
        
        # Generate transactions for this customer
        for _ in range(num_transactions):
            # Random transaction date
            random_days = random.randint(0, days_active)
            transaction_date = customer_start + timedelta(days=random_days)
            
            # Add seasonality (more sales in Nov-Dec, less in Jan-Feb)
            month = transaction_date.month
            if month in [11, 12]:  # Holiday season
                if random.random() > 0.3:  # Skip 30% to create spike
                    transaction_date = transaction_date
                else:
                    continue
            elif month in [1, 2]:  # Post-holiday slump
                if random.random() > 0.7:  # Skip 30% to create dip
                    continue
            
            # Number of items in this transaction
            num_items = max(1, int(np.random.poisson(behavior['avg_items'])))
            
            # Select products
            selected_products = products_df.sample(n=min(num_items, len(products_df)))
            
            for _, product in selected_products.iterrows():
                quantity = int(np.random.poisson(1.5)) + 1  # At least 1
                unit_price = product['price']
                
                # Apply discount randomly
                discount_pct = 0
                if random.random() < behavior['discount_prob']:
                    discount_pct = np.random.choice([5, 10, 15, 20, 25], p=[0.4, 0.3, 0.15, 0.10, 0.05])
                
                subtotal = unit_price * quantity
                discount_amount = round(subtotal * discount_pct / 100, 2)
                
                # Shipping
                shipping_cost = 0 if subtotal > 50 else round(np.random.uniform(5, 15), 2)
                
                # Tax (8%)
                tax_amount = round((subtotal - discount_amount) * 0.08, 2)
                
                total_amount = round(subtotal - discount_amount + shipping_cost + tax_amount, 2)
                
                transaction = {
                    'transaction_id': f'TXN{transaction_id:08d}',
                    'customer_id': customer['customer_id'],
                    'product_id': product['product_id'],
                    'transaction_date': transaction_date,
                    'quantity': quantity,
                    'unit_price': unit_price,
                    'discount_percent': discount_pct,
                    'discount_amount': discount_amount,
                    'subtotal': subtotal,
                    'tax_amount': tax_amount,
                    'shipping_cost': shipping_cost,
                    'total_amount': total_amount,
                    'payment_method': np.random.choice(PAYMENT_METHODS, p=[0.40, 0.25, 0.20, 0.10, 0.05]),
                    'order_status': np.random.choice(['Completed', 'Pending', 'Cancelled', 'Returned'], 
                                                     p=[0.90, 0.03, 0.03, 0.04]),
                    'shipping_address': fake.address().replace('\n', ', ') if random.random() > 0.02 else None,  # 2% missing
                    'order_notes': fake.sentence() if random.random() < 0.05 else None  # 5% have notes
                }
                
                transactions.append(transaction)
                transaction_id += 1
                
                if transaction_id % 50000 == 0:
                    print(f"   Generated {transaction_id:,} transactions")
                
                if transaction_id > n:
                    break
            
            if transaction_id > n:
                break
        
        if transaction_id > n:
            break
    
    df = pd.DataFrame(transactions)
    
    # Introduce additional missing values (realistic data quality issues)
    # 5% missing payment methods
    missing_payment = np.random.choice(df.index, size=int(len(df) * 0.05), replace=False)
    df.loc[missing_payment, 'payment_method'] = None
    
    # Save to CSV
    output_path = PATHS['data_raw'] / 'transactions.csv'
    df.to_csv(output_path, index=False)
    print(f" Saved to {output_path}\n")
    
    return df


def generate_returns(transactions_df):
    """Generate return/refund data"""
    print(" Generating returns data...")
    
    # Select ~4% of completed transactions to be returned
    completed = transactions_df[transactions_df['order_status'] == 'Completed']
    return_sample = completed.sample(frac=0.04, random_state=42)
    
    returns = []
    for _, txn in return_sample.iterrows():
        return_date = txn['transaction_date'] + timedelta(days=random.randint(1, 30))
        
        return_record = {
            'return_id': f'RET{len(returns)+1:06d}',
            'transaction_id': txn['transaction_id'],
            'customer_id': txn['customer_id'],
            'product_id': txn['product_id'],
            'return_date': return_date,
            'return_reason': np.random.choice([
                'Defective', 'Wrong Item', 'Not as Described', 
                'Changed Mind', 'Better Price Found'
            ], p=[0.25, 0.15, 0.20, 0.30, 0.10]),
            'refund_amount': txn['total_amount'],
            'return_status': np.random.choice(['Approved', 'Pending', 'Rejected'], p=[0.85, 0.10, 0.05])
        }
        returns.append(return_record)
    
    df = pd.DataFrame(returns)
    
    # Save to CSV
    output_path = PATHS['data_raw'] / 'returns.csv'
    df.to_csv(output_path, index=False)
    print(f" Saved to {output_path}")
    print(f"   Generated {len(returns):,} returns\n")
    
    return df


def generate_marketing_campaigns():
    """Generate marketing campaign data"""
    print(" Generating marketing campaigns...")
    
    campaigns = []
    campaign_names = [
        'Summer Sale 2022', 'Black Friday 2022', 'Cyber Monday 2022',
        'Spring Clearance 2023', 'Back to School 2023', 'Holiday Season 2023',
        'New Year Sale 2023', 'Valentine Special 2023', 'Easter Promotion 2023',
        'Summer Sale 2023', 'Black Friday 2023', 'Cyber Monday 2023'
    ]
    
    start_date = datetime.strptime(DATA_CONFIG['start_date'], '%Y-%m-%d')
    
    for i, name in enumerate(campaign_names):
        campaign = {
            'campaign_id': f'CAMP{i+1:03d}',
            'campaign_name': name,
            'start_date': start_date + timedelta(days=i*60),
            'end_date': start_date + timedelta(days=i*60+14),
            'budget': round(np.random.uniform(10000, 100000), 2),
            'channel': np.random.choice(['Email', 'Social Media', 'Search Ads', 'Display Ads']),
            'target_segment': np.random.choice(['All', 'VIP', 'Regular', 'Occasional']),
            'impressions': int(np.random.uniform(50000, 500000)),
            'clicks': int(np.random.uniform(1000, 50000)),
            'conversions': int(np.random.uniform(100, 5000))
        }
        campaigns.append(campaign)
    
    df = pd.DataFrame(campaigns)
    
    # Save to CSV
    output_path = PATHS['data_raw'] / 'marketing_campaigns.csv'
    df.to_csv(output_path, index=False)
    print(f" Saved to {output_path}\n")
    
    return df


def generate_summary_stats(customers_df, products_df, transactions_df, returns_df):
    """Generate and display summary statistics"""
    print("\n" + "="*60)
    print(" DATA GENERATION SUMMARY")
    print("="*60)
    
    print(f"\n Customers: {len(customers_df):,}")
    print(f"   - VIP: {len(customers_df[customers_df['customer_segment']=='VIP']):,}")
    print(f"   - Regular: {len(customers_df[customers_df['customer_segment']=='Regular']):,}")
    print(f"   - Occasional: {len(customers_df[customers_df['customer_segment']=='Occasional']):,}")
    
    print(f"\n Products: {len(products_df):,}")
    print(f"   - Categories: {products_df['category'].nunique()}")
    print(f"   - Avg Price: ${products_df['price'].mean():.2f}")
    
    print(f"\n Transactions: {len(transactions_df):,}")
    print(f"   - Date Range: {transactions_df['transaction_date'].min()} to {transactions_df['transaction_date'].max()}")
    print(f"   - Total Revenue: ${transactions_df['total_amount'].sum():,.2f}")
    print(f"   - Avg Transaction: ${transactions_df['total_amount'].mean():.2f}")
    print(f"   - Order Status:")
    print(f"     • Completed: {len(transactions_df[transactions_df['order_status']=='Completed']):,}")
    print(f"     • Returned: {len(transactions_df[transactions_df['order_status']=='Returned']):,}")
    print(f"     • Cancelled: {len(transactions_df[transactions_df['order_status']=='Cancelled']):,}")
    
    print(f"\n Returns: {len(returns_df):,}")
    print(f"   - Return Rate: {len(returns_df)/len(transactions_df[transactions_df['order_status']=='Completed'])*100:.2f}%")
    
    # Missing data summary
    print(f"\n DATA QUALITY (Missing Values):")
    for df_name, df in [('Customers', customers_df), ('Products', products_df), ('Transactions', transactions_df)]:
        missing_pct = (df.isnull().sum() / len(df) * 100).round(2)
        missing_cols = missing_pct[missing_pct > 0]
        if len(missing_cols) > 0:
            print(f"\n   {df_name}:")
            for col, pct in missing_cols.items():
                print(f"     • {col}: {pct}%")
    
    print(f"\n{'='*60}")
    print(" DATA GENERATION COMPLETED SUCCESSFULLY!")
    print(f"{'='*60}\n")


def main():
    """Main execution function"""
    try:
        # Generate all datasets
        customers_df = generate_customers(DATA_CONFIG['num_customers'])
        products_df = generate_products(DATA_CONFIG['num_products'])
        transactions_df = generate_transactions(customers_df, products_df, DATA_CONFIG['num_transactions'])
        returns_df = generate_returns(transactions_df)
        marketing_df = generate_marketing_campaigns()
        
        # Generate summary
        generate_summary_stats(customers_df, products_df, transactions_df, returns_df)
        
        print(" All data files generated successfully!")
        print(f" Location: {PATHS['data_raw']}\n")
        
        return True
        
    except Exception as e:
        print(f"\n ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)



