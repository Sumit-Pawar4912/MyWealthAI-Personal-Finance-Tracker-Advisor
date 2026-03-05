from flask import Blueprint, request, jsonify
import jwt
import os
from datetime import datetime, timedelta
from app.ml_service import MLService

bp = Blueprint('analytics', __name__, url_prefix='/api/analytics')

SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')


def get_user_id_from_token():
    """Extract user ID from JWT token"""
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return None
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload.get('user_id')
    except:
        return None


@bp.route('/spending-trends', methods=['GET'])
def spending_trends():
    """Get spending trends analysis"""
    try:
        user_id = get_user_id_from_token()
        if not user_id:
            return jsonify({'error': 'Unauthorized'}), 401
        
        days = request.args.get('days', 30, type=int)
        trends = MLService.get_spending_trends(user_id, days)
        
        return jsonify(trends), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/spending-prediction', methods=['GET'])
def spending_prediction():
    """Get predicted monthly spending"""
    try:
        user_id = get_user_id_from_token()
        if not user_id:
            return jsonify({'error': 'Unauthorized'}), 401
        
        prediction = MLService.predict_monthly_spending(user_id)
        
        return jsonify(prediction), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/spending-by-category', methods=['GET'])
def spending_by_category():
    """Get spending breakdown by category"""
    try:
        user_id = get_user_id_from_token()
        if not user_id:
            return jsonify({'error': 'Unauthorized'}), 401
        
        days = request.args.get('days', 30, type=int)
        breakdown = MLService.get_spending_by_category(user_id, days)
        
        return jsonify(breakdown), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/anomalies', methods=['GET'])
def detect_anomalies():
    """Detect spending anomalies"""
    try:
        user_id = get_user_id_from_token()
        if not user_id:
            return jsonify({'error': 'Unauthorized'}), 401
        
        anomalies = MLService.detect_anomalies(user_id)
        
        return jsonify({'anomalies': anomalies}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/recommendations', methods=['GET'])
def get_recommendations():
    """Get personalized financial recommendations"""
    try:
        user_id = get_user_id_from_token()
        if not user_id:
            return jsonify({'error': 'Unauthorized'}), 401
        
        recommendations = MLService.get_financial_recommendations(user_id)
        
        return jsonify({'recommendations': recommendations}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/overspending-risk', methods=['GET'])
def overspending_risk():
    """Get overspending risk prediction for the authenticated user"""
    try:
        user_id = get_user_id_from_token()
        if not user_id:
            return jsonify({'error': 'Unauthorized'}), 401

        days = request.args.get('days', 30, type=int)
        result = MLService.predict_overspending_risk(user_id, days)

        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
