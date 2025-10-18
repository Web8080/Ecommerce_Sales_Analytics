"""
E-Commerce Sales Analytics Dashboard
Interactive Streamlit Dashboard with 15+ visualizations
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sqlalchemy import create_engine
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))
from config import DATABASE_URL, PATHS

# Page configuration
st.set_page_config(
    page_title="E-Commerce Analytics Dashboard",
    page_icon="",
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
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #2E86AB;
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
st.markdown('<div class="main-header"> E-Commerce Sales Analytics Dashboard</div>', unsafe_allow_html=True)
st.markdown("---")

# Cache data loading
@st.cache_data(ttl=600)
def load_sales_data():
    """Load sales data from database"""
    engine = create_engine(DATABASE_URL)
    query = """
    SELECT * FROM vw_sales_overview
    WHERE order_status = 'Completed'
    """
    df = pd.read_sql(query, engine)
    df['transaction_date'] = pd.to_datetime(df['transaction_date'])
    
    # Calculate profit_margin if not present
    if 'profit_margin' not in df.columns and 'profit' in df.columns and 'total_amount' in df.columns:
        df['profit_margin'] = (df['profit'] / df['total_amount'] * 100).fillna(0)
    
    return df

@st.cache_data(ttl=600)
def load_customer_data():
    """Load customer lifetime value data"""
    engine = create_engine(DATABASE_URL)
    query = "SELECT * FROM vw_customer_lifetime_value"
    df = pd.read_sql(query, engine)
    return df

@st.cache_data(ttl=600)
def load_product_data():
    """Load product performance data"""
    engine = create_engine(DATABASE_URL)
    query = "SELECT * FROM vw_product_performance"
    df = pd.read_sql(query, engine)
    return df

# Load data
with st.spinner("Loading data..."):
    try:
        df = load_sales_data()
        customers_df = load_customer_data()
        products_df = load_product_data()
        st.success(" Data loaded successfully!")
    except Exception as e:
        st.error(f" Error loading data: {str(e)}")
        st.info(" Make sure PostgreSQL is running and data is loaded. Run: python data/generate_data.py && python database/load_data.py")
        st.stop()

# Sidebar filters
st.sidebar.header(" Filters")

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

# Display record count
st.sidebar.markdown("---")
st.sidebar.metric("Filtered Records", f"{len(filtered_df):,}")
st.sidebar.metric("Total Revenue", f"${filtered_df['total_amount'].sum():,.2f}")

# Main Dashboard
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    " Overview", " Customers", " Products", " Geography", " Trends"
])

### TAB 1: OVERVIEW ###
with tab1:
    st.header(" Business Overview")
    
    # KPI Cards
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        total_revenue = filtered_df['total_amount'].sum()
        st.metric("Total Revenue", f"${total_revenue:,.0f}", delta=None)
    
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
    
    # Revenue and Orders Over Time
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader(" Revenue Trend")
        daily_revenue = filtered_df.groupby('transaction_date')['total_amount'].sum().reset_index()
        fig = px.line(daily_revenue, x='transaction_date', y='total_amount',
                      title='Daily Revenue',
                      labels={'transaction_date': 'Date', 'total_amount': 'Revenue ($)'})
        fig.update_traces(line_color='#2E86AB', line_width=2)
        fig.update_layout(hovermode='x unified')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader(" Orders Trend")
        daily_orders = filtered_df.groupby('transaction_date')['transaction_id'].count().reset_index()
        fig = px.line(daily_orders, x='transaction_date', y='transaction_id',
                      title='Daily Orders',
                      labels={'transaction_date': 'Date', 'transaction_id': 'Orders'})
        fig.update_traces(line_color='#F18F01', line_width=2)
        fig.update_layout(hovermode='x unified')
        st.plotly_chart(fig, use_container_width=True)
    
    # Monthly Revenue and Profit
    st.subheader(" Monthly Performance")
    filtered_df['year_month'] = filtered_df['transaction_date'].dt.to_period('M').astype(str)
    monthly = filtered_df.groupby('year_month').agg({
        'total_amount': 'sum',
        'profit': 'sum',
        'transaction_id': 'count'
    }).reset_index()
    
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Bar(x=monthly['year_month'], y=monthly['total_amount'], name="Revenue",
               marker_color='#2E86AB', opacity=0.7),
        secondary_y=False
    )
    fig.add_trace(
        go.Scatter(x=monthly['year_month'], y=monthly['profit'], name="Profit",
                   line=dict(color='#F18F01', width=3), mode='lines+markers'),
        secondary_y=True
    )
    fig.update_layout(title='Monthly Revenue & Profit', hovermode='x unified')
    fig.update_xaxes(title_text="Month")
    fig.update_yaxes(title_text="Revenue ($)", secondary_y=False)
    fig.update_yaxes(title_text="Profit ($)", secondary_y=True)
    st.plotly_chart(fig, use_container_width=True)

### TAB 2: CUSTOMERS ###
with tab2:
    st.header(" Customer Analytics")
    
    # Customer Segment Analysis
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Customer Segment Distribution")
        segment_data = filtered_df.groupby('customer_segment')['total_amount'].sum().reset_index()
        fig = px.pie(segment_data, values='total_amount', names='customer_segment',
                     title='Revenue by Customer Segment',
                     color_discrete_sequence=px.colors.qualitative.Set2)
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Average Transaction by Segment")
        segment_avg = filtered_df.groupby('customer_segment')['total_amount'].mean().reset_index()
        fig = px.bar(segment_avg, x='customer_segment', y='total_amount',
                     title='Avg Transaction Value by Segment',
                     color='total_amount',
                     color_continuous_scale='Blues')
        fig.update_layout(showlegend=False)
        fig.update_xaxes(title_text="Segment")
        fig.update_yaxes(title_text="Avg Transaction ($)")
        st.plotly_chart(fig, use_container_width=True)
    
    # Top Customers
    st.subheader(" Top 20 Customers by Revenue")
    top_customers = filtered_df.groupby('customer_id').agg({
        'total_amount': 'sum',
        'transaction_id': 'count',
        'customer_segment': 'first',
        'country': 'first'
    }).reset_index()
    top_customers.columns = ['Customer ID', 'Total Revenue', 'Orders', 'Segment', 'Country']
    top_customers = top_customers.nlargest(20, 'Total Revenue')
    top_customers['Total Revenue'] = top_customers['Total Revenue'].apply(lambda x: f"${x:,.2f}")
    st.dataframe(top_customers, use_container_width=True, hide_index=True)
    
    # Customer Lifetime Value Distribution
    st.subheader(" Customer Lifetime Value Distribution")
    if len(customers_df) > 0:
        fig = px.histogram(customers_df, x='total_revenue', nbins=50,
                           title='Distribution of Customer Lifetime Value',
                           labels={'total_revenue': 'Customer LTV ($)'},
                           color_discrete_sequence=['#4ECDC4'])
        st.plotly_chart(fig, use_container_width=True)

### TAB 3: PRODUCTS ###
with tab3:
    st.header(" Product Performance")
    
    # Category Performance
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Top Categories by Revenue")
        category_revenue = filtered_df.groupby('category')['total_amount'].sum().reset_index()
        category_revenue = category_revenue.nlargest(10, 'total_amount')
        fig = px.bar(category_revenue, y='category', x='total_amount',
                     orientation='h',
                     title='Top 10 Categories',
                     color='total_amount',
                     color_continuous_scale='Viridis')
        fig.update_layout(showlegend=False)
        fig.update_xaxes(title_text="Revenue ($)")
        fig.update_yaxes(title_text="")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Category Profit Margins")
        category_margin = filtered_df.groupby('category')['profit_margin'].mean().reset_index()
        category_margin = category_margin.nlargest(10, 'profit_margin')
        fig = px.bar(category_margin, y='category', x='profit_margin',
                     orientation='h',
                     title='Top 10 by Margin',
                     color='profit_margin',
                     color_continuous_scale='RdYlGn')
        fig.update_layout(showlegend=False)
        fig.update_xaxes(title_text="Profit Margin (%)")
        fig.update_yaxes(title_text="")
        st.plotly_chart(fig, use_container_width=True)
    
    # Product Performance Table
    st.subheader(" Top 50 Products by Revenue")
    if len(products_df) > 0:
        top_products = products_df.nlargest(50, 'total_revenue')
        top_products_display = top_products[['product_name', 'category', 'total_revenue', 
                                               'total_orders', 'total_units_sold', 'total_profit']].copy()
        top_products_display['total_revenue'] = top_products_display['total_revenue'].apply(lambda x: f"${x:,.2f}")
        top_products_display['total_profit'] = top_products_display['total_profit'].apply(lambda x: f"${x:,.2f}")
        top_products_display.columns = ['Product', 'Category', 'Revenue', 'Orders', 'Units Sold', 'Profit']
        st.dataframe(top_products_display, use_container_width=True, hide_index=True)
    
    # Units Sold by Category
    st.subheader(" Units Sold by Category")
    category_units = filtered_df.groupby('category')['quantity'].sum().reset_index()
    category_units = category_units.nlargest(15, 'quantity')
    fig = px.treemap(category_units, path=['category'], values='quantity',
                     title='Units Sold Treemap',
                     color='quantity',
                     color_continuous_scale='Blues')
    st.plotly_chart(fig, use_container_width=True)

### TAB 4: GEOGRAPHY ###
with tab4:
    st.header(" Geographic Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Revenue by Country")
        country_revenue = filtered_df.groupby('country')['total_amount'].sum().reset_index()
        fig = px.bar(country_revenue, x='country', y='total_amount',
                     title='Revenue by Country',
                     color='total_amount',
                     color_continuous_scale='Tealgrn')
        fig.update_layout(showlegend=False)
        fig.update_xaxes(title_text="Country")
        fig.update_yaxes(title_text="Revenue ($)")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Orders by Country")
        country_orders = filtered_df.groupby('country')['transaction_id'].count().reset_index()
        fig = px.pie(country_orders, values='transaction_id', names='country',
                     title='Order Distribution',
                     color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig, use_container_width=True)
    
    # Geographic Metrics Table
    st.subheader(" Geographic Performance Metrics")
    geo_metrics = filtered_df.groupby('country').agg({
        'total_amount': 'sum',
        'transaction_id': 'count',
        'customer_id': 'nunique',
        'profit': 'sum'
    }).reset_index()
    geo_metrics.columns = ['Country', 'Revenue', 'Orders', 'Customers', 'Profit']
    geo_metrics = geo_metrics.sort_values('Revenue', ascending=False)
    geo_metrics['Avg Order Value'] = geo_metrics['Revenue'] / geo_metrics['Orders']
    geo_metrics['Revenue'] = geo_metrics['Revenue'].apply(lambda x: f"${x:,.2f}")
    geo_metrics['Profit'] = geo_metrics['Profit'].apply(lambda x: f"${x:,.2f}")
    geo_metrics['Avg Order Value'] = geo_metrics['Avg Order Value'].apply(lambda x: f"${x:.2f}")
    st.dataframe(geo_metrics, use_container_width=True, hide_index=True)

### TAB 5: TRENDS ###
with tab5:
    st.header(" Trends & Seasonality")
    
    # Seasonality Analysis
    st.subheader(" Monthly Seasonality")
    filtered_df['month'] = filtered_df['transaction_date'].dt.month
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                   'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    monthly_season = filtered_df.groupby('month')['total_amount'].sum().reset_index()
    monthly_season['month_name'] = monthly_season['month'].apply(lambda x: month_names[x-1])
    
    fig = px.bar(monthly_season, x='month_name', y='total_amount',
                 title='Revenue by Month (Seasonality)',
                 color='total_amount',
                 color_continuous_scale='RdYlGn',
                 labels={'month_name': 'Month', 'total_amount': 'Total Revenue ($)'})
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)
    
    # Day of Week Analysis
    st.subheader(" Day of Week Performance")
    dow_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    filtered_df['day_of_week'] = filtered_df['transaction_date'].dt.dayofweek
    dow_data = filtered_df.groupby('day_of_week')['total_amount'].sum().reset_index()
    dow_data['day_name'] = dow_data['day_of_week'].apply(lambda x: dow_names[x])
    
    fig = px.line(dow_data, x='day_name', y='total_amount',
                  title='Revenue by Day of Week',
                  markers=True,
                  labels={'day_name': 'Day', 'total_amount': 'Revenue ($)'})
    fig.update_traces(line_color='#2E86AB', line_width=3, marker_size=10)
    st.plotly_chart(fig, use_container_width=True)
    
    # Payment Method Trends
    st.subheader(" Payment Method Trends")
    col1, col2 = st.columns(2)
    
    with col1:
        payment_dist = filtered_df.groupby('payment_method')['transaction_id'].count().reset_index()
        fig = px.pie(payment_dist, values='transaction_id', names='payment_method',
                     title='Payment Method Distribution',
                     hole=0.4)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        payment_avg = filtered_df.groupby('payment_method')['total_amount'].mean().reset_index()
        fig = px.bar(payment_avg, x='payment_method', y='total_amount',
                     title='Avg Transaction by Payment Method',
                     color='total_amount',
                     color_continuous_scale='Plasma')
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p> E-Commerce Sales Analytics Platform | Built with Streamlit & PostgreSQL</p>
    <p>Data refreshes every 10 minutes | Last updated: {}</p>
</div>
""".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")), unsafe_allow_html=True)


