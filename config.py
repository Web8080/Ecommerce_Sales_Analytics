"""
Configuration file for E-Commerce Analytics Platform
"""
import os
from dotenv import load_dotenv
from pathlib import Path
from urllib.parse import quote_plus

# Load environment variables
load_dotenv()

# Project Root
PROJECT_ROOT = Path(__file__).parent

# Database Configuration
DATABASE_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),
    'database': os.getenv('DB_NAME', 'ecommerce_analytics'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'postgres')
}

# SQLAlchemy Connection String  
# URL-encode password to handle special characters like @ 
encoded_password = quote_plus(DATABASE_CONFIG['password'])
DATABASE_URL = f"postgresql://{DATABASE_CONFIG['user']}:{encoded_password}@{DATABASE_CONFIG['host']}:{DATABASE_CONFIG['port']}/{DATABASE_CONFIG['database']}?host={DATABASE_CONFIG['host']}"

# Data Generation Configuration
DATA_CONFIG = {
    'num_customers': int(os.getenv('NUM_CUSTOMERS', 50000)),
    'num_products': int(os.getenv('NUM_PRODUCTS', 1000)),
    'num_transactions': int(os.getenv('NUM_TRANSACTIONS', 500000)),
    'start_date': os.getenv('START_DATE', '2022-01-01'),
    'end_date': os.getenv('END_DATE', '2024-01-01')
}

# Paths
PATHS = {
    'data_raw': PROJECT_ROOT / 'data' / 'raw',
    'data_processed': PROJECT_ROOT / 'data' / 'processed',
    'models': PROJECT_ROOT / 'models',
    'reports': PROJECT_ROOT / 'reports',
    'notebooks': PROJECT_ROOT / 'notebooks'
}

# Create directories if they don't exist
for path in PATHS.values():
    path.mkdir(parents=True, exist_ok=True)

# Model Configuration
MODEL_CONFIG = {
    'random_seed': int(os.getenv('RANDOM_SEED', 42)),
    'test_size': float(os.getenv('TEST_SIZE', 0.2)),
    'cv_folds': 5
}

# Dashboard Configuration
DASHBOARD_CONFIG = {
    'port': int(os.getenv('DASHBOARD_PORT', 8501)),
    'page_title': 'E-Commerce Sales Analytics Dashboard',
    'layout': 'wide'
}

# Categories and Product Types
PRODUCT_CATEGORIES = [
    'Electronics', 'Clothing', 'Home & Garden', 'Sports & Outdoors',
    'Books & Media', 'Toys & Games', 'Beauty & Health', 'Food & Beverages',
    'Automotive', 'Office Supplies'
]

PAYMENT_METHODS = ['Credit Card', 'Debit Card', 'PayPal', 'Apple Pay', 'Google Pay']

COUNTRIES = ['USA', 'UK', 'Canada', 'Germany', 'France', 'Australia', 'Japan', 'Brazil']


