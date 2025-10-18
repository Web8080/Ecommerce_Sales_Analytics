"""
Utility functions for E-Commerce Analytics
"""

import pandas as pd
import numpy as np
from datetime import datetime

def calculate_rfm(df, customer_col='customer_id', date_col='transaction_date', 
                  amount_col='total_amount', analysis_date=None):
    """
    Calculate RFM (Recency, Frequency, Monetary) scores for customers
    
    Parameters:
    -----------
    df : DataFrame
        Transaction data
    customer_col : str
        Customer ID column name
    date_col : str
        Transaction date column name
    amount_col : str
        Transaction amount column name
    analysis_date : datetime
        Reference date for recency calculation (defaults to max date + 1 day)
    
    Returns:
    --------
    DataFrame with RFM scores
    """
    if analysis_date is None:
        analysis_date = df[date_col].max() + pd.Timedelta(days=1)
    
    rfm = df.groupby(customer_col).agg({
        date_col: lambda x: (analysis_date - x.max()).days,  # Recency
        customer_col: 'count',  # Frequency
        amount_col: 'sum'  # Monetary
    })
    
    rfm.columns = ['recency', 'frequency', 'monetary']
    rfm = rfm.reset_index()
    
    # Calculate RFM scores (1-5 scale, 5 being best)
    rfm['r_score'] = pd.qcut(rfm['recency'], 5, labels=[5, 4, 3, 2, 1], duplicates='drop')
    rfm['f_score'] = pd.qcut(rfm['frequency'].rank(method='first'), 5, labels=[1, 2, 3, 4, 5], duplicates='drop')
    rfm['m_score'] = pd.qcut(rfm['monetary'], 5, labels=[1, 2, 3, 4, 5], duplicates='drop')
    
    # Convert to numeric
    rfm['r_score'] = rfm['r_score'].astype(int)
    rfm['f_score'] = rfm['f_score'].astype(int)
    rfm['m_score'] = rfm['m_score'].astype(int)
    
    # Calculate RFM score
    rfm['rfm_score'] = rfm['r_score'] + rfm['f_score'] + rfm['m_score']
    
    # Segment customers
    def segment_customer(row):
        if row['rfm_score'] >= 13:
            return 'Champions'
        elif row['rfm_score'] >= 11:
            return 'Loyal Customers'
        elif row['rfm_score'] >= 9:
            return 'Potential Loyalist'
        elif row['rfm_score'] >= 7:
            return 'At Risk'
        elif row['rfm_score'] >= 5:
            return 'Needs Attention'
        else:
            return 'Lost'
    
    rfm['segment'] = rfm.apply(segment_customer, axis=1)
    
    return rfm


def calculate_customer_ltv(df, customer_col='customer_id', amount_col='total_amount',
                           date_col='transaction_date', months=12):
    """
    Calculate Customer Lifetime Value
    
    Parameters:
    -----------
    df : DataFrame
        Transaction data
    customer_col : str
        Customer ID column name
    amount_col : str
        Transaction amount column name
    date_col : str
        Transaction date column name
    months : int
        Number of months to project LTV
    
    Returns:
    --------
    DataFrame with LTV calculations
    """
    # Calculate customer metrics
    customer_metrics = df.groupby(customer_col).agg({
        amount_col: ['sum', 'mean', 'count'],
        date_col: ['min', 'max']
    }).reset_index()
    
    customer_metrics.columns = [customer_col, 'total_revenue', 'avg_order_value', 
                                 'num_orders', 'first_purchase', 'last_purchase']
    
    # Calculate customer lifetime in days
    customer_metrics['lifetime_days'] = (customer_metrics['last_purchase'] - 
                                          customer_metrics['first_purchase']).dt.days
    customer_metrics['lifetime_days'] = customer_metrics['lifetime_days'].replace(0, 1)  # Avoid division by zero
    
    # Calculate purchase frequency (orders per day)
    customer_metrics['purchase_frequency'] = customer_metrics['num_orders'] / customer_metrics['lifetime_days']
    
    # Project LTV
    days_in_period = months * 30
    customer_metrics['projected_orders'] = customer_metrics['purchase_frequency'] * days_in_period
    customer_metrics['ltv'] = customer_metrics['projected_orders'] * customer_metrics['avg_order_value']
    
    return customer_metrics


def cohort_analysis(df, customer_col='customer_id', date_col='transaction_date'):
    """
    Perform cohort analysis for customer retention
    
    Parameters:
    -----------
    df : DataFrame
        Transaction data
    customer_col : str
        Customer ID column name
    date_col : str
        Transaction date column name
    
    Returns:
    --------
    DataFrame with cohort retention rates
    """
    # Create cohort month (first purchase month)
    df[date_col] = pd.to_datetime(df[date_col])
    df['order_month'] = df[date_col].dt.to_period('M')
    
    cohort_data = df.groupby(customer_col).agg({
        date_col: 'min'
    }).reset_index()
    
    cohort_data.columns = [customer_col, 'cohort_date']
    cohort_data['cohort_month'] = cohort_data['cohort_date'].dt.to_period('M')
    
    # Merge cohort data with transactions
    df_cohort = df.merge(cohort_data, on=customer_col)
    
    # Calculate period number
    df_cohort['period_number'] = (df_cohort['order_month'] - df_cohort['cohort_month']).apply(lambda x: x.n)
    
    # Cohort size
    cohort_sizes = df_cohort.groupby('cohort_month')[customer_col].nunique()
    
    # Retention matrix
    cohort_matrix = df_cohort.groupby(['cohort_month', 'period_number'])[customer_col].nunique().reset_index()
    cohort_matrix = cohort_matrix.pivot(index='cohort_month', columns='period_number', values=customer_col)
    
    # Calculate retention rates
    cohort_retention = cohort_matrix.divide(cohort_sizes, axis=0) * 100
    
    return cohort_retention


def calculate_churn_features(df, customer_col='customer_id', date_col='transaction_date',
                             amount_col='total_amount', analysis_date=None):
    """
    Calculate features for churn prediction
    
    Parameters:
    -----------
    df : DataFrame
        Transaction data
    customer_col : str
        Customer ID column name
    date_col : str
        Transaction date column name
    amount_col : str
        Transaction amount column name
    analysis_date : datetime
        Reference date for calculating churn
    
    Returns:
    --------
    DataFrame with churn features
    """
    if analysis_date is None:
        analysis_date = df[date_col].max()
    
    # Calculate customer features
    features = df.groupby(customer_col).agg({
        date_col: ['min', 'max', 'count'],
        amount_col: ['sum', 'mean', 'std']
    }).reset_index()
    
    features.columns = [customer_col, 'first_purchase', 'last_purchase', 'num_purchases',
                        'total_spent', 'avg_purchase', 'std_purchase']
    
    # Calculate recency (days since last purchase)
    features['recency'] = (analysis_date - features['last_purchase']).dt.days
    
    # Calculate customer lifetime
    features['customer_lifetime'] = (features['last_purchase'] - features['first_purchase']).dt.days
    features['customer_lifetime'] = features['customer_lifetime'].replace(0, 1)
    
    # Calculate purchase frequency
    features['purchase_frequency'] = features['num_purchases'] / features['customer_lifetime']
    
    # Fill NaN std with 0
    features['std_purchase'] = features['std_purchase'].fillna(0)
    
    # Define churn (no purchase in last 90 days)
    features['is_churned'] = (features['recency'] > 90).astype(int)
    
    return features


def print_summary_stats(df, title="Summary Statistics"):
    """Print formatted summary statistics"""
    print("\n" + "="*70)
    print(f" {title}")
    print("="*70)
    
    if 'total_amount' in df.columns:
        print(f"Total Revenue: ${df['total_amount'].sum():,.2f}")
        print(f"Average Transaction: ${df['total_amount'].mean():.2f}")
        print(f"Median Transaction: ${df['total_amount'].median():.2f}")
    
    if 'customer_id' in df.columns:
        print(f"Unique Customers: {df['customer_id'].nunique():,}")
    
    if 'product_id' in df.columns:
        print(f"Unique Products: {df['product_id'].nunique():,}")
    
    print(f"Total Records: {len(df):,}")
    print("="*70 + "\n")


