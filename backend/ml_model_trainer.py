"""
ML Model Trainer for MyWelthAI
Trains and saves machine learning models for financial predictions
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.linear_model import LinearRegression
import pickle
import os
import json

class MLModelTrainer:
    """Train and save ML models for financial predictions"""
    
    def __init__(self, model_dir='models'):
        self.model_dir = model_dir
        os.makedirs(model_dir, exist_ok=True)
        self.scaler = StandardScaler()
        
    def generate_training_data(self, n_samples=100):
        """Generate realistic training data for model training"""
        np.random.seed(42)
        
        data = []
        for _ in range(n_samples):
            # Features: day of month, day of week, week of year, category
            day_of_month = np.random.randint(1, 31)
            day_of_week = np.random.randint(0, 7)
            week_of_year = np.random.randint(1, 53)
            category = np.random.randint(0, 8)  # 0-7 expense categories
            is_weekend = 1 if day_of_week >= 5 else 0
            
            # Amount depends on category and day
            category_avg = [1500, 3000, 1000, 2000, 500, 1200, 800, 2500][category]
            noise = np.random.normal(0, category_avg * 0.2)
            amount = max(100, category_avg + noise + (is_weekend * 200))
            
            data.append({
                'day_of_month': day_of_month,
                'day_of_week': day_of_week,
                'week_of_year': week_of_year,
                'is_weekend': is_weekend,
                'category': category,
                'amount': amount
            })
        
        return pd.DataFrame(data)
    
    def train_spending_predictor(self):
        """Train model to predict spending amounts"""
        print("🤖 Training spending prediction model...")
        
        # Generate training data
        df = self.generate_training_data(n_samples=200)
        
        # Prepare features and target
        feature_cols = ['day_of_month', 'day_of_week', 'week_of_year', 'is_weekend', 'category']
        X = df[feature_cols].values
        y = df['amount'].values
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train Random Forest model
        model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
        model.fit(X_scaled, y)
        
        # Save model
        model_path = os.path.join(self.model_dir, 'spending_predictor.pkl')
        with open(model_path, 'wb') as f:
            pickle.dump(model, f)
        
        # Save scaler
        scaler_path = os.path.join(self.model_dir, 'spending_scaler.pkl')
        with open(scaler_path, 'wb') as f:
            pickle.dump(self.scaler, f)
        
        print(f"✅ Spending predictor trained and saved to {model_path}")
        return model
    
    def train_anomaly_detector(self):
        """Train model to detect spending anomalies"""
        print("🤖 Training anomaly detection model...")
        
        # Generate training data
        df = self.generate_training_data(n_samples=200)
        
        # Mark anomalies (top 5% of amounts as anomalies)
        threshold = df['amount'].quantile(0.95)
        df['is_anomaly'] = (df['amount'] > threshold).astype(int)
        
        # Prepare features and target
        feature_cols = ['day_of_month', 'day_of_week', 'week_of_year', 'is_weekend', 'category']
        X = df[feature_cols].values
        y = df['is_anomaly'].values
        
        # Scale features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Train classifier
        model = RandomForestClassifier(
            n_estimators=50,
            max_depth=8,
            random_state=42,
            n_jobs=-1
        )
        model.fit(X_scaled, y)
        
        # Save model and scaler
        model_path = os.path.join(self.model_dir, 'anomaly_detector.pkl')
        with open(model_path, 'wb') as f:
            pickle.dump(model, f)
        
        scaler_path = os.path.join(self.model_dir, 'anomaly_scaler.pkl')
        with open(scaler_path, 'wb') as f:
            pickle.dump(scaler, f)
        
        print(f"✅ Anomaly detector trained and saved to {model_path}")
        return model
    
    def train_category_predictor(self):
        """Train model to predict transaction category"""
        print("🤖 Training category prediction model...")
        
        # Generate training data
        df = self.generate_training_data(n_samples=300)
        
        # Prepare features and target
        feature_cols = ['day_of_month', 'day_of_week', 'week_of_year', 'is_weekend', 'amount']
        X = df[feature_cols].values
        y = df['category'].values
        
        # Scale features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Train classifier
        model = RandomForestClassifier(
            n_estimators=80,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
        model.fit(X_scaled, y)
        
        # Save model and scaler
        model_path = os.path.join(self.model_dir, 'category_predictor.pkl')
        with open(model_path, 'wb') as f:
            pickle.dump(model, f)
        
        scaler_path = os.path.join(self.model_dir, 'category_scaler.pkl')
        with open(scaler_path, 'wb') as f:
            pickle.dump(scaler, f)
        
        print(f"✅ Category predictor trained and saved to {model_path}")
        return model
    
    def train_trend_analyzer(self):
        """Train model for spending trend analysis"""
        print("🤖 Training trend analyzer model...")
        
        # Generate trend data
        np.random.seed(42)
        days = 30
        daily_spending = []
        
        for day in range(days):
            base = 5000
            trend = day * 50  # Increasing trend
            noise = np.random.normal(0, 500)
            daily_spending.append(base + trend + noise)
        
        # Prepare data
        X = np.array(range(days)).reshape(-1, 1)
        y = np.array(daily_spending)
        
        # Train linear regression for trend
        model = LinearRegression()
        model.fit(X, y)
        
        # Save model
        model_path = os.path.join(self.model_dir, 'trend_analyzer.pkl')
        with open(model_path, 'wb') as f:
            pickle.dump(model, f)
        
        print(f"✅ Trend analyzer trained and saved to {model_path}")
        return model
    
    def save_model_metadata(self):
        """Save metadata about trained models"""
        metadata = {
            'trained_at': datetime.now().isoformat(),
            'models': {
                'spending_predictor': {
                    'type': 'RandomForestRegressor',
                    'purpose': 'Predict spending amounts',
                    'file': 'spending_predictor.pkl'
                },
                'anomaly_detector': {
                    'type': 'RandomForestClassifier',
                    'purpose': 'Detect spending anomalies',
                    'file': 'anomaly_detector.pkl'
                },
                'category_predictor': {
                    'type': 'RandomForestClassifier',
                    'purpose': 'Predict transaction category',
                    'file': 'category_predictor.pkl'
                },
                'trend_analyzer': {
                    'type': 'LinearRegression',
                    'purpose': 'Analyze spending trends',
                    'file': 'trend_analyzer.pkl'
                }
            },
            'features': {
                'spending_predictor': ['day_of_month', 'day_of_week', 'week_of_year', 'is_weekend', 'category'],
                'anomaly_detector': ['day_of_month', 'day_of_week', 'week_of_year', 'is_weekend', 'category'],
                'category_predictor': ['day_of_month', 'day_of_week', 'week_of_year', 'is_weekend', 'amount']
            }
        }
        
        metadata_path = os.path.join(self.model_dir, 'model_metadata.json')
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"✅ Model metadata saved to {metadata_path}")
    
    def train_all_models(self):
        """Train all models"""
        print("\n" + "="*60)
        print("🚀 Starting ML Model Training Pipeline")
        print("="*60 + "\n")
        
        try:
            self.train_spending_predictor()
            self.train_anomaly_detector()
            self.train_category_predictor()
            self.train_trend_analyzer()
            self.save_model_metadata()
            
            print("\n" + "="*60)
            print("✅ All models trained successfully!")
            print("="*60)
            print(f"Models saved in: {os.path.abspath(self.model_dir)}")
            print("\nReady to use in backend with ml_service.py")
            return True
        except Exception as e:
            print(f"\n❌ Error during model training: {str(e)}")
            return False


if __name__ == '__main__':
    trainer = MLModelTrainer(model_dir='models')
    trainer.train_all_models()
