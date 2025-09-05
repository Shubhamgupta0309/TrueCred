"""
Authentication service for the TrueCred application.

This service provides functions for user registration, authentication,
and profile management.
"""
from models.user import User
from utils.password import hash_password, verify_password, password_meets_requirements
from mongoengine.errors import NotUniqueError, ValidationError
import logging
from datetime import datetime, timedelta
from flask_jwt_extended import create_access_token, create_refresh_token
import secrets
import string

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AuthService:
    """
    Service class for authentication-related operations.
    """
    
    @staticmethod
    def register_user(username, email, password, first_name=None, last_name=None, role='user'):
        """
        Register a new user.
        
        Args:
            username: Unique username
            email: User's email address
            password: Plain text password
            first_name: User's first name (optional)
            last_name: User's last name (optional)
            role: User role (default: 'user')
            
        Returns:
            (user, error): (User object, None) if successful, (None, error_message) otherwise
        """
        try:
            # Check if username already exists
            if User.objects(username=username).first():
                return None, "Username already exists"
            
            # Check if email already exists
            if User.objects(email=email).first():
                return None, "Email already exists"
            
            # Validate password
            password_valid, password_error = password_meets_requirements(password)
            if not password_valid:
                return None, password_error
            
            # Hash password
            hashed_password = hash_password(password)
            
            # Create user
            user = User(
                username=username,
                email=email,
                password=hashed_password,
                first_name=first_name,
                last_name=last_name,
                role=role
            )
            
            # Save user
            user.save()
            
            logger.info(f"User registered successfully: {username}")
            return user, None
            
        except NotUniqueError as e:
            logger.error(f"Not unique error registering user: {e}")
            return None, "Username or email already exists"
            
        except ValidationError as e:
            logger.error(f"Validation error registering user: {e}")
            return None, str(e)
            
        except Exception as e:
            logger.error(f"Error registering user: {e}")
            return None, "An error occurred during registration"
    
    @staticmethod
    def authenticate_user(username_or_email, password):
        """
        Authenticate a user with username/email and password.
        
        Args:
            username_or_email: Username or email address
            password: Plain text password
            
        Returns:
            (user, error): (User object, None) if successful, (None, error_message) otherwise
        """
        try:
            # Check if input is email or username
            if '@' in username_or_email:
                user = User.objects(email=username_or_email.lower()).first()
            else:
                user = User.objects(username=username_or_email).first()
            
            # Check if user exists
            if not user:
                return None, "Invalid username/email or password"
            
            # Check if user is active
            if not user.is_active:
                return None, "Account is disabled"
            
            # Verify password
            if not verify_password(password, user.password):
                return None, "Invalid username/email or password"
            
            logger.info(f"User authenticated successfully: {user.username}")
            return user, None
            
        except Exception as e:
            logger.error(f"Error authenticating user: {e}")
            return None, "An error occurred during authentication"
    
    @staticmethod
    def generate_tokens(user_id, additional_claims=None):
        """
        Generate access and refresh tokens for a user.
        
        Args:
            user_id: User ID to encode in the token
            additional_claims: Additional claims to include in the token
            
        Returns:
            Dictionary containing access_token and refresh_token
        """
        try:
            # Set up claims
            claims = {'sub': str(user_id)}
            
            if additional_claims:
                claims.update(additional_claims)
            
            # Create tokens
            access_token = create_access_token(
                identity=str(user_id),
                additional_claims=claims,
                fresh=True
            )
            
            refresh_token = create_refresh_token(
                identity=str(user_id),
                additional_claims=claims
            )
            
            return {
                'access_token': access_token,
                'refresh_token': refresh_token,
                'token_type': 'Bearer'
            }
            
        except Exception as e:
            logger.error(f"Error generating tokens: {e}")
            raise
    
    @staticmethod
    def get_user_by_id(user_id):
        """
        Get a user by ID.
        
        Args:
            user_id: User ID
            
        Returns:
            (user, error): (User object, None) if successful, (None, error_message) otherwise
        """
        try:
            user = User.objects(id=user_id).first()
            
            if not user:
                return None, "User not found"
            
            return user, None
            
        except Exception as e:
            logger.error(f"Error getting user by ID: {e}")
            return None, "An error occurred while retrieving user"
            
    @staticmethod
    def change_password(user_id, current_password, new_password):
        """
        Change a user's password.
        
        Args:
            user_id: User ID
            current_password: Current password
            new_password: New password
            
        Returns:
            (success, error): (True, None) if successful, (False, error_message) otherwise
        """
        try:
            # Get user
            user, error = AuthService.get_user_by_id(user_id)
            
            if error:
                return False, error
            
            # Verify current password
            if not verify_password(current_password, user.password):
                return False, "Current password is incorrect"
            
            # Validate new password
            password_valid, password_error = password_meets_requirements(new_password)
            if not password_valid:
                return False, password_error
                
            # Check if new password is the same as current password
            if verify_password(new_password, user.password):
                return False, "New password must be different from current password"
            
            # Hash new password
            hashed_password = hash_password(new_password)
            
            # Update password
            user.password = hashed_password
            user.updated_at = datetime.utcnow()
            user.save()
            
            logger.info(f"Password changed successfully for user: {user.username}")
            return True, None
            
        except Exception as e:
            logger.error(f"Error changing password: {e}")
            return False, "An error occurred while changing password"
    
    @staticmethod
    def generate_reset_token():
        """
        Generate a secure random reset token.
        
        Returns:
            String: Random reset token
        """
        # Generate a random 16-character token
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(16))
    
    @staticmethod
    def request_password_reset(email):
        """
        Request a password reset for a user with the given email.
        
        Args:
            email: User's email address
            
        Returns:
            (success, message, token): (True, success_message, reset_token) if successful,
                                    (False, error_message, None) otherwise
        """
        try:
            # Get user by email
            user = User.objects(email=email.lower()).first()
            
            if not user:
                # For security reasons, don't reveal if email exists or not
                return True, "If an account with this email exists, a password reset link will be sent", None
            
            # Generate reset token
            reset_token = AuthService.generate_reset_token()
            
            # Set reset token and expiration
            user.reset_token = reset_token
            user.reset_token_expires = datetime.utcnow() + timedelta(hours=24)
            user.save()
            
            # In a real production app, we would send an email here
            # For development purposes, we'll return the token directly
            logger.info(f"Password reset requested for user: {user.username}")
            
            return True, "Password reset link sent", reset_token
            
        except Exception as e:
            logger.error(f"Error requesting password reset: {e}")
            return False, "An error occurred while processing your request", None
    
    @staticmethod
    def reset_password(reset_token, new_password):
        """
        Reset a user's password using a reset token.
        
        Args:
            reset_token: Reset token
            new_password: New password
            
        Returns:
            (success, message): (True, success_message) if successful,
                             (False, error_message) otherwise
        """
        try:
            # Find user with matching reset token
            user = User.objects(
                reset_token=reset_token,
                reset_token_expires__gt=datetime.utcnow()
            ).first()
            
            if not user:
                return False, "Invalid or expired reset token"
            
            # Validate new password
            password_valid, password_error = password_meets_requirements(new_password)
            if not password_valid:
                return False, password_error
            
            # Hash new password
            hashed_password = hash_password(new_password)
            
            # Update password and clear reset token
            user.password = hashed_password
            user.reset_token = None
            user.reset_token_expires = None
            user.updated_at = datetime.utcnow()
            user.save()
            
            logger.info(f"Password reset successfully for user: {user.username}")
            return True, "Password has been reset successfully"
            
        except Exception as e:
            logger.error(f"Error resetting password: {e}")
            return False, "An error occurred while resetting password"
