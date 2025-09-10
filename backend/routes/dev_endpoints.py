"""
Development-only endpoints for the TrueCred API.
These endpoints should be disabled in production.
"""
from flask import Blueprint, request, jsonify, current_app
from datetime import datetime
from models.user import User
from services.auth_service import AuthService

# Create blueprint
dev_bp = Blueprint('dev', __name__)

@dev_bp.route('/get-verification-token', methods=['POST'])
def dev_get_verification_token():
    if not current_app.config.get('DEBUG', False):
        return jsonify({
            'success': False,
            'message': 'This endpoint is only available in development mode'
        }), 403
    
    data = request.json
    email = data.get('email')
    
    if not email:
        return jsonify({
            'success': False,
            'message': 'Email is required'
        }), 400
    
    # Find user by email
    user = User.objects(email=email).first()
    
    if not user:
        return jsonify({
            'success': False,
            'message': 'User not found'
        }), 404
    
    # If the user already has a token and it's not expired, return it
    if user.verification_token and user.verification_token_expires and user.verification_token_expires > datetime.utcnow():
        return jsonify({
            'success': True,
            'token': user.verification_token,
            'expires': user.verification_token_expires.isoformat()
        }), 200
    
    # Otherwise, generate a new token
    success, message, token = AuthService.send_verification_email(user)
    
    if not success:
        return jsonify({
            'success': False,
            'message': message
        }), 500
    
    return jsonify({
        'success': True,
        'token': token,
        'expires': user.verification_token_expires.isoformat()
    }), 200
