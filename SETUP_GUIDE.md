# 🚀 Complete Setup Guide - E-Commerce Analytics Platform

This guide will walk you through setting up the entire project from scratch.

---

## 📋 Prerequisites

### Required Software
- **Python 3.9+** 
- **PostgreSQL 13+** (already installed with your credentials)
- **pip** (Python package manager)
- **Git** (for version control)

### System Requirements
- 4GB+ RAM
- 2GB free disk space
- macOS/Linux/Windows

---

## 🔧 Step-by-Step Setup

### Step 1: Create Virtual Environment

```bash
cd /Users/user/End-to-End_E-Commerce_Sales_Performance_Analytics_Platform

# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate  # Windows
```

### Step 2: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

This will install:
- pandas, numpy (data processing)
- scikit-learn, xgboost (machine learning)
- matplotlib, seaborn, plotly (visualization)
- streamlit (dashboard)
- sqlalchemy, psycopg2 (database)
- jupyter (notebooks)
- And more...

**Expected time:** 5-10 minutes

### Step 3: Configure Environment

Create `.env` file in project root:

```bash
# Create .env file
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

### Step 4: Create PostgreSQL Database

```bash
# Create database
createdb ecommerce_analytics

# Verify it was created
psql -l | grep ecommerce_analytics
```

If you get an error about PostgreSQL not running:
```bash
# Start PostgreSQL (macOS with Homebrew)
brew services start postgresql@14

# OR check if it's already running
pg_isready
```

### Step 5: Create Database Schema

```bash
# Run the schema SQL file
psql -U postgres -d ecommerce_analytics -f database/schema.sql
```

**Expected output:**
```
CREATE TABLE
CREATE TABLE
...
NOTICE: E-Commerce Analytics Schema Created!
```

### Step 6: Generate Synthetic Data

```bash
# Run data generation script
python data/generate_data.py
```

**Expected output:**
```
🚀 Starting E-Commerce Data Generation...
📊 Generating 50,000 customers...
✓ Generated 50,000 customers
📦 Generating 1,000 products...
✓ Generated 1,000 products
💳 Generating 500,000 transactions...
...
✅ DATA GENERATION COMPLETED SUCCESSFULLY!
```

**Expected time:** 5-10 minutes

### Step 7: Load Data into Database

```bash
# Load data into PostgreSQL
python database/load_data.py
```

**Expected output:**
```
🚀 Starting Data Loading Pipeline...
✅ Database connection established
📊 Loading dim_customers...
✓ Loaded 50,000 customers
...
✅ DATA LOADING COMPLETED SUCCESSFULLY!
```

**Expected time:** 2-5 minutes

### Step 8: Verify Setup

```bash
# Quick verification
psql -U postgres -d ecommerce_analytics -c "SELECT COUNT(*) FROM fact_sales;"
```

Should show ~450,000+ records.

---

## 🎉 Launch the Dashboard

```bash
streamlit run dashboards/streamlit_app.py
```

**Expected output:**
```
You can now view your Streamlit app in your browser.
Local URL: http://localhost:8501
```

Open your browser and visit **http://localhost:8501**

---

## 📓 Jupyter Notebooks

### Launch Jupyter

```bash
jupyter notebook
```

This will open Jupyter in your browser.

### Available Notebooks

1. **`01_data_cleaning_eda.ipynb`** - Data cleaning and exploratory analysis
2. **`02_statistical_analysis.ipynb`** - Cohort analysis, RFM segmentation (create this)
3. **`03_predictive_modeling.ipynb`** - ML models (create this)

### Create Additional Notebooks

You can create notebooks for:
- Statistical analysis (cohort, RFM, time-series)
- Predictive modeling (churn, demand forecasting, CLV)

---

## 🔬 Run Machine Learning Models

### Example: Train Churn Prediction Model

Create a script `train_models.py`:

```python
import pandas as pd
from sqlalchemy import create_engine
from src.models import ChurnPredictionModel, print_model_metrics
from config import DATABASE_URL, PATHS

# Load data
engine = create_engine(DATABASE_URL)
df = pd.read_sql("SELECT * FROM vw_sales_overview WHERE order_status = 'Completed'", engine)

# Train churn model
churn_model = ChurnPredictionModel()
features = churn_model.prepare_features(df)
metrics, cm = churn_model.train(features)

print_model_metrics(metrics, "Churn Prediction")
print("Confusion Matrix:")
print(cm)

# Save model
churn_model.save_model(PATHS['models'] / 'churn_model.pkl')
```

Run it:
```bash
python train_models.py
```

---

## 📊 Project Structure Overview

```
End-to-End_E-Commerce_Sales_Performance_Analytics_Platform/
├── data/
│   ├── generate_data.py          # ✅ DONE - Run this first
│   ├── raw/                      # Generated CSV files
│   └── processed/                # Cleaned data
├── database/
│   ├── schema.sql                # ✅ DONE - Database schema
│   └── load_data.py              # ✅ DONE - Load data script
├── src/
│   ├── models.py                 # ✅ DONE - ML models
│   └── utils.py                  # ✅ DONE - Utility functions
├── dashboards/
│   └── streamlit_app.py          # ✅ DONE - Interactive dashboard
├── notebooks/
│   └── 01_data_cleaning_eda.ipynb # ⏳ IN PROGRESS
├── reports/                      # Generated reports & plots
├── models/                       # Saved ML models
├── requirements.txt              # ✅ DONE
├── config.py                     # ✅ DONE
├── README.md                     # ✅ DONE
└── .env                          # ⚠️  YOU NEED TO CREATE THIS
```

---

## ✅ Verification Checklist

After setup, verify each component:

- [ ] Virtual environment activated
- [ ] All packages installed (`pip list`)
- [ ] PostgreSQL database created
- [ ] Database schema loaded (7 tables)
- [ ] Data generated (CSV files in `data/raw/`)
- [ ] Data loaded into database
- [ ] Dashboard launches successfully
- [ ] Jupyter notebooks open

---

## 🐛 Troubleshooting

### Issue: PostgreSQL Connection Error

**Error:** `psycopg2.OperationalError: connection to server failed`

**Solution:**
```bash
# Check PostgreSQL is running
brew services list | grep postgresql

# Start if not running
brew services start postgresql@14

# Verify connection
psql -U postgres -c "SELECT version();"
```

### Issue: Package Installation Fails

**Error:** `ERROR: Failed building wheel for psycopg2`

**Solution:**
```bash
# Install PostgreSQL development headers
brew install postgresql

# Try installing psycopg2-binary instead
pip install psycopg2-binary
```

### Issue: Data Generation Takes Too Long

**Solution:** Reduce dataset size in `.env`:
```
NUM_CUSTOMERS=10000
NUM_PRODUCTS=500
NUM_TRANSACTIONS=100000
```

### Issue: Dashboard Shows "No Data"

**Solution:**
```bash
# Verify data is loaded
psql -U postgres -d ecommerce_analytics -c "SELECT COUNT(*) FROM fact_sales;"

# If 0, reload data
python database/load_data.py
```

### Issue: Jupyter Notebook Kernel Error

**Solution:**
```bash
# Install ipykernel in virtual environment
pip install ipykernel
python -m ipykernel install --user --name=ecommerce_env
```

---

## 🎯 Next Steps

### 1. Explore the Dashboard
- Open http://localhost:8501
- Try different filters
- Explore all 5 tabs
- Take screenshots for your portfolio!

### 2. Run Jupyter Notebooks
- Open `01_data_cleaning_eda.ipynb`
- Run all cells
- Review visualizations and insights

### 3. Train ML Models
- Create training scripts
- Evaluate model performance
- Save trained models

### 4. Customize & Extend
- Add more visualizations
- Create custom reports
- Build additional models
- Add new features

---

## 📚 Learning Resources

### Understand the Code
- **config.py** - Configuration management
- **data/generate_data.py** - Data generation with Faker
- **database/schema.sql** - Star schema design
- **src/models.py** - ML model implementations
- **dashboards/streamlit_app.py** - Dashboard code

### Key Technologies
- **Pandas** - Data manipulation
- **SQLAlchemy** - Database ORM
- **Streamlit** - Dashboard framework
- **Plotly** - Interactive visualizations
- **scikit-learn** - Machine learning

---

## 💡 Tips

1. **Keep virtual environment activated** when working on the project
2. **Commit to Git regularly** to track your progress
3. **Take screenshots** of dashboard and visualizations for your CV
4. **Document your insights** in notebooks
5. **Experiment** with different models and parameters

---

## 🆘 Getting Help

If you encounter issues:

1. Check the error message carefully
2. Refer to this troubleshooting section
3. Check Python package versions
4. Verify PostgreSQL is running
5. Check `.env` configuration

---

## ✅ Setup Complete!

You now have a fully functional e-commerce analytics platform!

**What you've built:**
- ✅ 500K+ transaction database
- ✅ Star schema data warehouse
- ✅ Interactive Streamlit dashboard
- ✅ ML models ready to train
- ✅ Analysis notebooks
- ✅ Professional project structure

**Time to showcase it!** 🎉


