"""
Authentication routes for the TrueCred API.
"""
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import (
    create_access_token, create_refresh_token, jwt_required, 
    get_jwt_identity, get_jwt
)
from datetime import datetime, timedelta
from services.auth_service import AuthService
from models.user import User
from middleware.auth_middleware import admin_required
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create blueprint
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Register a new user.
    ---
    Endpoint for user registration.
    
    Request Body:
      username: Unique username
      email: User's email address
      password: Password
      first_name: User's first name (optional)
      last_name: User's last name (optional)
    
    Returns:
      User profile data and success message
    """
    data = request.json
    
    # Validate required fields
    required_fields = ['username', 'email', 'password']
    for field in required_fields:
        if field not in data:
            return jsonify({
                'success': False,
                'message': f'Missing required field: {field}'
            }), 400
    
    # Register user
    user, error = AuthService.register_user(
        username=data.get('username'),
        email=data.get('email'),
        password=data.get('password'),
        first_name=data.get('first_name'),
        last_name=data.get('last_name'),
        role=data.get('role', 'user')  # Default role is 'user'
    )
    
    if error:
        return jsonify({
            'success': False,
            'message': error
        }), 400
    
    # Generate tokens
    tokens = AuthService.generate_tokens(
        user_id=str(user.id),
        additional_claims={'role': user.role}
    )
    
    # Return user data and tokens
    return jsonify({
        'success': True,
        'message': 'User registered successfully',
        'user': user.to_json(),
        'tokens': tokens
    }), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Authenticate a user and return a JWT token.
    ---
    Endpoint for user login.
    
    Request Body:
      username_or_email: Username or email
      password: Password
    
    Returns:
      User profile data and access tokens
    """
    data = request.json
    
    # Validate required fields
    required_fields = ['username_or_email', 'password']
    for field in required_fields:
        if field not in data:
            return jsonify({
                'success': False,
                'message': f'Missing required field: {field}'
            }), 400
    
    # Authenticate user
    user, error = AuthService.authenticate_user(
        username_or_email=data.get('username_or_email'),
        password=data.get('password')
    )
    
    if error:
        return jsonify({
            'success': False,
            'message': error
        }), 401
    
    # Generate tokens
    tokens = AuthService.generate_tokens(
        user_id=str(user.id),
        additional_claims={'role': user.role}
    )
    
    # Return user data and tokens
    return jsonify({
        'success': True,
        'message': 'Login successful',
        'user': user.to_json(),
        'tokens': tokens
    }), 200

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """
    Logout a user by blacklisting their JWT token.
    ---
    Requires authentication.
    
    Returns:
      Success message
    """
    # Get the JWT ID
    jti = get_jwt()["jti"]
    
    # Add token to blacklist
    from app import token_blacklist
    token_blacklist.add(jti)
    
    return jsonify({
        'success': True,
        'message': 'Successfully logged out'
    }), 200

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """
    Get the current user's profile.
    ---
    Requires authentication.
    
    Returns:
      User profile data
    """
    current_user_id = get_jwt_identity()
    
    # Get user by ID
    user, error = AuthService.get_user_by_id(current_user_id)
    
    if error:
        return jsonify({
            'success': False,
            'message': error
        }), 404
    
    # Return user data
    return jsonify({
        'success': True,
        'user': user.to_json()
    }), 200

@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """
    Update the current user's profile.
    ---
    Requires authentication.
    
    Request Body:
      first_name: User's first name (optional)
      last_name: User's last name (optional)
      email: User's email address (optional)
    
    Returns:
      Updated user profile data
    """
    current_user_id = get_jwt_identity()
    data = request.json
    
    # Get user by ID
    user, error = AuthService.get_user_by_id(current_user_id)
    
    if error:
        return jsonify({
            'success': False,
            'message': error
        }), 404
    
    # Update user fields
    updatable_fields = ['first_name', 'last_name', 'email']
    updates = {}
    
    for field in updatable_fields:
        if field in data and data[field] is not None:
            updates[field] = data[field]
    
    if not updates:
        return jsonify({
            'success': False,
            'message': 'No valid fields to update'
        }), 400
    
    # Update user
    try:
        for field, value in updates.items():
            setattr(user, field, value)
        user.updated_at = datetime.utcnow()
        user.save()
        
        return jsonify({
            'success': True,
            'message': 'Profile updated successfully',
            'user': user.to_json()
        }), 200
        
    except Exception as e:
        logger.error(f"Error updating user profile: {e}")
        
        return jsonify({
            'success': False,
            'message': f'An error occurred while updating the profile: {str(e)}'
        }), 500

@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """
    Change the current user's password.
    ---
    Requires authentication.
    
    Request Body:
      current_password: User's current password
      new_password: User's new password
    
    Returns:
      Success message
    """
    current_user_id = get_jwt_identity()
    data = request.json
    
    # Validate required fields
    required_fields = ['current_password', 'new_password']
    for field in required_fields:
        if field not in data:
            return jsonify({
                'success': False,
                'message': f'Missing required field: {field}'
            }), 400
    
    # Change password
    success, error = AuthService.change_password(
        user_id=current_user_id,
        current_password=data.get('current_password'),
        new_password=data.get('new_password')
    )
    
    if not success:
        return jsonify({
            'success': False,
            'message': error
        }), 400
    
    return jsonify({
        'success': True,
        'message': 'Password changed successfully'
    }), 200

@auth_bp.route('/refresh', methods=['POST'])
def refresh_token():
    """
    Refresh an expired access token.
    ---
    Request Body:
      refresh_token: The refresh token
    
    Returns:
      New access and refresh tokens
    """
    data = request.json
    if not data or 'refresh_token' not in data:
        return jsonify({
            'success': False,
            'message': 'Refresh token is required'
        }), 400
    
    refresh_token = data['refresh_token']
    
    try:
        # Verify and decode the refresh token
        user_id = AuthService.verify_refresh_token(refresh_token)
        
        if not user_id:
            return jsonify({
                'success': False,
                'message': 'Invalid or expired refresh token'
            }), 401
        
        # Get the user from database
        user = User.objects(id=user_id).first()
        
        if not user:
            return jsonify({
                'success': False,
                'message': 'User not found'
            }), 404
        
        # Generate new tokens
        access_token = create_access_token(
            identity=str(user.id),
            additional_claims={'role': user.role}
        )
        
        new_refresh_token = create_refresh_token(
            identity=str(user.id),
            additional_claims={'role': user.role}
        )
        
        # Return new tokens
        return jsonify({
            'success': True,
            'tokens': {
                'access_token': access_token,
                'refresh_token': new_refresh_token,
                'token_type': 'Bearer'
            }
        }), 200
    except Exception as e:
        logger.error(f"Error refreshing token: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Error refreshing token'
        }), 500

@auth_bp.route('/users', methods=['GET'])
@jwt_required()
@admin_required
def get_users():
    """
    Get all users (admin only).
    ---
    Requires authentication and admin role.
    
    Returns:
      List of all users
    """
    try:
        users = User.objects.all()
        
        return jsonify({
            'success': True,
            'users': [user.to_json() for user in users]
        }), 200
        
    except Exception as e:
        logger.error(f"Error retrieving users: {e}")
        
        return jsonify({
            'success': False,
            'message': 'An error occurred while retrieving users'
        }), 500

@auth_bp.route('/users/<user_id>', methods=['GET', 'PUT', 'DELETE'])
@jwt_required()
@admin_required
def manage_user(user_id):
    """
    Manage a specific user by ID (admin only).
    ---
    Requires authentication and admin role.
    
    GET:
        Returns user profile data
    
    PUT:
        Request Body:
          first_name: User's first name (optional)
          last_name: User's last name (optional)
          email: User's email address (optional)
          is_active: User's active status (optional)
          role: User's role (optional)
        Returns updated user profile data
    
    DELETE:
        Deactivates a user (soft delete)
        Returns success message
    """
    # Get user by ID
    user, error = AuthService.get_user_by_id(user_id)
    
    if error:
        return jsonify({
            'success': False,
            'message': error
        }), 404
    
    # GET request - Return user data
    if request.method == 'GET':
        return jsonify({
            'success': True,
            'user': user.to_json()
        }), 200
    
    # PUT request - Update user
    elif request.method == 'PUT':
        data = request.json
        
        # Update user fields
        updatable_fields = ['first_name', 'last_name', 'email', 'is_active', 'role']
        updates = {}
        
        for field in updatable_fields:
            if field in data and data[field] is not None:
                updates[field] = data[field]
        
        if not updates:
            return jsonify({
                'success': False,
                'message': 'No valid fields to update'
            }), 400
        
        # Update user
        try:
            for field, value in updates.items():
                setattr(user, field, value)
            user.updated_at = datetime.utcnow()
            user.save()
            
            return jsonify({
                'success': True,
                'message': 'User updated successfully',
                'user': user.to_json()
            }), 200
            
        except Exception as e:
            logger.error(f"Error updating user: {e}")
            
            return jsonify({
                'success': False,
                'message': f'An error occurred while updating the user: {str(e)}'
            }), 500
    
    # DELETE request - Deactivate user
    elif request.method == 'DELETE':
        try:
            # Soft delete - deactivate user
            user.is_active = False
            user.updated_at = datetime.utcnow()
            user.save()
            
            return jsonify({
                'success': True,
                'message': 'User deactivated successfully'
            }), 200
            
        except Exception as e:
            logger.error(f"Error deactivating user: {e}")
            
            return jsonify({
                'success': False,
                'message': 'An error occurred while deactivating the user'
            }), 500

@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    """
    Request a password reset.
    ---
    Request Body:
      email: User's email address
    
    Returns:
      Success message
    """
    data = request.json
    
    # Validate required fields
    if 'email' not in data:
        return jsonify({
            'success': False,
            'message': 'Missing required field: email'
        }), 400
    
    # Request password reset
    success, message, token = AuthService.request_password_reset(data.get('email'))
    
    # In a production environment, we would send an email with a reset link
    # For development purposes, we'll return the token directly if available
    response = {
        'success': success,
        'message': message
    }
    
    # Only include token in development environment for testing
    if token and current_app.config.get('ENV') == 'development':
        response['reset_token'] = token
    
    return jsonify(response), 200 if success else 400

@auth_bp.route('/verify-email', methods=['GET'])
def verify_email():
    """
    Verify a user's email using a verification token.
    ---
    Endpoint for verifying a user's email.
    
    Query Parameters:
      token: Verification token
    
    Returns:
      Success message and user data
    """
    token = request.args.get('token')
    
    if not token:
        return jsonify({
            'success': False,
            'message': 'Missing verification token'
        }), 400
    
    # Verify email
    success, message, user = AuthService.verify_email(token)
    
    if not success:
        return jsonify({
            'success': False,
            'message': message
        }), 400
    
    # Generate tokens for auto-login after verification
    tokens = AuthService.generate_tokens(
        user_id=str(user.id),
        additional_claims={'role': user.role}
    )
    
    return jsonify({
        'success': True,
        'message': message,
        'user': user.to_json(),
        'tokens': tokens
    }), 200

@auth_bp.route('/resend-verification', methods=['POST'])
def resend_verification():
    """
    Resend verification email.
    ---
    Endpoint for resending verification email.
    
    Request Body:
      email: User's email address
    
    Returns:
      Success message
    """
    data = request.json
    
    if 'email' not in data:
        return jsonify({
            'success': False,
            'message': 'Missing required field: email'
        }), 400
    
    # Find user by email
    user = User.objects(email=data.get('email').lower()).first()
    
    if not user:
        # For security reasons, don't reveal if email exists or not
        return jsonify({
            'success': True,
            'message': 'If an account with this email exists, a verification link will be sent'
        }), 200
    
    # If already verified, don't send verification email
    if user.email_verified:
        return jsonify({
            'success': True,
            'message': 'Email is already verified'
        }), 200
    
    # Send verification email
    success, message, token = AuthService.send_verification_email(user)
    
    if not success:
        return jsonify({
            'success': False,
            'message': message
        }), 500
    
    return jsonify({
        'success': True,
        'message': 'Verification email sent'
    }), 200

@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """
    Reset a password using a reset token.
    ---
    Request Body:
      token: Password reset token
      new_password: New password
    
    Returns:
      Success message
    """
    data = request.json
    
    # Validate required fields
    required_fields = ['token', 'new_password']
    for field in required_fields:
        if field not in data:
            return jsonify({
                'success': False,
                'message': f'Missing required field: {field}'
            }), 400
    
    # Reset password
    success, message = AuthService.reset_password(
        reset_token=data.get('token'),
        new_password=data.get('new_password')
    )
    
    return jsonify({
        'success': success,
        'message': message
    }), 200 if success else 400

@auth_bp.route('/connect-wallet', methods=['POST'])
@jwt_required()
def connect_wallet():
    """
    Connect a wallet address to the current user account.
    ---
    Endpoint for connecting a wallet address to the current user.
    
    Request Body:
      wallet_address: Ethereum wallet address
    
    Returns:
      Success message
    """
    data = request.json
    
    # Validate required fields
    if 'wallet_address' not in data:
        return jsonify({
            'success': False,
            'message': 'Missing wallet address'
        }), 400
    
    wallet_address = data.get('wallet_address')
    user_id = get_jwt_identity()
    
    # Connect wallet
    success, error = AuthService.connect_wallet(user_id, wallet_address)
    
    if not success:
        return jsonify({
            'success': False,
            'message': error
        }), 400
    
    return jsonify({
        'success': True,
        'message': 'Wallet connected successfully'
    }), 200

@auth_bp.route('/wallet-auth', methods=['POST'])
def wallet_auth():
    """
    Authenticate using a wallet address.
    ---
    Endpoint for authenticating using an Ethereum wallet address.
    
    Request Body:
      wallet_address: Ethereum wallet address
      signature: Signed message proving ownership (optional)
    
    Returns:
      User profile data and access tokens
    """
    data = request.json
    
    # Validate required fields
    if 'wallet_address' not in data:
        return jsonify({
            'success': False,
            'message': 'Missing wallet address'
        }), 400
    
    wallet_address = data.get('wallet_address')
    
    # Authenticate user
    user, error = AuthService.authenticate_wallet(wallet_address)
    
    if error:
        return jsonify({
            'success': False,
            'message': error
        }), 401
    
    # Generate tokens
    tokens = AuthService.generate_tokens(
        user_id=str(user.id),
        additional_claims={'role': user.role}
    )
    
    # Return user data and tokens
    return jsonify({
        'success': True,
        'message': 'Authentication successful',
        'user': user.to_json(),
        'tokens': tokens
    }), 200
