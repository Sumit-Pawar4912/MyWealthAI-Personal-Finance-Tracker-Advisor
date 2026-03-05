"""
Chatbot API Routes for MyWelthAI
Handles AI chatbot messages and interactions
"""

from flask import Blueprint, request, jsonify
import jwt
import os
from app.chatbot_service import ChatbotService
from app.models import User
from datetime import datetime

SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

chatbot_bp = Blueprint('chatbot', __name__, url_prefix='/api/chatbot')


@chatbot_bp.route('/message', methods=['POST'])
def send_message():
    """
    Handle chatbot message
    
    Expected JSON:
    {
        "message": "user message text"
    }
    Expected Headers:
    {
        "Authorization": "Bearer <jwt_token>"
    }
    """
    try:
        # Verify JWT token
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'error': 'Missing authorization header'}), 401
        
        try:
            token = auth_header.split(' ')[1]
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            user_id = payload.get('user_id')
        except (jwt.DecodeError, jwt.ExpiredSignatureError, IndexError):
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({'error': 'Message is required'}), 400
        
        user_message = data['message'].strip()
        
        if not user_message:
            return jsonify({'error': 'Message cannot be empty'}), 400
        
        # Get chatbot response
        response = ChatbotService.get_response(user_id, user_message)
        
        return jsonify({
            'success': True,
            'response': response['response'],
            'intent': response.get('intent', 'unknown'),
            'timestamp': datetime.now().isoformat(),
            'data': response.get('data', {})
        }), 200
        
    except Exception as e:
        print(f"Error in chatbot endpoint: {str(e)}")
        return jsonify({
            'error': 'An error occurred while processing your message',
            'details': str(e)
        }), 500


@chatbot_bp.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'service': 'chatbot'
    }), 200
