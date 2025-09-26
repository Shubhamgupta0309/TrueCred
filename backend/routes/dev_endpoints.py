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

@dev_bp.route('/assign-missing-truecred-ids', methods=['POST'])
def dev_assign_missing_truecred_ids():
    """
    Development endpoint to assign TrueCred IDs to users who don't have them.
    This is useful for data migration and fixing existing users.
    """
    if not current_app.config.get('DEBUG', False):
        return jsonify({
            'success': False,
            'message': 'This endpoint is only available in development mode'
        }), 403
    
    try:
        success_count, error_count = AuthService.assign_missing_truecred_ids()
        
        return jsonify({
            'success': True,
            'message': f'Assigned TrueCred IDs to {success_count} users. {error_count} errors occurred.',
            'success_count': success_count,
            'error_count': error_count
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error assigning TrueCred IDs: {e}")
        return jsonify({
            'success': False,
            'message': f'An error occurred: {str(e)}'
        }), 500

@dev_bp.route('/test-truecred-id-generation', methods=['GET'])
def dev_test_truecred_id_generation():
    """
    Development endpoint to test TrueCred ID generation.
    """
    if not current_app.config.get('DEBUG', False):
        return jsonify({
            'success': False,
            'message': 'This endpoint is only available in development mode'
        }), 403
    
    try:
        from backend.utils.id_generator import generate_truecred_id, generate_sequential_truecred_id
        
        # Generate a few test IDs
        random_ids = [generate_truecred_id() for _ in range(5)]
        sequential_ids = [generate_sequential_truecred_id() for _ in range(3)]
        
        # Test uniqueness generation
        unique_id = AuthService._generate_unique_truecred_id()
        
        return jsonify({
            'success': True,
            'random_ids': random_ids,
            'sequential_ids': sequential_ids,
            'unique_id': unique_id,
            'format_validation': {
                'expected_format': 'TC + 6 digits',
                'example': 'TC123456',
                'length': 8
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error testing TrueCred ID generation: {e}")
        return jsonify({
            'success': False,
            'message': f'An error occurred: {str(e)}'
        }), 500
