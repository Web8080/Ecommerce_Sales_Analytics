# Streamlit Cloud Deployment Guide

**Platform:** Streamlit Community Cloud (FREE)  
**Repository:** https://github.com/Web8080/Ecommerce_Sales_Analytics  
**Estimated Time:** 15-20 minutes

---

## Prerequisites

- GitHub account
- Streamlit Cloud account (free)
- Repository pushed to GitHub

---

## Step 1: Prepare Repository for Deployment

### 1.1 Create Streamlit Config Directory

```bash
cd /Users/user/End-to-End_E-Commerce_Sales_Performance_Analytics_Platform
mkdir -p .streamlit
```

### 1.2 Create config.toml

Create `.streamlit/config.toml`:

```toml
[theme]
primaryColor = "#2E86AB"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"

[server]
headless = true
port = 8501
enableCORS = false
enableXsrfProtection = true

[browser]
gatherUsageStats = false
```

### 1.3 Create secrets.toml Template

Create `.streamlit/secrets.toml.example`:

```toml
# Database Connection (DO NOT COMMIT secrets.toml - only this example)
[database]
DB_HOST = "your-database-host.com"
DB_PORT = "5432"
DB_NAME = "ecommerce_analytics"
DB_USER = "your_username"
DB_PASSWORD = "your_password"

# Data Configuration
[data]
NUM_CUSTOMERS = "50000"
NUM_PRODUCTS = "1000"
NUM_TRANSACTIONS = "500000"

# Model Configuration
[model]
RANDOM_SEED = "42"
TEST_SIZE = "0.2"
```

### 1.4 Update .gitignore

Ensure `.streamlit/secrets.toml` is in `.gitignore` (already done):

```
.streamlit/secrets.toml
```

---

## Step 2: Modify config.py for Cloud Deployment

The `config.py` should support both local `.env` and Streamlit secrets:

```python
import os
import streamlit as st
from pathlib import Path
from urllib.parse import quote_plus

# Try Streamlit secrets first, then fall back to .env
try:
    # Streamlit Cloud deployment
    DATABASE_CONFIG = {
        'host': st.secrets["database"]["DB_HOST"],
        'port': st.secrets["database"]["DB_PORT"],
        'database': st.secrets["database"]["DB_NAME"],
        'user': st.secrets["database"]["DB_USER"],
        'password': st.secrets["database"]["DB_PASSWORD"]
    }
    print("Using Streamlit secrets")
except:
    # Local development
    from dotenv import load_dotenv
    load_dotenv()
    DATABASE_CONFIG = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': os.getenv('DB_PORT', '5432'),
        'database': os.getenv('DB_NAME', 'ecommerce_analytics'),
        'user': os.getenv('DB_USER', 'postgres'),
        'password': os.getenv('DB_PASSWORD', 'postgres')
    }
    print("Using .env file")
```

---

## Step 3: Deploy to Streamlit Cloud

### 3.1 Sign Up / Sign In

1. Go to: https://streamlit.io/cloud
2. Click "Sign in" and use your GitHub account
3. Authorize Streamlit to access your GitHub repositories

### 3.2 Deploy New App

1. Click "New app" button
2. Select repository: `Web8080/Ecommerce_Sales_Analytics`
3. Select branch: `main`
4. Set main file path: `dashboards/streamlit_app.py`
5. Click "Advanced settings..."

### 3.3 Configure Secrets

In the "Advanced settings" section:

1. Click "Secrets" tab
2. Paste your database credentials:

```toml
[database]
DB_HOST = "127.0.0.1"
DB_PORT = "5432"
DB_NAME = "ecommerce_analytics"
DB_USER = "postgres"
DB_PASSWORD = "NTU99999@"
```

**IMPORTANT:** For cloud deployment, you'll need:
- A cloud-hosted PostgreSQL database (not localhost)
- Options: ElephantSQL (free tier), AWS RDS, Azure Database, or Heroku Postgres

### 3.4 Deploy

1. Click "Deploy!"
2. Wait 2-5 minutes for deployment
3. Your app will be live at: `https://your-app-name.streamlit.app`

---

## Step 4: Cloud Database Options (Required for Public Deployment)

Since the dashboard needs database access, you have these options:

### Option A: ElephantSQL (FREE Tier)

**Best for:** Portfolio/Demo purposes

1. Go to: https://www.elephantsql.com/
2. Sign up (free tier: 20MB database)
3. Create new instance
4. Get connection details
5. Restore your PostgreSQL dump to ElephantSQL
6. Update Streamlit secrets with ElephantSQL credentials

### Option B: Heroku Postgres (FREE Tier)

**Best for:** Small production apps

1. Sign up at: https://www.heroku.com/
2. Create app and add Postgres addon (free tier: 10K rows)
3. Get DATABASE_URL from Heroku dashboard
4. Load your data to Heroku Postgres
5. Use DATABASE_URL in Streamlit secrets

### Option C: Neon (Serverless Postgres - FREE)

**Best for:** Modern serverless setup

1. Go to: https://neon.tech/
2. Sign up (free tier: 512 MB)
3. Create project
4. Get connection string
5. Load data
6. Use in Streamlit secrets

### Option D: Use CSV Files (Simple Alternative)

**Best for:** Quick demo without database

Modify `streamlit_app.py` to load from CSV instead of database:

```python
# Instead of PostgreSQL query
df = pd.read_csv('data/processed/cleaned_sales_data.csv')
```

**Pros:** No database needed  
**Cons:** No real-time queries, limited data

---

## Step 5: Alternative - Deploy with CSV Data

For quick deployment without cloud database:

### 5.1 Modify Dashboard to Use CSV

Create `dashboards/streamlit_app_csv.py`:

```python
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# Load data from CSV instead of database
@st.cache_data
def load_sales_data():
    df = pd.read_csv('data/processed/cleaned_sales_data.csv')
    df['transaction_date'] = pd.to_datetime(df['transaction_date'])
    return df

df = load_sales_data()
# ... rest of dashboard code
```

### 5.2 Deploy CSV Version

1. Commit CSV data files to Git
2. Update main file path to: `dashboards/streamlit_app_csv.py`
3. Deploy

**Note:** For this approach, update `.gitignore` to include the specific CSV file.

---

## Step 6: Post-Deployment

### 6.1 Test Deployed App

1. Visit your app URL
2. Test all 5 tabs
3. Verify filters work
4. Check all visualizations load

### 6.2 Custom Domain (Optional)

Streamlit Cloud allows custom domains:

1. Go to app settings
2. Add custom domain
3. Update DNS records
4. Access via: `analytics.yourdomain.com`

### 6.3 Update README

Add your live URL to README.md:

```markdown
### Live Demo
**Interactive Dashboard:** https://your-app-name.streamlit.app
```

### 6.4 Share Your Project

Update your:
- **LinkedIn:** Post with live link
- **Resume:** Add dashboard URL
- **GitHub README:** Badge with live demo link

---

## Recommended Approach for Portfolio

**For Resume/Portfolio (Recommended):**

### Option 1: Cloud Database + Streamlit Cloud
- **Pros:** Full functionality, impressive demo
- **Cons:** Requires cloud database setup
- **Time:** 30-45 minutes
- **Cost:** FREE (using free tiers)

### Option 2: CSV + Streamlit Cloud
- **Pros:** Quick deployment, no database needed
- **Cons:** Limited functionality
- **Time:** 10-15 minutes
- **Cost:** FREE

### Option 3: Video Demo + GitHub Only
- **Pros:** Showcases everything, no ongoing costs
- **Cons:** Not interactive for viewers
- **Time:** 20 minutes (record demo)
- **Cost:** FREE

**My Recommendation:** Option 2 (CSV + Streamlit Cloud) for quick portfolio showcase, then upgrade to Option 1 if interviewing seriously.

---

## Troubleshooting

### Issue: App won't start

**Solution:**
- Check `requirements.txt` includes all dependencies
- Verify main file path is correct
- Check Streamlit logs in dashboard

### Issue: Database connection fails

**Solution:**
- Verify secrets are correctly formatted (TOML syntax)
- Check database is publicly accessible
- Test connection from local machine first
- Ensure database allows connections from Streamlit's IP ranges

### Issue: Large dataset loads slowly

**Solution:**
- Implement caching (`@st.cache_data`)
- Reduce initial query size
- Use data sampling for demo
- Consider data aggregation

### Issue: App crashes on certain tabs

**Solution:**
- Add error handling (`try/except`)
- Check for missing columns
- Validate data types
- Test locally first

---

## Deployment Checklist

- [ ] Repository pushed to GitHub
- [ ] `.streamlit/config.toml` created
- [ ] Database accessible from cloud (or using CSV)
- [ ] Streamlit secrets configured
- [ ] App deployed successfully
- [ ] All tabs tested and working
- [ ] Custom URL configured (optional)
- [ ] README updated with live link
- [ ] Shared on LinkedIn/resume

---

## Post-Deployment Monitoring

### Monitor These Metrics:

1. **App Performance**
   - Load time: <5 seconds
   - Query time: <2 seconds
   - Error rate: <1%

2. **Usage Analytics** (in Streamlit Cloud dashboard)
   - Total views
   - Unique visitors
   - Average session time

3. **Cost Monitoring** (if using paid database)
   - Database connections
   - Storage usage
   - Query volume

---

## Maintenance

### Weekly:
- Check app is running
- Review any error logs
- Monitor usage stats

### Monthly:
- Update data (if using real data)
- Retrain models
- Review and optimize queries

### As Needed:
- Update code with improvements
- Add new features
- Respond to user feedback

---

## Support & Resources

**Streamlit Documentation:** https://docs.streamlit.io/  
**Deployment Guide:** https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app  
**Secrets Management:** https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app/secrets-management

---

## Summary

**Your app is ready for deployment!**

**Quick Steps:**
1. Sign in to Streamlit Cloud
2. Connect GitHub repo
3. Configure secrets (or use CSV)
4. Deploy
5. Share link on resume/LinkedIn

**Expected Result:**  
Live, interactive dashboard at: `https://your-app-name.streamlit.app`

---

**Questions?** Check Streamlit's documentation or community forum: https://discuss.streamlit.io/

**Ready to deploy!**

