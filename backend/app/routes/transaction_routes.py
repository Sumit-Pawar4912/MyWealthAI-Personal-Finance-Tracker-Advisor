from flask import Blueprint, request, jsonify
from app.database import db
from app.models import Transaction, User
from datetime import datetime
import jwt
import os

bp = Blueprint('transactions', __name__, url_prefix='/api/transactions')

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


@bp.route('', methods=['POST'])
def create_transaction():
    """Create a new transaction"""
    try:
        user = get_user_from_token()
        if not user:
            return jsonify({'error': 'Unauthorized'}), 401
        
        data = request.get_json()
        
        # Validate input
        required_fields = ['type', 'category', 'description', 'amount', 'date']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
        
        if data['type'] not in ['income', 'expense']:
            return jsonify({'error': 'Type must be income or expense'}), 400
        
        # Create transaction
        transaction = Transaction(
            user_id=user.id,
            type=data['type'],
            category=data['category'],
            description=data['description'],
            amount=float(data['amount']),
            date=datetime.strptime(data['date'], '%Y-%m-%d').date()
        )
        
        db.session.add(transaction)
        db.session.commit()
        
        return jsonify({
            'message': 'Transaction created successfully',
            'transaction': transaction.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('', methods=['GET'])
def get_transactions():
    """Get all transactions for the user"""
    try:
        user = get_user_from_token()
        if not user:
            return jsonify({'error': 'Unauthorized'}), 401
        
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        transaction_type = request.args.get('type', None)
        
        # Build query (order newest first)
        query = Transaction.query.filter_by(user_id=user.id).order_by(Transaction.date.desc(), Transaction.id.desc())
        
        if transaction_type:
            query = query.filter_by(type=transaction_type)
        
        # Paginate
        paginated = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'transactions': [t.to_dict() for t in paginated.items],
            'total': paginated.total,
            'pages': paginated.pages,
            'current_page': page
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:transaction_id>', methods=['GET'])
def get_transaction(transaction_id):
    """Get a specific transaction"""
    try:
        user = get_user_from_token()
        if not user:
            return jsonify({'error': 'Unauthorized'}), 401
        
        transaction = Transaction.query.filter_by(id=transaction_id, user_id=user.id).first()
        
        if not transaction:
            return jsonify({'error': 'Transaction not found'}), 404
        
        return jsonify(transaction.to_dict()), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:transaction_id>', methods=['PUT'])
def update_transaction(transaction_id):
    """Update a transaction"""
    try:
        user = get_user_from_token()
        if not user:
            return jsonify({'error': 'Unauthorized'}), 401
        
        transaction = Transaction.query.filter_by(id=transaction_id, user_id=user.id).first()
        
        if not transaction:
            return jsonify({'error': 'Transaction not found'}), 404
        
        data = request.get_json()
        
        # Update fields
        if 'category' in data:
            transaction.category = data['category']
        if 'description' in data:
            transaction.description = data['description']
        if 'amount' in data:
            transaction.amount = float(data['amount'])
        if 'date' in data:
            transaction.date = datetime.strptime(data['date'], '%Y-%m-%d').date()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Transaction updated successfully',
            'transaction': transaction.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:transaction_id>', methods=['DELETE'])
def delete_transaction(transaction_id):
    """Delete a transaction"""
    try:
        user = get_user_from_token()
        if not user:
            return jsonify({'error': 'Unauthorized'}), 401
        
        transaction = Transaction.query.filter_by(id=transaction_id, user_id=user.id).first()
        
        if not transaction:
            return jsonify({'error': 'Transaction not found'}), 404
        
        db.session.delete(transaction)
        db.session.commit()
        
        return jsonify({'message': 'Transaction deleted successfully'}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
