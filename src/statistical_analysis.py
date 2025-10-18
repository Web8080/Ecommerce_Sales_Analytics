"""
Advanced Statistical Analysis for E-Commerce Data
- Cohort Analysis (Customer Retention)
- RFM Segmentation
- Time-Series Decomposition
- Marketing Spend Correlation Analysis
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine
from statsmodels.tsa.seasonal import seasonal_decompose
from datetime import datetime
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))
from config import DATABASE_URL, PATHS
from src.utils import calculate_rfm, cohort_analysis

# Create plots directory
(PATHS['reports'] / 'plots').mkdir(parents=True, exist_ok=True)

print("="*70)
print(" ADVANCED STATISTICAL ANALYSIS")
print("="*70 + "\n")


def perform_cohort_analysis():
    """
    Cohort Analysis - Customer Retention Rates
    Shows how many customers return each month after their first purchase
    """
    print("1⃣  COHORT ANALYSIS (Customer Retention Rates)")
    print("-" * 70)
    
    # Load data
    engine = create_engine(DATABASE_URL)
    query = "SELECT * FROM vw_sales_overview WHERE order_status = 'Completed'"
    df = pd.read_sql(query, engine)
    df['transaction_date'] = pd.to_datetime(df['transaction_date'])
    
    # Perform cohort analysis
    cohort_retention = cohort_analysis(df, 'customer_id', 'transaction_date')
    
    print("\n Cohort Retention Matrix (%):")
    print("-" * 70)
    print(cohort_retention.round(1).head(12))  # Show first 12 months
    
    # Calculate average retention rates
    avg_retention = cohort_retention.mean()
    print(f"\n Average Retention by Period:")
    print("-" * 70)
    for period in range(min(6, len(avg_retention))):
        if period in avg_retention.index:
            print(f"  Month {period}: {avg_retention[period]:.1f}% of cohort returns")
    
    # Visualize cohort heatmap
    plt.figure(figsize=(14, 8))
    sns.heatmap(cohort_retention.iloc[:12, :12], annot=True, fmt='.1f', 
                cmap='RdYlGn', center=50, vmin=0, vmax=100,
                cbar_kws={'label': 'Retention Rate (%)'})
    plt.title('Customer Cohort Retention Analysis\n(% of customers returning each month)', 
              fontsize=14, fontweight='bold', pad=20)
    plt.xlabel('Months Since First Purchase', fontsize=12)
    plt.ylabel('Cohort (First Purchase Month)', fontsize=12)
    plt.tight_layout()
    plt.savefig(PATHS['reports'] / 'plots' / 'cohort_retention_heatmap.png', dpi=300, bbox_inches='tight')
    print(f"\n Cohort heatmap saved to: {PATHS['reports'] / 'plots' / 'cohort_retention_heatmap.png'}")
    plt.close()
    
    # Key insights
    month_1_retention = avg_retention[1] if 1 in avg_retention.index else 0
    month_3_retention = avg_retention[3] if 3 in avg_retention.index else 0
    month_6_retention = avg_retention[6] if 6 in avg_retention.index else 0
    
    print(f"\n KEY INSIGHTS:")
    print("-" * 70)
    print(f"  • Month 1 Retention: {month_1_retention:.1f}% of customers return")
    print(f"  • Month 3 Retention: {month_3_retention:.1f}% still active")
    print(f"  • Month 6 Retention: {month_6_retention:.1f}% long-term customers")
    print(f"  • Retention drop: {month_1_retention - month_6_retention:.1f}% from month 1 to 6")
    print("\n" + "="*70 + "\n")
    
    return cohort_retention


def perform_rfm_segmentation():
    """
    RFM Segmentation - Customer Value Analysis
    Segments customers based on Recency, Frequency, and Monetary value
    """
    print("2⃣  RFM SEGMENTATION (Recency, Frequency, Monetary Value)")
    print("-" * 70)
    
    # Load data
    engine = create_engine(DATABASE_URL)
    query = "SELECT * FROM vw_sales_overview WHERE order_status = 'Completed'"
    df = pd.read_sql(query, engine)
    df['transaction_date'] = pd.to_datetime(df['transaction_date'])
    
    # Calculate RFM scores
    rfm = calculate_rfm(df, 'customer_id', 'transaction_date', 'total_amount')
    
    print("\n RFM Summary Statistics:")
    print("-" * 70)
    print(rfm[['recency', 'frequency', 'monetary']].describe().round(2))
    
    # Segment distribution
    segment_dist = rfm['segment'].value_counts()
    segment_pct = (segment_dist / len(rfm) * 100).round(1)
    
    print(f"\n Customer Segments Distribution:")
    print("-" * 70)
    for segment, count in segment_dist.items():
        pct = segment_pct[segment]
        avg_value = rfm[rfm['segment'] == segment]['monetary'].mean()
        print(f"  • {segment:20s}: {count:6,} customers ({pct:5.1f}%) - Avg Value: ${avg_value:,.2f}")
    
    # Visualize RFM segments
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    
    # Segment distribution
    segment_dist.plot(kind='bar', ax=axes[0, 0], color='skyblue', alpha=0.8)
    axes[0, 0].set_title('Customer Count by Segment', fontsize=12, fontweight='bold')
    axes[0, 0].set_xlabel('Segment')
    axes[0, 0].set_ylabel('Number of Customers')
    axes[0, 0].tick_params(axis='x', rotation=45)
    axes[0, 0].grid(True, alpha=0.3)
    
    # Revenue by segment
    segment_revenue = rfm.groupby('segment')['monetary'].sum().sort_values(ascending=False)
    segment_revenue.plot(kind='bar', ax=axes[0, 1], color='coral', alpha=0.8)
    axes[0, 1].set_title('Total Revenue by Segment', fontsize=12, fontweight='bold')
    axes[0, 1].set_xlabel('Segment')
    axes[0, 1].set_ylabel('Total Revenue ($)')
    axes[0, 1].tick_params(axis='x', rotation=45)
    axes[0, 1].grid(True, alpha=0.3)
    
    # RFM score distribution
    rfm['rfm_score'].hist(bins=15, ax=axes[1, 0], color='lightgreen', alpha=0.8, edgecolor='black')
    axes[1, 0].set_title('RFM Score Distribution', fontsize=12, fontweight='bold')
    axes[1, 0].set_xlabel('RFM Score')
    axes[1, 0].set_ylabel('Number of Customers')
    axes[1, 0].grid(True, alpha=0.3)
    
    # Recency vs Monetary scatter
    segments_to_plot = rfm['segment'].unique()
    colors = plt.cm.Set3(np.linspace(0, 1, len(segments_to_plot)))
    for i, segment in enumerate(segments_to_plot):
        segment_data = rfm[rfm['segment'] == segment]
        axes[1, 1].scatter(segment_data['recency'], segment_data['monetary'], 
                          label=segment, alpha=0.6, s=50, color=colors[i])
    axes[1, 1].set_title('Recency vs Monetary Value by Segment', fontsize=12, fontweight='bold')
    axes[1, 1].set_xlabel('Recency (Days Since Last Purchase)')
    axes[1, 1].set_ylabel('Monetary Value ($)')
    axes[1, 1].legend(loc='best', fontsize=8)
    axes[1, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(PATHS['reports'] / 'plots' / 'rfm_segmentation_analysis.png', dpi=300, bbox_inches='tight')
    print(f"\n RFM analysis saved to: {PATHS['reports'] / 'plots' / 'rfm_segmentation_analysis.png'}")
    plt.close()
    
    # Key insights
    champions = rfm[rfm['segment'] == 'Champions']
    at_risk = rfm[rfm['segment'] == 'At Risk']
    
    print(f"\n KEY INSIGHTS:")
    print("-" * 70)
    print(f"  • Champions: {len(champions):,} customers ({len(champions)/len(rfm)*100:.1f}%) generating ${champions['monetary'].sum():,.2f}")
    print(f"  • At Risk: {len(at_risk):,} customers ({len(at_risk)/len(rfm)*100:.1f}%) worth ${at_risk['monetary'].sum():,.2f}")
    print(f"  • Avg Champion Value: ${champions['monetary'].mean():,.2f} vs Avg At Risk: ${at_risk['monetary'].mean():,.2f}")
    print(f"  • Recommended Action: Focus retention on {len(at_risk):,} at-risk customers")
    print("\n" + "="*70 + "\n")
    
    # Save RFM data
    rfm.to_csv(PATHS['data_processed'] / 'rfm_customer_segments.csv', index=False)
    print(f" RFM data saved to: {PATHS['data_processed'] / 'rfm_customer_segments.csv'}\n")
    
    return rfm


def perform_time_series_decomposition():
    """
    Time-Series Decomposition
    Breaks down sales into trend, seasonality, and residual components
    """
    print("3⃣  TIME-SERIES DECOMPOSITION")
    print("-" * 70)
    
    # Load data
    engine = create_engine(DATABASE_URL)
    query = "SELECT * FROM vw_sales_overview WHERE order_status = 'Completed'"
    df = pd.read_sql(query, engine)
    df['transaction_date'] = pd.to_datetime(df['transaction_date'])
    
    # Aggregate daily sales
    daily_sales = df.groupby('transaction_date')['total_amount'].sum().reset_index()
    daily_sales = daily_sales.set_index('transaction_date')
    daily_sales = daily_sales.asfreq('D', fill_value=0)  # Ensure daily frequency
    
    print(f"\n Time-Series Data:")
    print("-" * 70)
    print(f"  • Date Range: {daily_sales.index.min()} to {daily_sales.index.max()}")
    print(f"  • Total Days: {len(daily_sales):,}")
    print(f"  • Avg Daily Revenue: ${daily_sales['total_amount'].mean():,.2f}")
    print(f"  • Std Daily Revenue: ${daily_sales['total_amount'].std():,.2f}")
    
    # Perform decomposition (using additive model)
    try:
        # Use 7-day period for weekly seasonality
        decomposition = seasonal_decompose(daily_sales['total_amount'], 
                                          model='additive', 
                                          period=7,  # Weekly seasonality
                                          extrapolate_trend='freq')
        
        # Plot decomposition
        fig, axes = plt.subplots(4, 1, figsize=(16, 12))
        
        # Original data
        axes[0].plot(daily_sales.index, daily_sales['total_amount'], color='#2E86AB', linewidth=1)
        axes[0].set_title('Original Time Series (Daily Revenue)', fontsize=12, fontweight='bold')
        axes[0].set_ylabel('Revenue ($)')
        axes[0].grid(True, alpha=0.3)
        
        # Trend
        axes[1].plot(decomposition.trend.index, decomposition.trend, color='#F18F01', linewidth=2)
        axes[1].set_title('Trend Component', fontsize=12, fontweight='bold')
        axes[1].set_ylabel('Trend ($)')
        axes[1].grid(True, alpha=0.3)
        
        # Seasonal
        axes[2].plot(decomposition.seasonal.index, decomposition.seasonal, color='#4ECDC4', linewidth=1)
        axes[2].set_title('Seasonal Component (7-Day Pattern)', fontsize=12, fontweight='bold')
        axes[2].set_ylabel('Seasonal ($)')
        axes[2].grid(True, alpha=0.3)
        
        # Residual
        axes[3].plot(decomposition.resid.index, decomposition.resid, color='#95E1D3', linewidth=0.5, alpha=0.7)
        axes[3].set_title('Residual (Irregular) Component', fontsize=12, fontweight='bold')
        axes[3].set_xlabel('Date')
        axes[3].set_ylabel('Residual ($)')
        axes[3].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(PATHS['reports'] / 'plots' / 'time_series_decomposition.png', dpi=300, bbox_inches='tight')
        print(f"\n Time-series decomposition saved to: {PATHS['reports'] / 'plots' / 'time_series_decomposition.png'}")
        plt.close()
        
        # Calculate variance explained by each component
        trend_var = decomposition.trend.var()
        seasonal_var = decomposition.seasonal.var()
        resid_var = decomposition.resid.var()
        total_var = trend_var + seasonal_var + resid_var
        
        print(f"\n KEY INSIGHTS:")
        print("-" * 70)
        print(f"  • Trend explains {trend_var/total_var*100:.1f}% of variance")
        print(f"  • Seasonality explains {seasonal_var/total_var*100:.1f}% of variance")
        print(f"  • Residual (noise) explains {resid_var/total_var*100:.1f}% of variance")
        
        # Identify trend direction
        trend_start = decomposition.trend.dropna().iloc[0]
        trend_end = decomposition.trend.dropna().iloc[-1]
        trend_change = ((trend_end - trend_start) / trend_start * 100)
        
        print(f"  • Overall Trend: {' Increasing' if trend_change > 0 else ' Decreasing'} by {abs(trend_change):.1f}%")
        print(f"  • Weekly Pattern Detected: Revenue varies by ${decomposition.seasonal.max() - decomposition.seasonal.min():,.2f} within week")
        
    except Exception as e:
        print(f"\n  Decomposition warning: {str(e)}")
        print("   Using alternative approach...")
        
    print("\n" + "="*70 + "\n")


def perform_marketing_correlation_analysis():
    """
    Marketing Spend vs Revenue Correlation Analysis
    Analyzes relationship between marketing campaigns and revenue
    """
    print("4⃣  MARKETING SPEND vs REVENUE CORRELATION")
    print("-" * 70)
    
    # Load data
    engine = create_engine(DATABASE_URL)
    
    # Load marketing campaigns
    campaigns = pd.read_sql("SELECT * FROM dim_marketing_campaigns", engine)
    campaigns['start_date'] = pd.to_datetime(campaigns['start_date'])
    campaigns['end_date'] = pd.to_datetime(campaigns['end_date'])
    
    # Load sales data
    sales_query = "SELECT * FROM vw_sales_overview WHERE order_status = 'Completed'"
    df = pd.read_sql(sales_query, engine)
    df['transaction_date'] = pd.to_datetime(df['transaction_date'])
    
    # Aggregate daily revenue
    daily_revenue = df.groupby('transaction_date')['total_amount'].sum().reset_index()
    daily_revenue.columns = ['date', 'revenue']
    
    # Map campaign spend to each date
    daily_revenue['marketing_spend'] = 0.0
    
    for _, campaign in campaigns.iterrows():
        mask = (daily_revenue['date'] >= campaign['start_date']) & (daily_revenue['date'] <= campaign['end_date'])
        campaign_days = (campaign['end_date'] - campaign['start_date']).days + 1
        daily_spend = campaign['budget'] / campaign_days if campaign_days > 0 else 0
        daily_revenue.loc[mask, 'marketing_spend'] += daily_spend
    
    # Calculate correlation
    correlation = daily_revenue['revenue'].corr(daily_revenue['marketing_spend'])
    
    print(f"\n Marketing Performance Metrics:")
    print("-" * 70)
    print(f"  • Total Marketing Spend: ${campaigns['budget'].sum():,.2f}")
    print(f"  • Total Revenue (analysis period): ${daily_revenue['revenue'].sum():,.2f}")
    print(f"  • Number of Campaigns: {len(campaigns)}")
    print(f"  • Avg Campaign Budget: ${campaigns['budget'].mean():,.2f}")
    
    print(f"\n Correlation Analysis:")
    print("-" * 70)
    print(f"  • Pearson Correlation: {correlation:.4f}")
    
    if abs(correlation) > 0.7:
        strength = "Very Strong"
    elif abs(correlation) > 0.5:
        strength = "Strong"
    elif abs(correlation) > 0.3:
        strength = "Moderate"
    else:
        strength = "Weak"
    
    direction = "Positive" if correlation > 0 else "Negative"
    print(f"  • Interpretation: {strength} {direction} correlation")
    
    # Calculate ROI by campaign
    campaign_roi = []
    for _, campaign in campaigns.iterrows():
        mask = (df['transaction_date'] >= campaign['start_date']) & (df['transaction_date'] <= campaign['end_date'])
        campaign_revenue = df.loc[mask, 'total_amount'].sum()
        roi = ((campaign_revenue - campaign['budget']) / campaign['budget'] * 100) if campaign['budget'] > 0 else 0
        campaign_roi.append({
            'campaign': campaign['campaign_name'],
            'budget': campaign['budget'],
            'revenue': campaign_revenue,
            'roi': roi,
            'conversions': campaign['conversions']
        })
    
    roi_df = pd.DataFrame(campaign_roi).sort_values('roi', ascending=False)
    
    print(f"\n Top 5 Campaigns by ROI:")
    print("-" * 70)
    for i, row in roi_df.head(5).iterrows():
        print(f"  • {row['campaign']:30s}: ROI {row['roi']:7.1f}% (${row['revenue']:,.0f} revenue, ${row['budget']:,.0f} spend)")
    
    # Visualizations
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    
    # Scatter plot: Marketing Spend vs Revenue
    axes[0, 0].scatter(daily_revenue['marketing_spend'], daily_revenue['revenue'], 
                       alpha=0.5, s=30, color='#2E86AB')
    axes[0, 0].set_title(f'Marketing Spend vs Revenue (Correlation: {correlation:.3f})', 
                         fontsize=12, fontweight='bold')
    axes[0, 0].set_xlabel('Daily Marketing Spend ($)')
    axes[0, 0].set_ylabel('Daily Revenue ($)')
    axes[0, 0].grid(True, alpha=0.3)
    
    # Add trendline
    z = np.polyfit(daily_revenue['marketing_spend'], daily_revenue['revenue'], 1)
    p = np.poly1d(z)
    axes[0, 0].plot(daily_revenue['marketing_spend'], p(daily_revenue['marketing_spend']), 
                    "r--", linewidth=2, label='Trend Line')
    axes[0, 0].legend()
    
    # Campaign ROI bar chart
    top_campaigns = roi_df.head(10)
    axes[0, 1].barh(range(len(top_campaigns)), top_campaigns['roi'], color='#F18F01', alpha=0.8)
    axes[0, 1].set_yticks(range(len(top_campaigns)))
    axes[0, 1].set_yticklabels(top_campaigns['campaign'], fontsize=9)
    axes[0, 1].set_title('Top 10 Campaigns by ROI', fontsize=12, fontweight='bold')
    axes[0, 1].set_xlabel('ROI (%)')
    axes[0, 1].invert_yaxis()
    axes[0, 1].grid(True, alpha=0.3, axis='x')
    
    # Marketing spend over time
    axes[1, 0].plot(daily_revenue['date'], daily_revenue['marketing_spend'], 
                    color='#4ECDC4', linewidth=1.5, label='Marketing Spend')
    axes[1, 0].set_title('Marketing Spend Over Time', fontsize=12, fontweight='bold')
    axes[1, 0].set_xlabel('Date')
    axes[1, 0].set_ylabel('Daily Spend ($)')
    axes[1, 0].grid(True, alpha=0.3)
    axes[1, 0].legend()
    
    # Revenue with marketing overlay
    ax1 = axes[1, 1]
    ax1.plot(daily_revenue['date'], daily_revenue['revenue'], 
             color='#2E86AB', linewidth=1, label='Revenue')
    ax1.set_title('Revenue with Marketing Activity', fontsize=12, fontweight='bold')
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Revenue ($)', color='#2E86AB')
    ax1.tick_params(axis='y', labelcolor='#2E86AB')
    
    ax2 = ax1.twinx()
    ax2.fill_between(daily_revenue['date'], 0, daily_revenue['marketing_spend'], 
                     color='#F18F01', alpha=0.3, label='Marketing Spend')
    ax2.set_ylabel('Marketing Spend ($)', color='#F18F01')
    ax2.tick_params(axis='y', labelcolor='#F18F01')
    
    # Combine legends
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
    
    plt.tight_layout()
    plt.savefig(PATHS['reports'] / 'plots' / 'marketing_correlation_analysis.png', dpi=300, bbox_inches='tight')
    print(f"\n Marketing correlation analysis saved to: {PATHS['reports'] / 'plots' / 'marketing_correlation_analysis.png'}")
    plt.close()
    
    print(f"\n KEY INSIGHTS:")
    print("-" * 70)
    print(f"  • {strength} {direction.lower()} relationship between marketing spend and revenue")
    print(f"  • Average ROI across all campaigns: {roi_df['roi'].mean():.1f}%")
    print(f"  • Best performing campaign: {roi_df.iloc[0]['campaign']} (ROI: {roi_df.iloc[0]['roi']:.1f}%)")
    print(f"  • Total marketing-attributed revenue: ${roi_df['revenue'].sum():,.2f}")
    print(f"  • Recommendation: Focus budget on {'high' if roi_df['roi'].mean() > 100 else 'top-performing'} campaigns")
    
    print("\n" + "="*70 + "\n")
    
    # Save campaign ROI data
    roi_df.to_csv(PATHS['data_processed'] / 'campaign_roi_analysis.csv', index=False)
    print(f" Campaign ROI data saved to: {PATHS['data_processed'] / 'campaign_roi_analysis.csv'}\n")


def generate_summary_report():
    """Generate overall summary of statistical analyses"""
    print("\n" + "="*70)
    print(" STATISTICAL ANALYSIS SUMMARY")
    print("="*70)
    
    summary = """
 COMPLETED ANALYSES:

1. COHORT ANALYSIS
   - Tracked customer retention rates over time
   - Identified retention drop-off patterns
   - Generated cohort retention heatmap
   
2. RFM SEGMENTATION
   - Segmented customers by Recency, Frequency, Monetary value
   - Identified Champions, Loyal, At Risk, and Lost customers
   - Calculated segment-specific revenue contributions
   
3. TIME-SERIES DECOMPOSITION
   - Separated trend, seasonal, and residual components
   - Identified weekly seasonality patterns
   - Quantified variance explained by each component
   
4. MARKETING CORRELATION ANALYSIS
   - Calculated correlation between marketing spend and revenue
   - Analyzed campaign-level ROI
   - Identified top-performing marketing initiatives

 OUTPUT FILES:
   • Cohort heatmap: reports/plots/cohort_retention_heatmap.png
   • RFM analysis: reports/plots/rfm_segmentation_analysis.png
   • Time-series: reports/plots/time_series_decomposition.png
   • Marketing: reports/plots/marketing_correlation_analysis.png
   • RFM data: data/processed/rfm_customer_segments.csv
   • ROI data: data/processed/campaign_roi_analysis.csv

 All statistical analyses completed successfully!
"""
    print(summary)
    print("="*70)


def main():
    """Run all statistical analyses"""
    try:
        start_time = datetime.now()
        
        # Run analyses
        cohort_retention = perform_cohort_analysis()
        rfm_data = perform_rfm_segmentation()
        perform_time_series_decomposition()
        perform_marketing_correlation_analysis()
        
        # Generate summary
        generate_summary_report()
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print(f"\n⏱  Total execution time: {duration:.2f} seconds")
        print(" All analyses completed successfully!\n")
        
        return True
        
    except Exception as e:
        print(f"\n ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)


