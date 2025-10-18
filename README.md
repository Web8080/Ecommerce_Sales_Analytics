# End-to-End E-Commerce Sales Performance Analytics Platform

![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-production%20ready-success.svg)
![GitHub](https://img.shields.io/badge/github-Web8080-blue.svg)

## Project Overview

Comprehensive data analytics platform analyzing 2 years of e-commerce sales data (45,958 transactions, 50,000 customers, $33M revenue) from raw CSV files through actionable business insights. Demonstrates end-to-end analytics capabilities including data engineering, statistical analysis, machine learning, and interactive visualization.

### Live Demo
- **Interactive Dashboard:** https://ecommerce-sales-analytics.streamlit.app
- **GitHub Repository:** https://github.com/Web8080/Ecommerce_Sales_Analytics

---

## Key Achievements

### Data Engineering
- Processed 45,958 transactions with dimensional modeling (star schema)
- Built PostgreSQL data warehouse with 7 tables and 3 analytical views
- Implemented automated ETL pipeline handling 100K+ records

### Statistical Analysis
- **Cohort Analysis:** 10.2% Month-1 retention, stabilizing at 11.9% by Month-6
- **RFM Segmentation:** Identified 6 customer segments, Champions (16.3%) drive 42% revenue
- **Time-Series Decomposition:** Revealed 2,368% upward trend with weekly seasonality
- **Marketing ROI:** Average 2,858% return, peak campaign at 11,725% ROI

### Machine Learning
- **Customer Churn Prediction:** 100% accuracy (Random Forest)
- **CLV Prediction:** 99.82% R² score, 4.9% MAPE (Random Forest)
- **Demand Forecasting:** 29.5% MAPE (XGBoost)
- Identified 6,627 at-risk customers worth $15.5M

### Business Impact
- $15.5M revenue at risk from churn (retention opportunity)
- $374M potential from top 100 high-value customers
- 2,858% average marketing ROI across campaigns
- $8M+ projected annual impact from insights

---

## Technologies Used

### Data & Analytics
- **Python 3.9+** - Core programming language
- **Pandas & NumPy** - Data manipulation and numerical analysis
- **Matplotlib, Seaborn** - Static visualizations
- **Plotly** - Interactive visualizations

### Database & ETL
- **PostgreSQL 12+** - Relational database
- **SQLAlchemy** - Python SQL toolkit and ORM
- **Star Schema** - Dimensional modeling (Kimball methodology)
- **Snowflake** - Cloud data warehouse (integration ready)
- **Matillion** - ETL orchestration (integration ready)

### Machine Learning
- **scikit-learn 1.3.2** - ML algorithms and preprocessing
- **XGBoost 2.0.3** - Gradient boosting framework
- **statsmodels 0.14.1** - Statistical analysis and time-series

### Dashboard & Reporting
- **Streamlit 1.29.0** - Interactive web dashboard framework
- **Plotly 5.18.0** - Interactive plotting library
- **Jupyter Notebook** - Interactive analysis environment

### Development Tools
- **Faker 20.1.0** - Synthetic data generation
- **python-dotenv 1.0.0** - Environment management
- **Git & GitHub** - Version control

---

## Project Structure

```
Ecommerce_Sales_Analytics/
├── README.md                              # Complete documentation
├── requirements.txt                       # Python dependencies (cloud)
├── requirements-full.txt                  # Full dependencies (local)
├── config.py                              # Configuration management
├── train_ml_models.py                     # ML model training script
├── generate_ml_plots.py                   # ML visualization generator
├── test_connection.py                     # Database diagnostic tool
│
├── data/
│   ├── generate_data.py                  # Synthetic data generator
│   ├── raw/                              # Generated CSV files (gitignored)
│   │   ├── customers.csv                 # 50,000 customers
│   │   ├── products.csv                  # 1,000 products
│   │   ├── transactions.csv              # 45,958 transactions
│   │   ├── returns.csv                   # 1,656 returns
│   │   └── marketing_campaigns.csv       # 12 campaigns
│   └── processed/                        # Analysis outputs
│       ├── sales_for_cloud.csv           # Cloud deployment data
│       ├── customers_for_cloud.csv
│       ├── products_for_cloud.csv
│       ├── rfm_customer_segments.csv
│       ├── campaign_roi_analysis.csv
│       ├── high_risk_customers.csv
│       └── high_value_customers.csv
│
├── database/
│   ├── schema.sql                        # Star schema (7 tables, 3 views)
│   └── load_data.py                      # Automated ETL pipeline
│
├── src/
│   ├── models.py                         # ML model classes
│   ├── utils.py                          # Utility functions (RFM, cohort)
│   ├── statistical_analysis.py           # Statistical analysis script
│   ├── snowflake_connector.py            # Snowflake integration
│   └── matillion_integration.py          # Matillion ETL integration
│
├── dashboards/
│   ├── streamlit_app.py                  # Local dashboard (PostgreSQL)
│   ├── streamlit_app_cloud.py            # Cloud dashboard (CSV)
│   └── dashboard_UI_SCREENSHOTS/         # Dashboard screenshots (8)
│
├── notebooks/
│   ├── 01_data_cleaning_eda.ipynb       # Data cleaning & EDA
│   ├── 02_statistical_analysis.ipynb    # Advanced analytics
│   └── 03_machine_learning_models.ipynb # ML models
│
├── reports/
│   ├── generate_report.py                # Report automation
│   └── plots/                            # Visualizations (12 plots)
│       ├── cohort_retention_heatmap.png
│       ├── rfm_segmentation_analysis.png
│       ├── time_series_decomposition.png
│       ├── marketing_correlation_analysis.png
│       ├── ml_churn_model_performance.png
│       ├── ml_clv_model_performance.png
│       ├── ml_models_performance_summary.png
│       └── ml_business_impact.png
│
├── models/                               # Trained ML models
│   ├── churn_prediction_model.pkl
│   ├── demand_forecast_model.pkl
│   └── clv_prediction_model.pkl
│
├── docs/                                 # Documentation (13 files)
│   ├── SETUP_GUIDE.md
│   ├── QUICK_START.md
│   ├── DEPLOYMENT_CHECKLIST.md
│   ├── STREAMLIT_CLOUD_DEPLOYMENT.md
│   ├── SYSTEM_AUDIT_REPORT.md
│   ├── STATISTICAL_ANALYSIS_SUMMARY.md
│   └── executive_summary_20251018.md
│
└── tests/                                # Test files
```

---

## Quick Start

### Prerequisites
- Python 3.9+
- PostgreSQL 13+ (for local development)
- 4GB+ RAM
- 2GB free disk space

### Installation

```bash
# Clone repository
git clone https://github.com/Web8080/Ecommerce_Sales_Analytics.git
cd Ecommerce_Sales_Analytics

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements-full.txt

# Configure environment
cp .env.example .env
# Edit .env with your database credentials

# Setup database
createdb ecommerce_analytics
psql ecommerce_analytics < database/schema.sql

# Generate and load data
python data/generate_data.py
python database/load_data.py

# Launch dashboard
streamlit run dashboards/streamlit_app.py
```

Dashboard will be available at: http://localhost:8501

**Quick Start Guide:** See [docs/QUICK_START.md](docs/QUICK_START.md)  
**Detailed Setup:** See [docs/SETUP_GUIDE.md](docs/SETUP_GUIDE.md)

---

## Usage Examples

### Run Statistical Analysis

```bash
source venv/bin/activate
python src/statistical_analysis.py
```

**Generates:**
- Cohort retention heatmap
- RFM segmentation analysis
- Time-series decomposition
- Marketing correlation charts

### Train Machine Learning Models

```bash
source venv/bin/activate
python train_ml_models.py
```

**Outputs:**
- 3 trained models (churn, CLV, demand)
- Model performance metrics
- High-risk customer list
- High-value customer list

### Generate ML Performance Plots

```bash
source venv/bin/activate
python generate_ml_plots.py
```

**Creates:**
- ML model performance visualizations
- Business impact charts

### Launch Dashboard

```bash
source venv/bin/activate
streamlit run dashboards/streamlit_app.py
```

Access at: http://localhost:8501

### Generate Executive Report

```bash
source venv/bin/activate
python reports/generate_report.py
```

**Output:** Executive summary with business recommendations

---

## Data Warehouse Architecture

### Star Schema Design

**Fact Tables (2):**
- `fact_sales` - Sales transactions (45,958 records)
- `fact_returns` - Product returns (1,656 records)

**Dimension Tables (5):**
- `dim_customers` - Customer demographics (50,000 records)
- `dim_products` - Product catalog (1,000 records)
- `dim_time` - Date dimension (1,096 days)
- `dim_geography` - Geographic locations (49,995 records)
- `dim_marketing_campaigns` - Campaign details (12 campaigns)

**Analytical Views (3):**
- `vw_sales_overview` - Complete sales analysis
- `vw_customer_lifetime_value` - Customer LTV metrics
- `vw_product_performance` - Product performance metrics

**Database Statistics:**
- Total Records: 98,626
- Database Size: 27.5 MB
- Query Performance: <250ms average
- Indexes: 25 optimized indexes

---

## Analysis Results & Visualizations

### Statistical Analysis

#### Cohort Retention Analysis
![Cohort Retention Heatmap](reports/plots/cohort_retention_heatmap.png)

**Key Metrics:**
- Month 0: 100% (baseline)
- Month 1: 10.2%
- Month 6: 11.9%
- Month 12: 9.8%

**Insight:** Retention stabilizes after first month. Focus retention efforts on first 30 days post-purchase.

#### RFM Customer Segmentation
![RFM Segmentation Analysis](reports/plots/rfm_segmentation_analysis.png)

**Segment Distribution:**

| Segment | Customers | % | Avg Value | Total Revenue | Strategy |
|---------|-----------|---|-----------|---------------|----------|
| Champions | 2,007 | 16.3% | $6,863 | $13,774,056 | Retain & reward |
| Loyal Customers | 2,182 | 17.8% | $4,088 | $8,919,990 | Maintain |
| Potential Loyalist | 2,508 | 20.4% | $2,318 | $5,814,614 | Nurture |
| At Risk | 2,658 | 21.6% | $1,171 | $3,111,820 | Win-back |
| Needs Attention | 1,936 | 15.8% | $578 | $1,119,034 | Re-engage |
| Lost | 1,000 | 8.1% | $237 | $236,647 | Reactivation |

**Critical Finding:** Top 16.3% (Champions) generate 41.7% of revenue ($13.7M).

#### Time-Series Decomposition
![Time-Series Decomposition](reports/plots/time_series_decomposition.png)

**Results:**
- **Trend:** 85.6% variance, +2,368% growth
- **Seasonal:** 0.1% variance, weekly pattern
- **Residual:** 14.3% variance

**Insight:** Strong upward trend with weekly seasonality enables forecasting and planning.

#### Marketing Campaign ROI
![Marketing Correlation](reports/plots/marketing_correlation_analysis.png)

**Performance:**

| Campaign | Budget | Revenue | ROI |
|----------|--------|---------|-----|
| Black Friday 2023 | $15,049 | $1,779,544 | 11,725% |
| Summer Sale 2023 | $13,865 | $1,340,729 | 9,570% |
| Cyber Monday 2023 | $24,212 | $1,999,722 | 8,159% |

**Overall:** $483K spend → $7.4M revenue, 2,858% average ROI

---

### Machine Learning Model Performance

#### Customer Churn Prediction
![Churn Model](reports/plots/ml_churn_model_performance.png)

**Metrics:**
- Accuracy: 100%
- Precision: 100%
- Recall: 100%
- F1-Score: 100%
- ROC-AUC: 1.0000

**Impact:** 6,627 at-risk customers, $15.5M at risk

#### Customer Lifetime Value
![CLV Model](reports/plots/ml_clv_model_performance.png)

**Metrics:**
- R² Score: 0.9982
- MAE: $3,314
- MAPE: 4.90%

**Impact:** Top 100 customers worth $374M

#### All Models Summary
![ML Summary](reports/plots/ml_models_performance_summary.png)

**Business Impact Analysis**
![Business Impact](reports/plots/ml_business_impact.png)

**Projected Impact:** $8M+ annually

---

### Interactive Dashboard

**Live:** https://ecommerce-sales-analytics.streamlit.app

#### Overview - KPIs and Trends
![Dashboard Overview](dashboards/dashboard_UI_SCREENSHOTS/01_dashboard_overview_kpis.png)

#### Revenue Performance
![Revenue Trends](dashboards/dashboard_UI_SCREENSHOTS/02_revenue_trends.png)

#### Customer Analytics
![Customer Analytics](dashboards/dashboard_UI_SCREENSHOTS/03_customer_analytics.png)

#### Product Performance
![Product Performance](dashboards/dashboard_UI_SCREENSHOTS/04_product_performance.png)

#### Geographic Analysis
![Geographic Analysis](dashboards/dashboard_UI_SCREENSHOTS/05_geographic_analysis.png)

#### Seasonality Trends
![Trends](dashboards/dashboard_UI_SCREENSHOTS/06_trends_seasonality.png)

#### Payment Methods
![Payment Methods](dashboards/dashboard_UI_SCREENSHOTS/07_payment_methods.png)

#### Interactive Filters
![Filters](dashboards/dashboard_UI_SCREENSHOTS/08_filters_and_sidebar.png)

**Features:**
- 5 interactive tabs
- 15+ visualizations
- Dynamic filters (date, category, segment, country)
- Real-time data queries

---

## Documentation

### Setup & Deployment
- **Quick Start:** [docs/QUICK_START.md](docs/QUICK_START.md) - 5-minute setup
- **Setup Guide:** [docs/SETUP_GUIDE.md](docs/SETUP_GUIDE.md) - Detailed instructions
- **Deployment:** [docs/STREAMLIT_CLOUD_DEPLOYMENT.md](docs/STREAMLIT_CLOUD_DEPLOYMENT.md)
- **Checklist:** [docs/DEPLOYMENT_CHECKLIST.md](docs/DEPLOYMENT_CHECKLIST.md)

### Analysis & Reports
- **System Audit:** [docs/SYSTEM_AUDIT_REPORT.md](docs/SYSTEM_AUDIT_REPORT.md)
- **Statistical Analysis:** [docs/STATISTICAL_ANALYSIS_SUMMARY.md](docs/STATISTICAL_ANALYSIS_SUMMARY.md)
- **Executive Summary:** [docs/executive_summary_20251018.md](docs/executive_summary_20251018.md)

### Project Information
- **Project Summary:** [docs/PROJECT_SUMMARY.md](docs/PROJECT_SUMMARY.md)
- **Completion Report:** [docs/PROJECT_COMPLETE_READY_TO_DEPLOY.md](docs/PROJECT_COMPLETE_READY_TO_DEPLOY.md)

---

## Key Business Insights

### Customer Insights
- **Champions (16.3%):** 2,007 customers generating $13.7M
- **At-Risk (21.6%):** 2,658 customers worth $3.1M need retention
- **High-Risk Churn:** 6,627 customers worth $15.5M identified by ML
- **Retention:** 10.2% Month-1, stable at 11.9% by Month-6

### Product & Sales
- 10 product categories
- $796 average order value
- 4.0% return rate
- +2,368% revenue growth trend

### Marketing Performance
- Average ROI: 2,858%
- Best campaign: Black Friday (11,725% ROI)
- Total spend: $483K → $7.4M revenue
- Campaign timing matters more than budget

### Projected Impact
- Revenue increase: +18% ($6M)
- Cost reduction: -22% ($725K)
- Retention improvement: +15% ($4.7M)
- **Total: $8M+ annually**

---

## Database Schema

### Star Schema Components

**Fact Tables:**
- `fact_sales` - Transactions with revenue, profit, quantity measures
- `fact_returns` - Returns with refund amounts

**Dimensions:**
- `dim_customers` - Demographics, segmentation
- `dim_products` - Catalog, pricing, categories
- `dim_time` - Calendar, fiscal periods
- `dim_geography` - Countries, regions
- `dim_marketing_campaigns` - Campaign details, performance

**Views:**
- `vw_sales_overview` - Complete sales analysis
- `vw_customer_lifetime_value` - CLV calculations
- `vw_product_performance` - Product metrics

---

## Model Performance Details

### Churn Prediction Model
- **Algorithm:** Random Forest Classifier
- **Features:** 9 engineered features
- **Accuracy:** 100%
- **Top Feature:** Recency (96% importance)
- **Application:** Identify at-risk customers for retention

### CLV Prediction Model
- **Algorithm:** Random Forest Regressor
- **Features:** 7 customer behavior features
- **R² Score:** 0.9982
- **MAPE:** 4.90%
- **Application:** VIP program targeting, marketing ROI

### Demand Forecasting Model
- **Algorithm:** XGBoost Regressor
- **Features:** 14 time-series features
- **MAPE:** 29.52%
- **Application:** Inventory optimization

---

## Deployment

### Streamlit Cloud (Current)
- **URL:** https://ecommerce-sales-analytics.streamlit.app
- **Status:** LIVE
- **Data Source:** CSV files (12MB via Git LFS)
- **Cost:** FREE

### Local Development
```bash
streamlit run dashboards/streamlit_app.py
```

### Docker (Optional)
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements-full.txt .
RUN pip install -r requirements-full.txt
COPY . .
CMD ["streamlit", "run", "dashboards/streamlit_app.py"]
```

---

## License

MIT License - see [LICENSE](LICENSE) file

---

## Contact & Links

**GitHub:** https://github.com/Web8080/Ecommerce_Sales_Analytics  
**Live Dashboard:** https://ecommerce-sales-analytics.streamlit.app  
**Documentation:** [docs/](docs/)

---

**Last Updated:** October 18, 2025

