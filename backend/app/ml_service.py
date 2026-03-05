"""
Machine Learning Service for MyWelthAI
Provides predictive analytics, anomaly detection, and financial insights
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from app.models import Transaction
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import pickle
import os
import warnings
warnings.filterwarnings('ignore')


class MLService:
    """Machine Learning service for financial analysis"""
    
    # Application models directory (backend/app/models) and repository ML_Models
    APP_MODELS_DIR = os.path.join(os.path.dirname(__file__), 'models')
    ML_MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ML_Models')
    MODEL_DIR = APP_MODELS_DIR
    
    # Cached models
    _models = {}
    _scalers = {}
    
    @classmethod
    def load_model(cls, model_name):
        """Load a trained model from disk"""
        if model_name in cls._models:
            return cls._models[model_name]
        # Look in app models first, then ML_Models folder at repo root
        candidates = [
            os.path.join(cls.APP_MODELS_DIR, f'{model_name}.pkl'),
            os.path.join(cls.ML_MODELS_DIR, f'{model_name}.pkl')
        ]
        for model_path in candidates:
            print(f"MLService: checking model path {model_path}")
            if os.path.exists(model_path):
                print(f"MLService: found model file at {model_path}, attempting to load")
                try:
                    with open(model_path, 'rb') as f:
                        try:
                            model = pickle.load(f)
                        except Exception as pe:
                            print(f"MLService: pickle.load failed for {model_path}: {pe}")
                            # try cloudpickle for objects pickled with it
                            try:
                                import cloudpickle
                                f.seek(0)
                                model = cloudpickle.load(f)
                            except Exception as ce:
                                print(f"MLService: cloudpickle.load failed for {model_path}: {ce}")
                                raise
                    cls._models[model_name] = model
                    print(f"MLService: loaded model {model_name} from {model_path}")
                    return model
                except Exception as e:
                    import traceback
                    print(f"MLService: Could not load model {model_name} from {model_path}: {e}")
                    traceback.print_exc()
        return None
    
    @classmethod
    def load_scaler(cls, scaler_name):
        """Load a trained scaler from disk"""
        if scaler_name in cls._scalers:
            return cls._scalers[scaler_name]
        
        candidates = [
            os.path.join(cls.APP_MODELS_DIR, f'{scaler_name}.pkl'),
            os.path.join(cls.ML_MODELS_DIR, f'{scaler_name}.pkl')
        ]
        for scaler_path in candidates:
            if os.path.exists(scaler_path):
                try:
                    with open(scaler_path, 'rb') as f:
                        scaler = pickle.load(f)
                    cls._scalers[scaler_name] = scaler
                    return scaler
                except Exception as e:
                    print(f"Warning: Could not load scaler {scaler_name} from {scaler_path}: {str(e)}")
        return None

    @classmethod
    def _load_feature_names(cls):
        """Attempt to load feature names or metadata from model_features.pkl"""
        candidates = [
            os.path.join(cls.APP_MODELS_DIR, 'model_features.pkl'),
            os.path.join(cls.ML_MODELS_DIR, 'model_features.pkl')
        ]
        for p in candidates:
            if os.path.exists(p):
                try:
                    with open(p, 'rb') as f:
                        return pickle.load(f)
                except Exception as e:
                    print(f"Warning: could not load feature metadata from {p}: {e}")
        return None

    @classmethod
    def predict_overspending_risk(cls, user_id, days=30):
        """Predict overspending risk for a user.

        First tries to use the trained model if available, otherwise uses a formula-based approach.
        Returns a dict with `risk_score` (0-1), `risk_label`, and debug info.
        """
        try:
            # Gather transaction features for the last `days`
            start_date = datetime.utcnow() - timedelta(days=days)
            transactions = Transaction.query.filter(
                Transaction.user_id == user_id,
                Transaction.created_at >= start_date
            ).all()

            expenses = [t.amount for t in transactions if getattr(t, 'type', None) == 'expense']
            incomes = [t.amount for t in transactions if getattr(t, 'type', None) == 'income']

            total_expense = float(sum(expenses)) if expenses else 0.0
            total_income = float(sum(incomes)) if incomes else 0.0
            # avoid divide-by-zero
            expense_ratio = float(total_expense / total_income) if total_income > 0 else 0.0
            savings_rate = float((total_income - total_expense) / total_income) if total_income > 0 else 0.0

            # Category-specific percentages (food, shopping)
            cat_totals = {}
            for t in transactions:
                if getattr(t, 'type', None) != 'expense':
                    continue
                cat = (t.category or 'uncategorized').lower()
                cat_totals[cat] = cat_totals.get(cat, 0.0) + t.amount

            def pct_for_keywords(keywords):
                s = 0.0
                for cat, amt in cat_totals.items():
                    for kw in keywords:
                        if kw in cat:
                            s += amt
                            break
                return float(s / total_expense) if total_expense > 0 else 0.0

            food_pct = pct_for_keywords(['food', 'restaurant', 'dining', 'meal'])
            shopping_pct = pct_for_keywords(['shop', 'shopping', 'retail'])

            feature_names = ['total_income', 'total_expense', 'expense_ratio', 'savings_rate', 'food_pct', 'shopping_pct']
            feature_map = {
                'total_income': total_income,
                'total_expense': total_expense,
                'expense_ratio': expense_ratio,
                'savings_rate': savings_rate,
                'food_pct': food_pct,
                'shopping_pct': shopping_pct,
            }

            X = [float(feature_map.get(name, 0.0)) for name in feature_names]
            X_arr = np.array(X).reshape(1, -1)

            # Try to use the trained model first
            model = cls.load_model('overspending_risk_model')
            risk_score = None
            model_used = False

            if model is not None:
                try:
                    scaler = cls.load_scaler('overspending_scaler') or cls.load_scaler('scaler')
                    X_scaled = X_arr
                    if scaler is not None:
                        try:
                            X_scaled = scaler.transform(X_arr)
                        except Exception:
                            pass
                    
                    if hasattr(model, 'predict_proba'):
                        prob = model.predict_proba(X_scaled)
                        risk_score = float(prob[0][1])
                    else:
                        pred = model.predict(X_scaled)
                        try:
                            risk_score = float(pred[0])
                        except Exception:
                            risk_score = float(pred)
                    
                    model_used = True
                    print(f"MLService: using trained model for overspending risk prediction for user {user_id}")
                except Exception as e:
                    print(f"MLService: model prediction failed ({e}), falling back to formula")

            # Fallback: if model not found or failed, use formula-based calculation
            if not model_used or risk_score is None:
                # Formula: risk increases with expense_ratio and decreases with savings_rate
                # Also consider high food/shopping percentages
                risk_score = (expense_ratio * 0.4) + (1 - savings_rate) * 0.3 + (food_pct * 0.2) + (shopping_pct * 0.1)
                risk_score = float(risk_score)
                print(f"MLService: using formula-based prediction for user {user_id}: risk_score={risk_score}")

            # Normalize and label
            risk_score = max(0.0, min(1.0, float(risk_score)))
            if risk_score >= 0.75:
                label = 'high'
            elif risk_score >= 0.4:
                label = 'medium'
            else:
                label = 'low'

            return {
                'risk_score': round(risk_score, 3),
                'risk_label': label,
                'based_on_days': days,
                'features_used': feature_names,
                'model_used': model_used
            }

        except Exception as e:
            print(f"Error in predict_overspending_risk: {e}")
            return {
                'risk_score': None,
                'risk_label': 'unknown',
                'based_on_days': days,
                'features_used': None,
                'error': str(e)
            }
    
    @staticmethod
    def get_spending_trends(user_id, days=30):
        """
        Analyze spending trends over the last N days
        
        Args:
            user_id: User ID
            days: Number of days to analyze
            
        Returns:
            dict with spending trends
        """
        try:
            # Get transactions for the period
            start_date = datetime.utcnow() - timedelta(days=days)
            transactions = Transaction.query.filter(
                Transaction.user_id == user_id,
                Transaction.type == 'expense',
                Transaction.created_at >= start_date
            ).all()
            
            if not transactions:
                return {
                    'total_spent': 0,
                    'daily_average': 0,
                    'highest_spending_day': None,
                    'lowest_spending_day': None,
                    'trend': 'insufficient_data'
                }
            
            # Convert to DataFrame
            data = pd.DataFrame([
                {
                    'date': t.created_at.date(),
                    'amount': t.amount,
                    'category': t.category
                } for t in transactions
            ])
            
            # Calculate metrics
            daily_spending = data.groupby('date')['amount'].sum()
            total_spent = data['amount'].sum()
            daily_average = daily_spending.mean()
            
            # Detect trend (increasing or decreasing)
            if len(daily_spending) > 1:
                first_half_avg = daily_spending.iloc[:len(daily_spending)//2].mean()
                second_half_avg = daily_spending.iloc[len(daily_spending)//2:].mean()
                trend = 'increasing' if second_half_avg > first_half_avg else 'decreasing'
            else:
                trend = 'stable'
            
            return {
                'total_spent': round(float(total_spent), 2),
                'daily_average': round(float(daily_average), 2),
                'highest_spending_day': float(daily_spending.max()) if len(daily_spending) > 0 else 0,
                'lowest_spending_day': float(daily_spending.min()) if len(daily_spending) > 0 else 0,
                'trend': trend,
                'transaction_count': len(transactions)
            }
        except Exception as e:
            print(f"Error in get_spending_trends: {str(e)}")
            return {'error': str(e)}
    
    @staticmethod
    def predict_monthly_spending(user_id):
        """
        Predict next month's spending using historical data
        
        Args:
            user_id: User ID
            
        Returns:
            dict with spending prediction
        """
        try:
            # Get last 3 months of transaction data
            start_date = datetime.utcnow() - timedelta(days=90)
            transactions = Transaction.query.filter(
                Transaction.user_id == user_id,
                Transaction.type == 'expense',
                Transaction.created_at >= start_date
            ).all()
            
            if len(transactions) < 5:
                return {
                    'predicted_spending': 0,
                    'confidence': 'low',
                    'message': 'Insufficient data for prediction'
                }
            
            # Prepare data
            data = pd.DataFrame([
                {
                    'date': t.created_at.date(),
                    'amount': t.amount,
                    'category': t.category
                } for t in transactions
            ])
            
            # Monthly aggregation
            data['month'] = pd.to_datetime(data['date']).dt.to_period('M')
            monthly_spending = data.groupby('month')['amount'].sum().values
            
            if len(monthly_spending) < 2:
                avg_spending = float(monthly_spending[0]) if len(monthly_spending) > 0 else 0
                return {
                    'predicted_spending': round(avg_spending, 2),
                    'confidence': 'low',
                    'message': 'Based on limited data'
                }
            
            # Simple trend-based prediction
            x = np.arange(len(monthly_spending)).reshape(-1, 1)
            y = monthly_spending.reshape(-1, 1)
            
            model = RandomForestRegressor(n_estimators=10, random_state=42)
            model.fit(x, y.ravel())
            
            # Predict next month
            next_month = np.array([[len(monthly_spending)]])
            prediction = model.predict(next_month)[0]
            
            # Calculate confidence based on variance
            variance = np.var(monthly_spending)
            confidence = 'high' if variance < np.mean(monthly_spending) * 0.3 else 'medium'
            
            return {
                'predicted_spending': round(float(prediction), 2),
                'confidence': confidence,
                'based_on_months': len(monthly_spending)
            }
        except Exception as e:
            print(f"Error in predict_monthly_spending: {str(e)}")
            return {'error': str(e)}
    
    @staticmethod
    def get_spending_by_category(user_id, days=30):
        """
        Analyze spending breakdown by category
        
        Args:
            user_id: User ID
            days: Number of days to analyze
            
        Returns:
            dict with category breakdown
        """
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            transactions = Transaction.query.filter(
                Transaction.user_id == user_id,
                Transaction.type == 'expense',
                Transaction.created_at >= start_date
            ).all()
            
            if not transactions:
                return {'categories': {}, 'total': 0}
            
            # Group by category
            category_totals = {}
            for transaction in transactions:
                category = transaction.category or 'Uncategorized'
                if category not in category_totals:
                    category_totals[category] = 0
                category_totals[category] += transaction.amount
            
            # Calculate percentages
            total = sum(category_totals.values())
            category_breakdown = {
                cat: {
                    'amount': round(amount, 2),
                    'percentage': round((amount / total) * 100, 1) if total > 0 else 0
                }
                for cat, amount in sorted(category_totals.items(), key=lambda x: x[1], reverse=True)
            }
            
            return {
                'categories': category_breakdown,
                'total': round(total, 2)
            }
        except Exception as e:
            print(f"Error in get_spending_by_category: {str(e)}")
            return {'error': str(e)}
    
    @staticmethod
    def detect_anomalies(user_id):
        """
        Detect unusual spending patterns
        
        Args:
            user_id: User ID
            
        Returns:
            list of anomalies detected
        """
        try:
            # Get last 30 days of transactions
            start_date = datetime.utcnow() - timedelta(days=30)
            transactions = Transaction.query.filter(
                Transaction.user_id == user_id,
                Transaction.type == 'expense',
                Transaction.created_at >= start_date
            ).all()
            
            if len(transactions) < 5:
                return []
            
            # Calculate statistics
            amounts = [t.amount for t in transactions]
            mean = np.mean(amounts)
            std = np.std(amounts)
            
            # Detect outliers (3 standard deviations)
            anomalies = []
            for transaction in transactions:
                if transaction.amount > mean + (3 * std):
                    anomalies.append({
                        'description': transaction.description,
                        'amount': round(transaction.amount, 2),
                        'category': transaction.category,
                        'date': transaction.created_at.strftime('%Y-%m-%d'),
                        'reason': f'Unusually high for {transaction.category}'
                    })
            
            return anomalies
        except Exception as e:
            print(f"Error in detect_anomalies: {str(e)}")
            return []
    
    @staticmethod
    def get_financial_recommendations(user_id):
        """
        Generate personalized financial recommendations
        
        Args:
            user_id: User ID
            
        Returns:
            list of recommendations
        """
        try:
            recommendations = []
            
            # Get spending trends
            trends = MLService.get_spending_trends(user_id)
            
            # Get spending by category
            by_category = MLService.get_spending_by_category(user_id)
            
            # Get anomalies
            anomalies = MLService.detect_anomalies(user_id)
            
            # Generate recommendations
            if trends.get('trend') == 'increasing':
                recommendations.append({
                    'priority': 'high',
                    'title': 'Rising Spending Alert',
                    'description': f"Your spending is increasing. Daily average is {trends.get('daily_average')}. Consider reviewing your budget.",
                    'icon': '📈'
                })
            
            # Check for high category spending
            if by_category.get('categories'):
                for category, data in by_category['categories'].items():
                    if data['percentage'] > 40:
                        recommendations.append({
                            'priority': 'medium',
                            'title': f'{category} Spending Alert',
                            'description': f"{category} accounts for {data['percentage']}% of your spending. This is higher than recommended.",
                            'icon': '🎯'
                        })
            
            # Anomaly recommendations
            if anomalies:
                recommendations.append({
                    'priority': 'medium',
                    'title': f'Unusual Spending Detected',
                    'description': f"We detected {len(anomalies)} unusual transaction(s). Review them to ensure they're legitimate.",
                    'icon': '⚠️'
                })
            
            # Savings potential
            if trends.get('daily_average', 0) > 0:
                potential_savings = trends['daily_average'] * 0.1
                recommendations.append({
                    'priority': 'low',
                    'title': 'Savings Opportunity',
                    'description': f"If you reduce daily spending by 10%, you could save approximately ${round(potential_savings, 2)} per day.",
                    'icon': '💰'
                })
            
            return recommendations
        except Exception as e:
            print(f"Error in get_financial_recommendations: {str(e)}")
            return []
