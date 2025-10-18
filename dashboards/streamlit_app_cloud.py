"""
E-Commerce Sales Analytics Dashboard - Cloud Version
Uses CSV files instead of PostgreSQL for Streamlit Cloud deployment
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="E-Commerce Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 48px;
        font-weight: bold;
        color: #2E86AB;
        text-align: center;
        padding: 20px;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# Title
st.markdown('<div class="main-header">E-Commerce Sales Analytics Dashboard</div>', unsafe_allow_html=True)
st.markdown("---")

# Cache data loading
@st.cache_data
def load_sales_data():
    """Load sales data from CSV"""
    try:
        df = pd.read_csv('data/processed/sales_for_cloud.csv')
        df['transaction_date'] = pd.to_datetime(df['transaction_date'])
        
        # Calculate profit_margin if not present
        if 'profit_margin' not in df.columns and 'profit' in df.columns and 'total_amount' in df.columns:
            df['profit_margin'] = (df['profit'] / df['total_amount'] * 100).fillna(0)
        
        return df
    except FileNotFoundError:
        st.error("Data files not found. Please ensure data/processed/sales_for_cloud.csv exists.")
        return pd.DataFrame()

@st.cache_data
def load_customer_data():
    """Load customer data from CSV"""
    try:
        df = pd.read_csv('data/processed/customers_for_cloud.csv')
        return df
    except FileNotFoundError:
        return pd.DataFrame()

@st.cache_data
def load_product_data():
    """Load product data from CSV"""
    try:
        df = pd.read_csv('data/processed/products_for_cloud.csv')
        return df
    except FileNotFoundError:
        return pd.DataFrame()

# Load data
with st.spinner("Loading data..."):
    df = load_sales_data()
    customers_df = load_customer_data()
    products_df = load_product_data()
    
    if len(df) == 0:
        st.error("Failed to load data. Check data files.")
        st.stop()
    else:
        st.success(f"Data loaded successfully! {len(df):,} transactions")

# Sidebar filters
st.sidebar.header("Filters")

# Date range filter
date_range = st.sidebar.date_input(
    "Date Range",
    value=(df['transaction_date'].min(), df['transaction_date'].max()),
    min_value=df['transaction_date'].min(),
    max_value=df['transaction_date'].max()
)

# Category filter
categories = ['All'] + sorted(df['category'].unique().tolist())
selected_category = st.sidebar.selectbox("Product Category", categories)

# Customer segment filter
segments = ['All'] + sorted(df['customer_segment'].unique().tolist())
selected_segment = st.sidebar.selectbox("Customer Segment", segments)

# Country filter
countries = ['All'] + sorted(df['country'].unique().tolist())
selected_country = st.sidebar.selectbox("Country", countries)

# Apply filters
filtered_df = df.copy()

if len(date_range) == 2:
    filtered_df = filtered_df[
        (filtered_df['transaction_date'].dt.date >= date_range[0]) &
        (filtered_df['transaction_date'].dt.date <= date_range[1])
    ]

if selected_category != 'All':
    filtered_df = filtered_df[filtered_df['category'] == selected_category]

if selected_segment != 'All':
    filtered_df = filtered_df[filtered_df['customer_segment'] == selected_segment]

if selected_country != 'All':
    filtered_df = filtered_df[filtered_df['country'] == selected_country]

# Display metrics
st.sidebar.markdown("---")
st.sidebar.metric("Filtered Records", f"{len(filtered_df):,}")
st.sidebar.metric("Total Revenue", f"${filtered_df['total_amount'].sum():,.2f}")

# Main Dashboard
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Overview", "Customers", "Products", "Geography", "Trends"
])

### TAB 1: OVERVIEW ###
with tab1:
    st.header("Business Overview")
    
    # KPI Cards
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        total_revenue = filtered_df['total_amount'].sum()
        st.metric("Total Revenue", f"${total_revenue:,.0f}")
    
    with col2:
        total_profit = filtered_df['profit'].sum()
        profit_margin = (total_profit / total_revenue * 100) if total_revenue > 0 else 0
        st.metric("Total Profit", f"${total_profit:,.0f}", delta=f"{profit_margin:.1f}%")
    
    with col3:
        total_orders = filtered_df['transaction_id'].nunique()
        avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
        st.metric("Total Orders", f"{total_orders:,}", delta=f"${avg_order_value:.2f} AOV")
    
    with col4:
        unique_customers = filtered_df['customer_id'].nunique()
        st.metric("Unique Customers", f"{unique_customers:,}")
    
    with col5:
        unique_products = filtered_df['product_id'].nunique()
        st.metric("Products Sold", f"{unique_products:,}")
    
    st.markdown("---")
    
    # Revenue Trend
    st.subheader("Revenue Trend")
    daily_revenue = filtered_df.groupby('transaction_date')['total_amount'].sum().reset_index()
    fig = px.line(daily_revenue, x='transaction_date', y='total_amount',
                  labels={'transaction_date': 'Date', 'total_amount': 'Revenue ($)'})
    fig.update_traces(line_color='#2E86AB', line_width=2)
    st.plotly_chart(fig, use_container_width=True)

### TAB 2: CUSTOMERS ###
with tab2:
    st.header("Customer Analytics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Customer Segment Distribution")
        segment_data = filtered_df.groupby('customer_segment')['total_amount'].sum().reset_index()
        fig = px.pie(segment_data, values='total_amount', names='customer_segment',
                     title='Revenue by Customer Segment')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Top 20 Customers by Revenue")
        top_customers = filtered_df.groupby('customer_id').agg({
            'total_amount': 'sum',
            'transaction_id': 'count'
        }).reset_index()
        top_customers.columns = ['Customer ID', 'Total Revenue', 'Orders']
        top_customers = top_customers.nlargest(20, 'Total Revenue')
        top_customers['Total Revenue'] = top_customers['Total Revenue'].apply(lambda x: f"${x:,.2f}")
        st.dataframe(top_customers, use_container_width=True, hide_index=True)

### TAB 3: PRODUCTS ###
with tab3:
    st.header("Product Performance")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Top Categories by Revenue")
        category_revenue = filtered_df.groupby('category')['total_amount'].sum().reset_index()
        category_revenue = category_revenue.nlargest(10, 'total_amount')
        fig = px.bar(category_revenue, y='category', x='total_amount',
                     orientation='h',
                     color='total_amount',
                     color_continuous_scale='Viridis')
        fig.update_xaxes(title_text="Revenue ($)")
        fig.update_yaxes(title_text="")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Category Performance Table")
        category_stats = filtered_df.groupby('category').agg({
            'total_amount': 'sum',
            'transaction_id': 'count',
            'quantity': 'sum'
        }).reset_index()
        category_stats.columns = ['Category', 'Revenue', 'Orders', 'Units']
        category_stats = category_stats.sort_values('Revenue', ascending=False)
        category_stats['Revenue'] = category_stats['Revenue'].apply(lambda x: f"${x:,.2f}")
        st.dataframe(category_stats, use_container_width=True, hide_index=True)

### TAB 4: GEOGRAPHY ###
with tab4:
    st.header("Geographic Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Revenue by Country")
        country_revenue = filtered_df.groupby('country')['total_amount'].sum().reset_index()
        fig = px.bar(country_revenue, x='country', y='total_amount',
                     color='total_amount',
                     color_continuous_scale='Tealgrn')
        fig.update_xaxes(title_text="Country")
        fig.update_yaxes(title_text="Revenue ($)")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Geographic Metrics")
        geo_metrics = filtered_df.groupby('country').agg({
            'total_amount': 'sum',
            'transaction_id': 'count',
            'customer_id': 'nunique'
        }).reset_index()
        geo_metrics.columns = ['Country', 'Revenue', 'Orders', 'Customers']
        geo_metrics = geo_metrics.sort_values('Revenue', ascending=False)
        geo_metrics['Revenue'] = geo_metrics['Revenue'].apply(lambda x: f"${x:,.2f}")
        st.dataframe(geo_metrics, use_container_width=True, hide_index=True)

### TAB 5: TRENDS ###
with tab5:
    st.header("Trends & Seasonality")
    
    st.subheader("Monthly Seasonality")
    filtered_df['month'] = filtered_df['transaction_date'].dt.month
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                   'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    monthly_season = filtered_df.groupby('month')['total_amount'].sum().reset_index()
    monthly_season['month_name'] = monthly_season['month'].apply(lambda x: month_names[x-1])
    
    fig = px.bar(monthly_season, x='month_name', y='total_amount',
                 color='total_amount',
                 color_continuous_scale='RdYlGn',
                 labels={'month_name': 'Month', 'total_amount': 'Total Revenue ($)'})
    st.plotly_chart(fig, use_container_width=True)

# Footer
st.markdown("---")
st.markdown(f"""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p>E-Commerce Sales Analytics Platform | Built with Streamlit & Python</p>
    <p>Data: Oct 2022 - Jan 2024 | 45,958 transactions | $33M revenue analyzed</p>
</div>
""", unsafe_allow_html=True)

