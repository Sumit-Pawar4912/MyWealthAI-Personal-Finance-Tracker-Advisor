from flask import Blueprint, request, jsonify
from app.database import db
from app.models import User, Transaction
import jwt
import os

bp = Blueprint('admin', __name__, url_prefix='/api/admin')

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

def require_admin(f):
    """Decorator to require admin privileges"""
    def decorated_function(*args, **kwargs):
        user = get_user_from_token()
        if not user or not user.is_admin:
            return jsonify({'error': 'Unauthorized: admin access required'}), 403
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@bp.route('/users', methods=['GET'])
@require_admin
def list_users():
    """List all users (admin only)"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        paginated = User.query.paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'users': [u.to_dict() for u in paginated.items],
            'total': paginated.total,
            'pages': paginated.pages,
            'current_page': page
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/users/<int:user_id>', methods=['GET'])
@require_admin
def get_user_details(user_id):
    """Get detailed user information (admin only)"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get user transactions count
        tx_count = Transaction.query.filter_by(user_id=user_id).count()
        
        # Get user summary
        expenses = db.session.query(db.func.sum(Transaction.amount)).filter(
            Transaction.user_id == user_id,
            Transaction.type == 'expense'
        ).scalar() or 0.0
        
        income = db.session.query(db.func.sum(Transaction.amount)).filter(
            Transaction.user_id == user_id,
            Transaction.type == 'income'
        ).scalar() or 0.0
        
        return jsonify({
            'user': user.to_dict(),
            'transaction_count': tx_count,
            'total_expense': round(float(expenses), 2),
            'total_income': round(float(income), 2),
            'balance': round(float(income - expenses), 2)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/users/<int:user_id>/reset-password', methods=['POST'])
@require_admin
def reset_user_password(user_id):
    """Reset a user's password to a new one (admin only)"""
    try:
        data = request.get_json()
        new_password = data.get('password')
        
        if not new_password:
            return jsonify({'error': 'Password is required'}), 400
        
        if len(new_password) < 6:
            return jsonify({'error': 'Password must be at least 6 characters'}), 400
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        user.set_password(new_password)
        db.session.commit()
        
        return jsonify({
            'message': f'Password reset for {user.email}',
            'user': user.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/users/<int:user_id>/toggle-admin', methods=['POST'])
@require_admin
def toggle_admin(user_id):
    """Toggle admin status for a user (admin only)"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        user.is_admin = not user.is_admin
        db.session.commit()
        
        return jsonify({
            'message': f'Admin status set to {user.is_admin} for {user.email}',
            'user': user.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/users/<int:user_id>', methods=['DELETE'])
@require_admin
def delete_user(user_id):
    """Delete a user and all their data (admin only)"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        email = user.email
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({'message': f'User {email} deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/stats', methods=['GET'])
@require_admin
def admin_stats():
    """Get admin dashboard statistics"""
    try:
        total_users = User.query.count()
        admin_count = User.query.filter_by(is_admin=True).count()
        total_transactions = Transaction.query.count()
        
        total_expenses = db.session.query(db.func.sum(Transaction.amount)).filter(
            Transaction.type == 'expense'
        ).scalar() or 0.0
        
        total_income = db.session.query(db.func.sum(Transaction.amount)).filter(
            Transaction.type == 'income'
        ).scalar() or 0.0
        
        return jsonify({
            'total_users': total_users,
            'admin_count': admin_count,
            'total_transactions': total_transactions,
            'total_expenses': round(float(total_expenses), 2),
            'total_income': round(float(total_income), 2),
            'system_balance': round(float(total_income - total_expenses), 2)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
