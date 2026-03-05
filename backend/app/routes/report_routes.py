from flask import Blueprint, request, jsonify, make_response
from app.models import Transaction, User
import jwt
import os
import io
import csv
from datetime import datetime
import logging

# Set up logging
logger = logging.getLogger(__name__)

bp = Blueprint('report', __name__, url_prefix='/api/report')

SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')


def get_user_from_token():
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            logger.warning('No token provided in request')
            return None
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        user = User.query.get(payload['user_id'])
        if not user:
            logger.warning(f'User not found for token: {payload.get("user_id")}')
        return user
    except jwt.InvalidTokenError as e:
        logger.error(f'Invalid token: {str(e)}')
        return None
    except Exception as e:
        logger.error(f'Error decoding token: {str(e)}')
        return None


@bp.route('/transactions', methods=['GET'])
def export_transactions():
    """Export user's transactions as CSV (default)

    Query params:
    - format=csv (only csv supported for now)
    """
    try:
        user = get_user_from_token()
        if not user:
            logger.error('Unauthorized access attempt to export_transactions')
            return jsonify({'error': 'Unauthorized - Please log in'}), 401

        fmt = request.args.get('format', 'csv').lower()
        if fmt != 'csv':
            return jsonify({'error': 'Only csv format is supported'}), 400

        # Fetch all transactions for user ordered by date desc
        transactions = Transaction.query.filter_by(user_id=user.id).order_by(Transaction.date.desc(), Transaction.id.desc()).all()
        
        logger.info(f'Exporting {len(transactions)} transactions for user {user.id}')

        # Create CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)

        # Header
        writer.writerow(['id', 'type', 'category', 'description', 'amount', 'date', 'created_at'])

        for t in transactions:
            writer.writerow([
                t.id,
                t.type,
                t.category,
                t.description,
                f"{t.amount:.2f}",
                t.date.isoformat(),
                t.created_at.isoformat(),
            ])

        csv_data = output.getvalue()
        output.close()

        # Build response
        filename = f"transactions_{user.id}_{datetime.utcnow().strftime('%Y%m%d')}.csv"
        response = make_response(csv_data)
        response.headers['Content-Type'] = 'text/csv; charset=utf-8'
        response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
        response.headers['Content-Length'] = len(csv_data)
        return response

    except Exception as e:
        error_msg = f'Error exporting transactions: {str(e)}'
        logger.error(error_msg)
        return jsonify({'error': error_msg}), 500
