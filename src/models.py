"""
Machine Learning Models for E-Commerce Analytics
- Customer Churn Prediction
- Demand Forecasting
- Customer Lifetime Value Prediction
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.metrics import (accuracy_score, precision_score, recall_score, 
                             f1_score, roc_auc_score, mean_absolute_error,
                             mean_squared_error, r2_score, confusion_matrix)
import xgboost as xgb
import joblib
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')


class ChurnPredictionModel:
    """
    Customer Churn Prediction Model
    Predicts which customers are likely to churn
    """
    
    def __init__(self, random_state=42):
        self.random_state = random_state
        self.model = None
        self.scaler = StandardScaler()
        self.feature_importance = None
        
    def prepare_features(self, df, customer_col='customer_id', date_col='transaction_date',
                        amount_col='total_amount', analysis_date=None):
        """
        Prepare features for churn prediction
        """
        if analysis_date is None:
            analysis_date = df[date_col].max()
        
        # Calculate customer features
        features = df.groupby(customer_col).agg({
            date_col: ['min', 'max', 'count'],
            amount_col: ['sum', 'mean', 'std', 'min', 'max']
        }).reset_index()
        
        features.columns = [customer_col, 'first_purchase', 'last_purchase', 'num_purchases',
                           'total_spent', 'avg_purchase', 'std_purchase', 'min_purchase', 'max_purchase']
        
        # Time-based features
        features['recency'] = (analysis_date - features['last_purchase']).dt.days
        features['customer_lifetime'] = (features['last_purchase'] - features['first_purchase']).dt.days
        features['customer_lifetime'] = features['customer_lifetime'].replace(0, 1)
        features['purchase_frequency'] = features['num_purchases'] / features['customer_lifetime']
        
        # Fill NaN
        features['std_purchase'] = features['std_purchase'].fillna(0)
        
        # Define churn (no purchase in last 90 days)
        features['is_churned'] = (features['recency'] > 90).astype(int)
        
        # Additional features
        features['avg_days_between_purchases'] = features['customer_lifetime'] / features['num_purchases']
        features['purchase_range'] = features['max_purchase'] - features['min_purchase']
        
        return features
    
    def train(self, features_df, target_col='is_churned'):
        """
        Train churn prediction model
        """
        # Select features
        feature_cols = ['recency', 'num_purchases', 'total_spent', 'avg_purchase',
                       'std_purchase', 'customer_lifetime', 'purchase_frequency',
                       'avg_days_between_purchases', 'purchase_range']
        
        X = features_df[feature_cols]
        y = features_df[target_col]
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=self.random_state, stratify=y
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train Random Forest model
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            min_samples_split=20,
            random_state=self.random_state,
            n_jobs=-1
        )
        
        self.model.fit(X_train_scaled, y_train)
        
        # Predictions
        y_pred = self.model.predict(X_test_scaled)
        y_pred_proba = self.model.predict_proba(X_test_scaled)[:, 1]
        
        # Evaluation
        metrics = {
            'accuracy': accuracy_score(y_test, y_pred),
            'precision': precision_score(y_test, y_pred),
            'recall': recall_score(y_test, y_pred),
            'f1_score': f1_score(y_test, y_pred),
            'roc_auc': roc_auc_score(y_test, y_pred_proba)
        }
        
        # Feature importance
        self.feature_importance = pd.DataFrame({
            'feature': feature_cols,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        # Cross-validation score
        cv_scores = cross_val_score(self.model, X_train_scaled, y_train, cv=5, scoring='accuracy')
        metrics['cv_accuracy_mean'] = cv_scores.mean()
        metrics['cv_accuracy_std'] = cv_scores.std()
        
        return metrics, confusion_matrix(y_test, y_pred)
    
    def predict_churn_probability(self, features_df):
        """
        Predict churn probability for customers
        """
        feature_cols = ['recency', 'num_purchases', 'total_spent', 'avg_purchase',
                       'std_purchase', 'customer_lifetime', 'purchase_frequency',
                       'avg_days_between_purchases', 'purchase_range']
        
        X = features_df[feature_cols]
        X_scaled = self.scaler.transform(X)
        
        churn_prob = self.model.predict_proba(X_scaled)[:, 1]
        return churn_prob
    
    def save_model(self, filepath):
        """Save trained model"""
        joblib.dump({
            'model': self.model,
            'scaler': self.scaler,
            'feature_importance': self.feature_importance
        }, filepath)
        print(f"✅ Model saved to {filepath}")
    
    def load_model(self, filepath):
        """Load trained model"""
        data = joblib.load(filepath)
        self.model = data['model']
        self.scaler = data['scaler']
        self.feature_importance = data['feature_importance']
        print(f"✅ Model loaded from {filepath}")


class DemandForecastModel:
    """
    Demand Forecasting Model
    Predicts future product demand
    """
    
    def __init__(self, random_state=42):
        self.random_state = random_state
        self.model = None
        self.scaler = StandardScaler()
    
    def prepare_features(self, df, product_col='product_id', date_col='transaction_date',
                        quantity_col='quantity'):
        """
        Prepare time-series features for demand forecasting
        """
        df = df.copy()
        df[date_col] = pd.to_datetime(df[date_col])
        
        # Aggregate daily demand by product
        daily_demand = df.groupby([product_col, date_col])[quantity_col].sum().reset_index()
        daily_demand.columns = [product_col, 'date', 'demand']
        
        # Create time-based features
        daily_demand['year'] = daily_demand['date'].dt.year
        daily_demand['month'] = daily_demand['date'].dt.month
        daily_demand['day'] = daily_demand['date'].dt.day
        daily_demand['day_of_week'] = daily_demand['date'].dt.dayofweek
        daily_demand['week_of_year'] = daily_demand['date'].dt.isocalendar().week
        daily_demand['is_weekend'] = (daily_demand['day_of_week'] >= 5).astype(int)
        daily_demand['is_month_start'] = daily_demand['date'].dt.is_month_start.astype(int)
        daily_demand['is_month_end'] = daily_demand['date'].dt.is_month_end.astype(int)
        
        # Lag features (previous days' demand)
        for product in daily_demand[product_col].unique():
            mask = daily_demand[product_col] == product
            for lag in [1, 7, 14, 30]:
                daily_demand.loc[mask, f'demand_lag_{lag}'] = daily_demand.loc[mask, 'demand'].shift(lag)
        
        # Rolling features
        for product in daily_demand[product_col].unique():
            mask = daily_demand[product_col] == product
            daily_demand.loc[mask, 'demand_rolling_7'] = daily_demand.loc[mask, 'demand'].rolling(7, min_periods=1).mean()
            daily_demand.loc[mask, 'demand_rolling_30'] = daily_demand.loc[mask, 'demand'].rolling(30, min_periods=1).mean()
        
        # Fill NaN with 0 for lag features
        lag_cols = [col for col in daily_demand.columns if 'lag' in col or 'rolling' in col]
        daily_demand[lag_cols] = daily_demand[lag_cols].fillna(0)
        
        return daily_demand
    
    def train(self, features_df, target_col='demand'):
        """
        Train demand forecasting model
        """
        # Select features
        feature_cols = ['year', 'month', 'day', 'day_of_week', 'week_of_year',
                       'is_weekend', 'is_month_start', 'is_month_end',
                       'demand_lag_1', 'demand_lag_7', 'demand_lag_14', 'demand_lag_30',
                       'demand_rolling_7', 'demand_rolling_30']
        
        # Remove rows with NaN in lag features (first few rows)
        features_df = features_df.dropna(subset=feature_cols)
        
        X = features_df[feature_cols]
        y = features_df[target_col]
        
        # Split data (time-series split - no shuffle)
        split_idx = int(len(X) * 0.8)
        X_train, X_test = X[:split_idx], X[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train XGBoost model
        self.model = xgb.XGBRegressor(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            random_state=self.random_state,
            n_jobs=-1
        )
        
        self.model.fit(X_train_scaled, y_train)
        
        # Predictions
        y_pred = self.model.predict(X_test_scaled)
        y_pred = np.maximum(y_pred, 0)  # Demand can't be negative
        
        # Evaluation
        metrics = {
            'mae': mean_absolute_error(y_test, y_pred),
            'rmse': np.sqrt(mean_squared_error(y_test, y_pred)),
            'mape': np.mean(np.abs((y_test - y_pred) / (y_test + 1))) * 100,  # +1 to avoid division by zero
            'r2_score': r2_score(y_test, y_pred)
        }
        
        return metrics
    
    def predict_demand(self, features_df):
        """
        Predict future demand
        """
        feature_cols = ['year', 'month', 'day', 'day_of_week', 'week_of_year',
                       'is_weekend', 'is_month_start', 'is_month_end',
                       'demand_lag_1', 'demand_lag_7', 'demand_lag_14', 'demand_lag_30',
                       'demand_rolling_7', 'demand_rolling_30']
        
        X = features_df[feature_cols]
        X_scaled = self.scaler.transform(X)
        
        predictions = self.model.predict(X_scaled)
        predictions = np.maximum(predictions, 0)
        
        return predictions
    
    def save_model(self, filepath):
        """Save trained model"""
        joblib.dump({
            'model': self.model,
            'scaler': self.scaler
        }, filepath)
        print(f"✅ Model saved to {filepath}")
    
    def load_model(self, filepath):
        """Load trained model"""
        data = joblib.load(filepath)
        self.model = data['model']
        self.scaler = data['scaler']
        print(f"✅ Model loaded from {filepath}")


class CLVPredictionModel:
    """
    Customer Lifetime Value Prediction Model
    """
    
    def __init__(self, random_state=42):
        self.random_state = random_state
        self.model = None
        self.scaler = StandardScaler()
    
    def prepare_features(self, df, customer_col='customer_id', date_col='transaction_date',
                        amount_col='total_amount'):
        """
        Prepare features for CLV prediction
        """
        # Calculate customer metrics
        features = df.groupby(customer_col).agg({
            amount_col: ['sum', 'mean', 'std', 'count'],
            date_col: ['min', 'max']
        }).reset_index()
        
        features.columns = [customer_col, 'historical_revenue', 'avg_order_value', 
                           'std_order_value', 'num_orders', 'first_purchase', 'last_purchase']
        
        # Calculate additional features
        features['customer_lifetime_days'] = (features['last_purchase'] - features['first_purchase']).dt.days
        features['customer_lifetime_days'] = features['customer_lifetime_days'].replace(0, 1)
        features['purchase_frequency'] = features['num_orders'] / features['customer_lifetime_days']
        features['days_since_last_purchase'] = (df[date_col].max() - features['last_purchase']).dt.days
        features['std_order_value'] = features['std_order_value'].fillna(0)
        
        # Calculate CLV (12-month projection)
        features['projected_purchases'] = features['purchase_frequency'] * 365
        features['clv_12m'] = features['projected_purchases'] * features['avg_order_value']
        
        return features
    
    def train(self, features_df, target_col='clv_12m'):
        """
        Train CLV prediction model
        """
        feature_cols = ['historical_revenue', 'avg_order_value', 'std_order_value',
                       'num_orders', 'customer_lifetime_days', 'purchase_frequency',
                       'days_since_last_purchase']
        
        X = features_df[feature_cols]
        y = features_df[target_col]
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=self.random_state
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train Random Forest Regressor
        self.model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=self.random_state,
            n_jobs=-1
        )
        
        self.model.fit(X_train_scaled, y_train)
        
        # Predictions
        y_pred = self.model.predict(X_test_scaled)
        
        # Evaluation
        metrics = {
            'mae': mean_absolute_error(y_test, y_pred),
            'rmse': np.sqrt(mean_squared_error(y_test, y_pred)),
            'r2_score': r2_score(y_test, y_pred),
            'mape': np.mean(np.abs((y_test - y_pred) / (y_test + 1))) * 100
        }
        
        return metrics
    
    def predict_clv(self, features_df):
        """
        Predict customer lifetime value
        """
        feature_cols = ['historical_revenue', 'avg_order_value', 'std_order_value',
                       'num_orders', 'customer_lifetime_days', 'purchase_frequency',
                       'days_since_last_purchase']
        
        X = features_df[feature_cols]
        X_scaled = self.scaler.transform(X)
        
        clv_predictions = self.model.predict(X_scaled)
        return clv_predictions
    
    def save_model(self, filepath):
        """Save trained model"""
        joblib.dump({
            'model': self.model,
            'scaler': self.scaler
        }, filepath)
        print(f"✅ Model saved to {filepath}")
    
    def load_model(self, filepath):
        """Load trained model"""
        data = joblib.load(filepath)
        self.model = data['model']
        self.scaler = data['scaler']
        print(f"✅ Model loaded from {filepath}")


def print_model_metrics(metrics, model_name="Model"):
    """
    Print formatted model evaluation metrics
    """
    print("\n" + "="*60)
    print(f"📊 {model_name} EVALUATION METRICS")
    print("="*60)
    
    for metric, value in metrics.items():
        print(f"  {metric.upper()}: {value:.4f}")
    
    print("="*60 + "\n")


