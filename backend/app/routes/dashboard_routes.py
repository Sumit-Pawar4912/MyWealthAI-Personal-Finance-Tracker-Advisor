from flask import Blueprint, request, jsonify
from app.models import Transaction, User
from datetime import datetime, timedelta
from sqlalchemy import func
import jwt
import os

bp = Blueprint('dashboard', __name__, url_prefix='/api/dashboard')

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


@bp.route('/summary', methods=['GET'])
def get_summary():
    """Get dashboard summary - total income, expenses, balance, savings"""
    try:
        user = get_user_from_token()
        if not user:
            return jsonify({'error': 'Unauthorized'}), 401
        
        month = request.args.get('month', None)
        
        if month:
            year, month_num = map(int, month.split('-'))
            start_date = datetime(year, month_num, 1).date()
            if month_num == 12:
                end_date = datetime(year + 1, 1, 1).date()
            else:
                end_date = datetime(year, month_num + 1, 1).date()
        else:
            today = datetime.utcnow().date()
            start_date = datetime(today.year, today.month, 1).date()
            if today.month == 12:
                end_date = datetime(today.year + 1, 1, 1).date()
            else:
                end_date = datetime(today.year, today.month + 1, 1).date()
        
        month_transactions = Transaction.query.filter(
            Transaction.user_id == user.id,
            Transaction.date >= start_date,
            Transaction.date < end_date
        ).all()
        
        all_transactions = Transaction.query.filter(
            Transaction.user_id == user.id
        ).all()
        
        month_income = sum(t.amount for t in month_transactions if t.type == 'income')
        month_expense = sum(t.amount for t in month_transactions if t.type == 'expense')
        month_balance = month_income - month_expense
        month_savings_rate = (month_balance / month_income * 100) if month_income > 0 else 0
        
        total_income = sum(t.amount for t in all_transactions if t.type == 'income')
        total_expense = sum(t.amount for t in all_transactions if t.type == 'expense')
        cumulative_balance = total_income - total_expense
        
        categories = {}
        for t in month_transactions:
            if t.type == 'expense':
                if t.category not in categories:
                    categories[t.category] = 0
                categories[t.category] += t.amount
        
        return jsonify({
            'income': round(month_income, 2),
            'expense': round(month_expense, 2),
            'balance': round(month_balance, 2),
            'cumulative_balance': round(cumulative_balance, 2),
            'savings_rate': round(month_savings_rate, 2),
            'categories': categories,
            'transaction_count': len(month_transactions)
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/current-balance', methods=['GET'])
def get_current_balance():
    """Get all-time current balance (total income - total expenses)"""
    try:
        user = get_user_from_token()
        if not user:
            return jsonify({'error': 'Unauthorized'}), 401
        
        all_transactions = Transaction.query.filter(
            Transaction.user_id == user.id
        ).all()
        
        total_income = sum(t.amount for t in all_transactions if t.type == 'income')
        total_expense = sum(t.amount for t in all_transactions if t.type == 'expense')
        current_balance = total_income - total_expense
        
        return jsonify({
            'balance': round(current_balance, 2),
            'total_income': round(total_income, 2),
            'total_expense': round(total_expense, 2)
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/monthly-data', methods=['GET'])
def get_monthly_data():
    """Get monthly income and expense data for charts"""
    try:
        user = get_user_from_token()
        if not user:
            return jsonify({'error': 'Unauthorized'}), 401

        months_data = {}
        today = datetime.utcnow().date()

        for i in range(6):
            # Correctly calculate month by subtracting i months
            month = today.month - i
            year = today.year
            while month <= 0:
                month += 12
                year -= 1

            month_start = datetime(year, month, 1).date()
            if month == 12:
                next_month_start = datetime(year + 1, 1, 1).date()
            else:
                next_month_start = datetime(year, month + 1, 1).date()

            month_transactions = Transaction.query.filter(
                Transaction.user_id == user.id,
                Transaction.date >= month_start,
                Transaction.date < next_month_start
            ).all()

            month_key = f"{year}-{str(month).zfill(2)}"
            months_data[month_key] = {
                'income': sum(t.amount for t in month_transactions if t.type == 'income'),
                'expense': sum(t.amount for t in month_transactions if t.type == 'expense'),
            }

        return jsonify(months_data), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500