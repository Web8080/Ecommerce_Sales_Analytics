"""
Data Loading Pipeline for E-Commerce Analytics
Loads CSV data into PostgreSQL star schema
"""

import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
from pathlib import Path
import sys
from datetime import datetime

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))
from config import DATABASE_URL, PATHS

print(" Starting Data Loading Pipeline...")
print(f"Database: {DATABASE_URL.split('@')[1]}\n")  # Hide password


def create_db_engine():
    """Create database connection"""
    try:
        # Create engine with proper configuration
        engine = create_engine(
            DATABASE_URL,
            pool_pre_ping=True,  # Verify connections before using
            echo=False  # Set to True for SQL debugging
        )
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            result.fetchone()  # Consume the result
        print(" Database connection established\n")
        return engine
    except Exception as e:
        print(f" Database connection failed: {str(e)}")
        print(f"   Error type: {type(e).__name__}")
        print("\n Troubleshooting:")
        print("   1. Make sure PostgreSQL is running: pg_isready")
        print("   2. Check .env file exists with correct credentials")
        print("   3. Create database: createdb ecommerce_analytics")
        print("   4. Run schema: psql -U postgres -d ecommerce_analytics -f database/schema.sql\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def load_dimension_customers(engine):
    """Load customer dimension"""
    print(" Loading dim_customers...")
    
    # Read CSV
    df = pd.read_csv(PATHS['data_raw'] / 'customers.csv')
    
    # Insert into database
    df_db = df[['customer_id', 'first_name', 'last_name', 'email', 'phone', 
                'registration_date', 'customer_segment', 'age', 'gender']]
    
    df_db.to_sql('dim_customers', engine, if_exists='append', index=False, method='multi')
    
    print(f"    Loaded {len(df):,} customers\n")
    return df


def load_dimension_products(engine):
    """Load product dimension"""
    print(" Loading dim_products...")
    
    # Read CSV
    df = pd.read_csv(PATHS['data_raw'] / 'products.csv')
    
    # Insert into database
    df_db = df[['product_id', 'product_name', 'category', 'subcategory', 'brand',
                'price', 'cost', 'weight_kg', 'stock_quantity', 'rating', 
                'num_reviews', 'launch_date']]
    
    df_db.to_sql('dim_products', engine, if_exists='append', index=False, method='multi')
    
    print(f"    Loaded {len(df):,} products\n")
    return df


def load_dimension_geography(engine, transactions_df, customers_df):
    """Load geography dimension from transactions and customers"""
    print(" Loading dim_geography...")
    
    # Extract unique geography combinations
    geo_data = []
    
    # From customers
    for _, row in customers_df.iterrows():
        geo_data.append({
            'country': row['country'],
            'state': row['state'],
            'city': row['city'],
            'zip_code': row['zip_code']
        })
    
    # Create dataframe and remove duplicates
    df = pd.DataFrame(geo_data).drop_duplicates()
    
    # Add region (simplified mapping)
    region_map = {
        'USA': 'North America', 'Canada': 'North America',
        'UK': 'Europe', 'Germany': 'Europe', 'France': 'Europe',
        'Australia': 'Oceania', 'Japan': 'Asia', 'Brazil': 'South America'
    }
    df['region'] = df['country'].map(region_map)
    
    # Insert into database
    df.to_sql('dim_geography', engine, if_exists='append', index=False, method='multi')
    
    print(f"    Loaded {len(df):,} geography records\n")
    return df


def load_dimension_marketing(engine):
    """Load marketing campaigns dimension"""
    print(" Loading dim_marketing_campaigns...")
    
    # Read CSV
    df = pd.read_csv(PATHS['data_raw'] / 'marketing_campaigns.csv')
    
    # Insert into database
    df_db = df[['campaign_id', 'campaign_name', 'start_date', 'end_date',
                'budget', 'channel', 'target_segment', 'impressions', 
                'clicks', 'conversions']]
    
    df_db.to_sql('dim_marketing_campaigns', engine, if_exists='append', index=False, method='multi')
    
    print(f"    Loaded {len(df):,} marketing campaigns\n")
    return df


def load_fact_sales(engine):
    """Load sales fact table"""
    print(" Loading fact_sales...")
    
    # Read transactions CSV
    df = pd.read_csv(PATHS['data_raw'] / 'transactions.csv')
    df['transaction_date'] = pd.to_datetime(df['transaction_date'])
    
    print(f"   Read {len(df):,} transactions from CSV")
    
    # Get foreign keys from dimension tables
    print("   Mapping foreign keys...")
    
    with engine.connect() as conn:
        # Get customer keys
        customers = pd.read_sql("SELECT customer_key, customer_id FROM dim_customers", conn)
        customer_map = dict(zip(customers['customer_id'], customers['customer_key']))
        
        # Get product keys
        products = pd.read_sql("SELECT product_key, product_id FROM dim_products", conn)
        product_map = dict(zip(products['product_id'], products['product_key']))
        
        # Get time keys
        time_dim = pd.read_sql("SELECT time_key, date FROM dim_time", conn)
        time_dim['date'] = pd.to_datetime(time_dim['date'])
        time_map = dict(zip(time_dim['date'].dt.date, time_dim['time_key']))
        
        # Load geography dimension
        geography = pd.read_sql("SELECT geography_key, country, state, city FROM dim_geography", conn)
    
    # Get geography mapping from original customers CSV (dim_customers doesn't have geo columns)
    customers_csv = pd.read_csv(PATHS['data_raw'] / 'customers.csv')
    
    # Create customer to geography mapping
    geo_map = {}
    for _, cust in customers_csv.iterrows():
        # Find matching geography
        match = geography[
            (geography['country'] == cust['country']) &
            (geography['state'].fillna('') == (str(cust['state']) if pd.notna(cust['state']) else '')) &
            (geography['city'] == cust['city'])
        ]
        if len(match) > 0:
            geo_map[cust['customer_id']] = match.iloc[0]['geography_key']
        else:
            geo_map[cust['customer_id']] = None
    
    # Map foreign keys
    df['customer_key'] = df['customer_id'].map(customer_map)
    df['product_key'] = df['product_id'].map(product_map)
    df['time_key'] = df['transaction_date'].dt.date.map(time_map)
    df['geography_key'] = df['customer_id'].map(geo_map)
    
    # Prepare fact table data
    fact_df = df[[
        'transaction_id', 'customer_key', 'product_key', 'time_key', 'geography_key',
        'transaction_date', 'quantity', 'unit_price', 'subtotal', 'discount_percent',
        'discount_amount', 'tax_amount', 'shipping_cost', 'total_amount',
        'payment_method', 'order_status', 'shipping_address', 'order_notes'
    ]].copy()
    
    # Convert date to date only (no time)
    fact_df['transaction_date'] = fact_df['transaction_date'].dt.date
    
    # Load in batches
    batch_size = 10000
    total_batches = (len(fact_df) + batch_size - 1) // batch_size
    
    for i in range(0, len(fact_df), batch_size):
        batch = fact_df.iloc[i:i+batch_size]
        batch.to_sql('fact_sales', engine, if_exists='append', index=False, method='multi')
        
        batch_num = (i // batch_size) + 1
        print(f"    Loaded batch {batch_num}/{total_batches} ({len(batch):,} records)")
    
    print(f"    Total loaded: {len(fact_df):,} sales records\n")
    return df


def load_fact_returns(engine):
    """Load returns fact table"""
    print(" Loading fact_returns...")
    
    # Read returns CSV
    df = pd.read_csv(PATHS['data_raw'] / 'returns.csv')
    df['return_date'] = pd.to_datetime(df['return_date'])
    
    print(f"   Read {len(df):,} returns from CSV")
    
    # Get foreign keys
    with engine.connect() as conn:
        # Get sales keys
        sales = pd.read_sql("SELECT sales_key, transaction_id FROM fact_sales", conn)
        sales_map = dict(zip(sales['transaction_id'], sales['sales_key']))
        
        # Get customer keys
        customers = pd.read_sql("SELECT customer_key, customer_id FROM dim_customers", conn)
        customer_map = dict(zip(customers['customer_id'], customers['customer_key']))
        
        # Get product keys
        products = pd.read_sql("SELECT product_key, product_id FROM dim_products", conn)
        product_map = dict(zip(products['product_id'], products['product_key']))
        
        # Get time keys
        time_dim = pd.read_sql("SELECT time_key, date FROM dim_time", conn)
        time_dim['date'] = pd.to_datetime(time_dim['date'])
        time_map = dict(zip(time_dim['date'].dt.date, time_dim['time_key']))
    
    # Map foreign keys
    df['sales_key'] = df['transaction_id'].map(sales_map)
    df['customer_key'] = df['customer_id'].map(customer_map)
    df['product_key'] = df['product_id'].map(product_map)
    df['return_time_key'] = df['return_date'].dt.date.map(time_map)
    
    # Prepare fact table data
    fact_df = df[[
        'return_id', 'sales_key', 'customer_key', 'product_key', 'return_time_key',
        'transaction_id', 'return_date', 'return_reason', 'refund_amount', 'return_status'
    ]].copy()
    
    # Convert date to date only
    fact_df['return_date'] = fact_df['return_date'].dt.date
    
    # Load to database
    fact_df.to_sql('fact_returns', engine, if_exists='append', index=False, method='multi')
    
    print(f"    Loaded {len(fact_df):,} returns records\n")
    return df


def verify_data_load(engine):
    """Verify data was loaded correctly"""
    print(" Verifying data load...\n")
    
    with engine.connect() as conn:
        tables = [
            'dim_customers', 'dim_products', 'dim_time', 'dim_geography',
            'dim_marketing_campaigns', 'fact_sales', 'fact_returns'
        ]
        
        for table in tables:
            result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
            count = result.fetchone()[0]
            print(f"    {table}: {count:,} records")
    
    print("\n" + "="*60)
    
    # Sample query to verify joins
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT 
                COUNT(*) as total_sales,
                SUM(total_amount) as total_revenue,
                AVG(total_amount) as avg_transaction
            FROM fact_sales
            WHERE order_status = 'Completed'
        """))
        
        row = result.fetchone()
        print(f"\n SALES SUMMARY:")
        print(f"   Total Completed Sales: {row[0]:,}")
        print(f"   Total Revenue: ${row[1]:,.2f}")
        print(f"   Avg Transaction: ${row[2]:.2f}")
    
    print("="*60 + "\n")


def main():
    """Main execution function"""
    try:
        start_time = datetime.now()
        
        # Create database engine
        engine = create_db_engine()
        
        # Load dimensions first (required for foreign keys)
        customers_df = load_dimension_customers(engine)
        products_df = load_dimension_products(engine)
        
        # Load transactions to get geography data
        transactions_df = pd.read_csv(PATHS['data_raw'] / 'transactions.csv')
        
        # Load remaining dimensions
        geo_df = load_dimension_geography(engine, transactions_df, customers_df)
        marketing_df = load_dimension_marketing(engine)
        
        # Load facts
        sales_df = load_fact_sales(engine)
        returns_df = load_fact_returns(engine)
        
        # Verify
        verify_data_load(engine)
        
        # Calculate time taken
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print(" DATA LOADING COMPLETED SUCCESSFULLY!")
        print(f"⏱  Time taken: {duration:.2f} seconds\n")
        
        print(" Next steps:")
        print("   1. Run analysis notebooks: jupyter notebook notebooks/")
        print("   2. Launch dashboard: streamlit run dashboards/streamlit_app.py")
        print("   3. View analytics: Open notebooks/01_data_cleaning_eda.ipynb\n")
        
        return True
        
    except Exception as e:
        print(f"\n ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

