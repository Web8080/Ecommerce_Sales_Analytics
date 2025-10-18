# ⚡ Quick Start Guide (5 Minutes)

Get the project running in 5 simple commands!

---

## Prerequisites
- PostgreSQL installed
- Python 3.9+

---

## 🚀 5-Step Quick Start

### 1️⃣ Setup Environment
```bash
cd /Users/user/End-to-End_E-Commerce_Sales_Performance_Analytics_Platform
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2️⃣ Configure Database
```bash
# Create .env file with your credentials
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
```

### 3️⃣ Create Database & Schema
```bash
createdb ecommerce_analytics
psql -U postgres -d ecommerce_analytics -f database/schema.sql
```

### 4️⃣ Generate & Load Data
```bash
python data/generate_data.py
python database/load_data.py
```

### 5️⃣ Launch Dashboard
```bash
streamlit run dashboards/streamlit_app.py
```

**Done!** Open http://localhost:8501 🎉

---

## ⏱️ Expected Time
- Step 1: ~5 minutes (package installation)
- Step 2: ~30 seconds
- Step 3: ~30 seconds
- Step 4: ~10 minutes (data generation)
- Step 5: ~30 seconds

**Total: ~15-20 minutes**

---

## 🎯 What You Get

✅ **500K+ transactions** in PostgreSQL  
✅ **Interactive dashboard** with 15+ visualizations  
✅ **Star schema** data warehouse  
✅ **ML models** ready to train  
✅ **Jupyter notebooks** for analysis  

---

## 📊 Verify Setup

```bash
# Check database
psql -U postgres -d ecommerce_analytics -c "SELECT COUNT(*) FROM fact_sales;"

# Should show ~450,000+ records
```

---

## 🐛 Quick Troubleshooting

**PostgreSQL not running?**
```bash
brew services start postgresql@14
```

**Connection error?**
- Check `.env` file has correct password
- Verify PostgreSQL is running: `pg_isready`

**Dashboard shows no data?**
- Verify data loaded: `psql -U postgres -d ecommerce_analytics -c "SELECT COUNT(*) FROM fact_sales;"`
- Reload if needed: `python database/load_data.py`

---

## 🎓 Next Steps

1. **Explore Dashboard** - Try all filters and visualizations
2. **Open Jupyter** - `jupyter notebook` → Open `01_data_cleaning_eda.ipynb`
3. **Train Models** - Run ML models in `src/models.py`
4. **Customize** - Add your own analysis and features!

---

**Need detailed setup?** See [SETUP_GUIDE.md](SETUP_GUIDE.md)


