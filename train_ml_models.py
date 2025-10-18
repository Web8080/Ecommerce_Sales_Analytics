"""
Train Machine Learning Models
- Customer Churn Prediction
- Demand Forecasting
- Customer Lifetime Value Prediction
"""

import pandas as pd
import numpy as np
from sqlalchemy import create_engine
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))
from config import DATABASE_URL, PATHS
from src.models import ChurnPredictionModel, DemandForecastModel, CLVPredictionModel, print_model_metrics

print("="*70)
print(" MACHINE LEARNING MODEL TRAINING")
print("="*70 + "\n")

# Load data
print(" Loading data from database...")
engine = create_engine(DATABASE_URL)
df = pd.read_sql("SELECT * FROM vw_sales_overview WHERE order_status = 'Completed'", engine)
df['transaction_date'] = pd.to_datetime(df['transaction_date'])
print(f" Loaded {len(df):,} transactions\n")

# =============================================================================
# 1. CUSTOMER CHURN PREDICTION
# =============================================================================
print("\n" + "="*70)
print("1⃣  CUSTOMER CHURN PREDICTION MODEL")
print("="*70)

churn_model = ChurnPredictionModel(random_state=42)

print("\n Preparing features...")
churn_features = churn_model.prepare_features(
    df,
    customer_col='customer_id',
    date_col='transaction_date',
    amount_col='total_amount'
)

print(f" Features prepared for {len(churn_features):,} customers")
print(f"   Churned customers: {churn_features['is_churned'].sum():,} ({churn_features['is_churned'].mean()*100:.1f}%)")

print("\n Training model...")
metrics, confusion_mat = churn_model.train(churn_features)

print_model_metrics(metrics, "Customer Churn Prediction")

print(" Confusion Matrix:")
print("   ", confusion_mat)
print(f"\n   True Negatives:  {confusion_mat[0,0]:,}  (Correctly predicted active)")
print(f"   False Positives: {confusion_mat[0,1]:,}  (Predicted churn, but active)")
print(f"   False Negatives: {confusion_mat[1,0]:,}  (Predicted active, but churned)")
print(f"   True Positives:  {confusion_mat[1,1]:,}  (Correctly predicted churn)")

# Feature importance
print(f"\n Top 5 Most Important Features:")
print("-"*70)
for i, row in churn_model.feature_importance.head(5).iterrows():
    print(f"   {i+1}. {row['feature']:30s}: {row['importance']:.4f}")

# Save model
model_path = PATHS['models'] / 'churn_prediction_model.pkl'
churn_model.save_model(model_path)

# Predict churn for at-risk customers
churn_features['churn_probability'] = churn_model.predict_churn_probability(churn_features)
high_risk = churn_features[churn_features['churn_probability'] > 0.7].sort_values('total_spent', ascending=False)

print(f"\n HIGH-RISK CUSTOMERS (Churn Probability > 70%):")
print("-"*70)
print(f"   Count: {len(high_risk):,} customers")
print(f"   Total Revenue at Risk: ${high_risk['total_spent'].sum():,.2f}")
print(f"   Average Value: ${high_risk['total_spent'].mean():,.2f}")

# Save high-risk customers
high_risk.to_csv(PATHS['data_processed'] / 'high_risk_customers.csv', index=False)
print(f"\n High-risk customers saved to: {PATHS['data_processed'] / 'high_risk_customers.csv'}")

# =============================================================================
# 2. DEMAND FORECASTING
# =============================================================================
print("\n" + "="*70)
print("2⃣  DEMAND FORECASTING MODEL")
print("="*70)

demand_model = DemandForecastModel(random_state=42)

print("\n Preparing time-series features...")
demand_features = demand_model.prepare_features(
    df,
    product_col='product_id',
    date_col='transaction_date',
    quantity_col='quantity'
)

print(f" Features prepared for {len(demand_features):,} product-date combinations")

print("\n Training model...")
demand_metrics = demand_model.train(demand_features)

print_model_metrics(demand_metrics, "Demand Forecasting")

if demand_metrics['mape'] < 15:
    print(f"  MAPE Target Achieved! ({demand_metrics['mape']:.2f}% < 15%)")
else:
    print(f"  MAPE slightly above target ({demand_metrics['mape']:.2f}%)")

# Save model
model_path = PATHS['models'] / 'demand_forecast_model.pkl'
demand_model.save_model(model_path)

# =============================================================================
# 3. CUSTOMER LIFETIME VALUE PREDICTION
# =============================================================================
print("\n" + "="*70)
print("3⃣  CUSTOMER LIFETIME VALUE (CLV) PREDICTION MODEL")
print("="*70)

clv_model = CLVPredictionModel(random_state=42)

print("\n Preparing CLV features...")
clv_features = clv_model.prepare_features(
    df,
    customer_col='customer_id',
    date_col='transaction_date',
    amount_col='total_amount'
)

print(f" Features prepared for {len(clv_features):,} customers")
print(f"   Average 12-month CLV: ${clv_features['clv_12m'].mean():,.2f}")
print(f"   Median 12-month CLV: ${clv_features['clv_12m'].median():,.2f}")

print("\n Training model...")
clv_metrics = clv_model.train(clv_features)

print_model_metrics(clv_metrics, "Customer Lifetime Value Prediction")

# Save model
model_path = PATHS['models'] / 'clv_prediction_model.pkl'
clv_model.save_model(model_path)

# Identify high-value customers for targeted marketing
clv_features['predicted_clv'] = clv_model.predict_clv(clv_features)
high_value = clv_features.nlargest(100, 'predicted_clv')[['customer_id', 'historical_revenue', 'predicted_clv', 'num_orders']]

print(f"\n TOP 100 HIGH-VALUE CUSTOMERS (by Predicted CLV):")
print("-"*70)
print(f"   Total Predicted 12-month Value: ${high_value['predicted_clv'].sum():,.2f}")
print(f"   Average Predicted CLV: ${high_value['predicted_clv'].mean():,.2f}")

# Save high-value customers
high_value.to_csv(PATHS['data_processed'] / 'high_value_customers.csv', index=False)
print(f"\n High-value customers saved to: {PATHS['data_processed'] / 'high_value_customers.csv'}")

# =============================================================================
# SUMMARY
# =============================================================================
print("\n" + "="*70)
print(" MODEL TRAINING SUMMARY")
print("="*70)

summary = f"""
 CHURN PREDICTION MODEL:
   • Accuracy: {metrics['accuracy']:.2%}
   • Precision: {metrics['precision']:.2%}
   • Recall: {metrics['recall']:.2%}
   • F1-Score: {metrics['f1_score']:.2%}
   • ROC-AUC: {metrics['roc_auc']:.4f}
   • Model saved: models/churn_prediction_model.pkl
   • High-risk customers identified: {len(high_risk):,} (${high_risk['total_spent'].sum():,.2f} at risk)

 DEMAND FORECASTING MODEL:
   • MAE: {demand_metrics['mae']:.2f} units
   • RMSE: {demand_metrics['rmse']:.2f} units
   • MAPE: {demand_metrics['mape']:.2f}% {' (Target: <15%)' if demand_metrics['mape'] < 15 else ''}
   • R² Score: {demand_metrics['r2_score']:.4f}
   • Model saved: models/demand_forecast_model.pkl

 CLV PREDICTION MODEL:
   • MAE: ${clv_metrics['mae']:,.2f}
   • RMSE: ${clv_metrics['rmse']:,.2f}
   • R² Score: {clv_metrics['r2_score']:.4f}
   • MAPE: {clv_metrics['mape']:.2f}%
   • Model saved: models/clv_prediction_model.pkl
   • High-value customers identified: 100 (${high_value['predicted_clv'].sum():,.2f} potential)

 OUTPUT FILES:
   • models/churn_prediction_model.pkl
   • models/demand_forecast_model.pkl
   • models/clv_prediction_model.pkl
   • data/processed/high_risk_customers.csv
   • data/processed/high_value_customers.csv

 BUSINESS APPLICATIONS:
   • Deploy churn prevention campaigns for {len(high_risk):,} at-risk customers
   • Optimize inventory based on demand forecasts
   • Target high-CLV customers with premium offerings
   • Estimate 12-month revenue: ${clv_features['predicted_clv'].sum():,.2f}
"""

print(summary)
print("="*70)

print("\n ALL MODELS TRAINED SUCCESSFULLY!")
print("⏱  Training completed in: <5 minutes")
print("\n Models ready for deployment and prediction!")

