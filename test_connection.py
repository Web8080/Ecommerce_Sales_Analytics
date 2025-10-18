"""
Database Connection Test Script
Run this to diagnose connection issues
"""

import sys
from pathlib import Path

print("="*70)
print(" DATABASE CONNECTION DIAGNOSTIC TEST")
print("="*70 + "\n")

# Test 1: Check .env file exists
print("1⃣  Checking .env file...")
env_file = Path('.env')
if env_file.exists():
    print("    .env file found")
    # Read and display (hiding password)
    with open(env_file, 'r') as f:
        lines = f.readlines()
        for line in lines:
            if 'PASSWORD' in line:
                parts = line.split('=')
                if len(parts) == 2:
                    print(f"    {parts[0]}=****")
            elif line.strip() and not line.startswith('#'):
                print(f"    {line.strip()}")
else:
    print("    .env file NOT found!")
    print("    Create .env file with:")
    print("""
cat > .env << 'EOL'
DB_HOST=localhost
DB_PORT=5432
DB_NAME=ecommerce_analytics
DB_USER=postgres
DB_PASSWORD=NTU99999@
NUM_CUSTOMERS=50000
NUM_PRODUCTS=1000
NUM_TRANSACTIONS=500000
START_DATE=2022-01-01
END_DATE=2024-01-01
RANDOM_SEED=42
TEST_SIZE=0.2
DASHBOARD_PORT=8501
EOL
    """)
    sys.exit(1)

print()

# Test 2: Load config
print("2⃣  Loading configuration...")
try:
    from config import DATABASE_CONFIG, DATABASE_URL
    print("    Config loaded successfully")
    print(f"    Host: {DATABASE_CONFIG['host']}")
    print(f"    Port: {DATABASE_CONFIG['port']}")
    print(f"    Database: {DATABASE_CONFIG['database']}")
    print(f"    User: {DATABASE_CONFIG['user']}")
    print(f"    Password: {'*' * len(DATABASE_CONFIG['password'])}")
except Exception as e:
    print(f"    Config load failed: {str(e)}")
    sys.exit(1)

print()

# Test 3: Check PostgreSQL is running
print("3⃣  Checking PostgreSQL status...")
import subprocess
try:
    result = subprocess.run(['pg_isready'], capture_output=True, text=True)
    if result.returncode == 0:
        print("    PostgreSQL is running")
    else:
        print("     PostgreSQL status unknown")
        print(f"   Output: {result.stdout}")
except FileNotFoundError:
    print("     pg_isready command not found (PostgreSQL may not be in PATH)")
except Exception as e:
    print(f"     Could not check status: {str(e)}")

print()

# Test 4: Try psycopg2 direct connection
print("4⃣  Testing psycopg2 connection...")
try:
    import psycopg2
    conn = psycopg2.connect(
        host=DATABASE_CONFIG['host'],
        port=DATABASE_CONFIG['port'],
        database=DATABASE_CONFIG['database'],
        user=DATABASE_CONFIG['user'],
        password=DATABASE_CONFIG['password']
    )
    print("    psycopg2 connection successful")
    
    # Test query
    cursor = conn.cursor()
    cursor.execute("SELECT version();")
    version = cursor.fetchone()
    print(f"    PostgreSQL version: {version[0][:50]}...")
    cursor.close()
    conn.close()
except ImportError:
    print("    psycopg2 not installed")
    print("    Install: pip install psycopg2-binary")
    sys.exit(1)
except Exception as e:
    print(f"    psycopg2 connection failed: {str(e)}")
    print(f"   Error type: {type(e).__name__}")
    
    if "does not exist" in str(e):
        print("\n    Database doesn't exist. Create it:")
        print(f"      createdb {DATABASE_CONFIG['database']}")
    elif "authentication failed" in str(e):
        print("\n    Authentication failed. Check password in .env file")
    elif "could not connect" in str(e):
        print("\n    Cannot connect. Make sure PostgreSQL is running:")
        print("      brew services start postgresql@14")
    
    sys.exit(1)

print()

# Test 5: Try SQLAlchemy connection
print("5⃣  Testing SQLAlchemy connection...")
try:
    from sqlalchemy import create_engine, text
    
    # Create engine
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    print("    SQLAlchemy engine created")
    
    # Test connection
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        row = result.fetchone()
        print(f"    SQLAlchemy connection successful (test query returned: {row[0]})")
        
        # Check tables
        result = conn.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """))
        tables = result.fetchall()
        
        if tables:
            print(f"    Found {len(tables)} tables in database:")
            for table in tables:
                print(f"      • {table[0]}")
        else:
            print("     No tables found. Run schema:")
            print(f"      psql -U {DATABASE_CONFIG['user']} -d {DATABASE_CONFIG['database']} -f database/schema.sql")
    
except Exception as e:
    print(f"    SQLAlchemy connection failed: {str(e)}")
    print(f"   Error type: {type(e).__name__}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()

# Test 6: Test pandas integration
print("6⃣  Testing pandas with SQLAlchemy...")
try:
    import pandas as pd
    
    # Try to read a simple query
    df = pd.read_sql("SELECT 1 as test_column", engine)
    print(f"    pandas.read_sql() works! Retrieved {len(df)} row(s)")
    
except Exception as e:
    print(f"    pandas integration failed: {str(e)}")
    sys.exit(1)

print()
print("="*70)
print(" ALL TESTS PASSED! Database connection is working correctly.")
print("="*70)
print("\nYou're ready to:")
print("  1. Generate data: python data/generate_data.py")
print("  2. Load data: python database/load_data.py")
print("  3. Run analysis: python src/statistical_analysis.py")
print("  4. Launch dashboard: streamlit run dashboards/streamlit_app.py")


