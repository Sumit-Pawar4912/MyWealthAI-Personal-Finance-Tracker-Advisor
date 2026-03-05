from flask import Blueprint, request, jsonify
from app.models import Transaction, User
from datetime import datetime
import jwt
import os

bp = Blueprint('advice', __name__, url_prefix='/api/advice')

SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

def get_user_from_token():
    """Extract user from JWT token"""
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return None
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return User.query.get(payload['user_id'])
    except:
        return None


@bp.route('', methods=['GET'])
def get_financial_advice():
    """Generate AI financial advice based on spending patterns"""
    try:
        user = get_user_from_token()
        if not user:
            return jsonify({'error': 'Unauthorized'}), 401
        
        # Get current month transactions
        today = datetime.utcnow().date()
        start_date = datetime(today.year, today.month, 1).date()
        
        if today.month == 12:
            end_date = datetime(today.year + 1, 1, 1).date()
        else:
            end_date = datetime(today.year, today.month + 1, 1).date()
        
        transactions = Transaction.query.filter(
            Transaction.user_id == user.id,
            Transaction.date >= start_date,
            Transaction.date < end_date
        ).all()
        
        # Calculate metrics
        income = sum(t.amount for t in transactions if t.type == 'income')
        expense = sum(t.amount for t in transactions if t.type == 'expense')
        
        advice_list = []
        
        # Check savings rate
        savings_rate = (income - expense) / income * 100 if income > 0 else 0
        
        if savings_rate < 20:
            advice_list.append({
                'title': 'Increase Savings Rate',
                'description': f'Your current savings rate is {savings_rate:.1f}%. Financial experts recommend saving at least 20% of your income. Try reducing discretionary spending.',
                'icon': '💰',
                'priority': 'high',
                'category': 'savings'
            })
        
        # Check if expenses exceed income
        if expense > income:
            advice_list.append({
                'title': 'Expenses Exceed Income',
                'description': 'Your expenses are higher than your income this month. Review your spending habits and consider creating a budget to control costs.',
                'icon': '⚠️',
                'priority': 'high',
                'category': 'budget'
            })
        
        # Analyze spending by category
        categories = {}
        for t in transactions:
            if t.type == 'expense':
                if t.category not in categories:
                    categories[t.category] = 0
                categories[t.category] += t.amount
        
        # Check largest expense category
        if categories:
            largest_category = max(categories.items(), key=lambda x: x[1])
            
            if largest_category[0] == 'Food & Dining' and largest_category[1] > income * 0.15:
                advice_list.append({
                    'title': 'Food Spending Alert',
                    'description': f'Your food spending is ${largest_category[1]:.2f} this month. Consider meal planning and cooking at home to reduce costs.',
                    'icon': '🍽️',
                    'priority': 'medium',
                    'category': 'spending'
                })
            
            if largest_category[0] == 'Shopping' and largest_category[1] > income * 0.2:
                advice_list.append({
                    'title': 'High Shopping Expenses',
                    'description': f'Your shopping expenses are ${largest_category[1]:.2f}. Review your purchases and distinguish between needs and wants.',
                    'icon': '🛍️',
                    'priority': 'medium',
                    'category': 'spending'
                })
        
        # Check if user has no transactions
        if len(transactions) == 0:
            advice_list.append({
                'title': 'Start Tracking',
                'description': 'Start recording your transactions to get personalized financial advice and insights about your spending patterns.',
                'icon': '📝',
                'priority': 'low',
                'category': 'tracking'
            })
        
        # Add default positive advice if no issues found
        if len(advice_list) == 0:
            advice_list.append({
                'title': 'Great Job!',
                'description': f'You\'re doing well! Your savings rate of {savings_rate:.1f}% is above the recommended 20%. Keep up the good financial habits.',
                'icon': '🎉',
                'priority': 'low',
                'category': 'positive'
            })
        
        return jsonify({
            'advice': advice_list,
            'metrics': {
                'income': round(income, 2),
                'expense': round(expense, 2),
                'savings_rate': round(savings_rate, 2)
            }
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
