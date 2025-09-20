"""
Authentication service for the TrueCred application.

This service provides functions for user registration, authentication,
and profile management.
"""
from models.user import User
from utils.password import hash_password, verify_password, password_meets_requirements
from utils.id_generator import generate_truecred_id
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
            
            # Generate unique TrueCred ID using improved logic
            truecred_id = AuthService._generate_unique_truecred_id()
            if not truecred_id:
                logger.error("Failed to generate unique TrueCred ID after multiple attempts")
                return None, "Failed to generate unique user ID. Please try again."
            
            # Create user
            user = User(
                username=username,
                email=email,
                password=hashed_password,
                first_name=first_name,
                last_name=last_name,
                role=role,
                truecred_id=truecred_id
            )
            
            # Save user
            user.save()
            
            # Send verification email
            success, message, token = AuthService.send_verification_email(user)
            if not success:
                logger.warning(f"Failed to send verification email: {message}")
            
            logger.info(f"User registered successfully: {username} with TrueCred ID: {truecred_id}")
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
    def _generate_unique_truecred_id():
        """
        Generate a unique TrueCred ID with improved logic and fallback mechanisms.
        
        Returns:
            A unique TrueCred ID string or None if generation fails
        """
        try:
            # First try the improved random generation with better uniqueness checking
            truecred_id = generate_truecred_id()
            if truecred_id and not User.objects(truecred_id=truecred_id).first():
                return truecred_id
            
            # If random generation fails, try sequential generation
            from utils.id_generator import generate_sequential_truecred_id
            sequential_id = generate_sequential_truecred_id()
            if sequential_id and not User.objects(truecred_id=sequential_id).first():
                return sequential_id
            
            # Final fallback: timestamp-based with additional uniqueness
            import time
            import random
            timestamp = str(int(time.time() * 1000000))[-8:]  # Microsecond precision
            random_suffix = str(random.randint(100, 999))
            fallback_id = f"TC{timestamp[-6:]}{random_suffix[-2:]}"
            
            # Ensure fallback is unique
            counter = 0
            original_fallback = fallback_id
            while User.objects(truecred_id=fallback_id).first() and counter < 1000:
                counter += 1
                fallback_id = f"TC{str(int(timestamp) + counter)[-6:]}{str(random.randint(100, 999))[-2:]}"
            
            if not User.objects(truecred_id=fallback_id).first():
                return fallback_id
            
            # If all methods fail, return None (should be extremely rare)
            logger.error("All TrueCred ID generation methods failed")
            return None
            
        except Exception as e:
            logger.error(f"Error generating TrueCred ID: {e}")
            return None
    
    @staticmethod
    def assign_missing_truecred_ids():
        """
        Assign TrueCred IDs to users who don't have them.
        Useful for data migration and fixing existing users.
        
        Returns:
            (success_count, error_count): Number of successful assignments and errors
        """
        try:
            users_without_ids = User.objects(truecred_id__exists=False).all()
            success_count = 0
            error_count = 0
            
            for user in users_without_ids:
                try:
                    truecred_id = AuthService._generate_unique_truecred_id()
                    if truecred_id:
                        user.truecred_id = truecred_id
                        user.save()
                        success_count += 1
                        logger.info(f"Assigned TrueCred ID {truecred_id} to user {user.username}")
                    else:
                        error_count += 1
                        logger.error(f"Failed to generate TrueCred ID for user {user.username}")
                except Exception as e:
                    error_count += 1
                    logger.error(f"Error assigning TrueCred ID to user {user.username}: {e}")
            
            logger.info(f"TrueCred ID assignment completed: {success_count} successful, {error_count} errors")
            return success_count, error_count
            
        except Exception as e:
            logger.error(f"Error in assign_missing_truecred_ids: {e}")
            return 0, 1
    
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
            
            # Check if email is verified
            if not user.email_verified:
                # Re-send verification email
                success, message, token = AuthService.send_verification_email(user)
                return None, "Email not verified. We've sent a new verification link to your email."
            
            logger.info(f"User authenticated successfully: {user.username}")
            return user, None
            
        except Exception as e:
            logger.error(f"Error authenticating user: {e}")
            return None, "An error occurred during authentication"
    
    @staticmethod
    def authenticate_wallet(wallet_address):
        """
        Authenticate a user with wallet address.
        
        Args:
            wallet_address: Ethereum wallet address
            
        Returns:
            (user, error): (User object, None) if successful, (None, error_message) otherwise
        """
        try:
            # Log the wallet address for debugging
            logger.info(f"Attempting to authenticate with wallet address: {wallet_address}")
            
            # Find user by wallet address
            user = User.find_by_wallet_address(wallet_address)
            
            # Log the user lookup result
            if user:
                logger.info(f"Found user with wallet address: {user.username}")
            else:
                logger.info(f"No user found with wallet address: {wallet_address}")
            
            # If no user found, create a new one
            if not user:
                return None, "No account found with this wallet address"
            
            # Check if user is active
            if not user.is_active:
                return None, "Account is disabled"
            
            logger.info(f"User authenticated via wallet successfully: {user.username}")
            return user, None
            
        except Exception as e:
            logger.error(f"Error authenticating user with wallet: {str(e)}")
            return None, "An error occurred during wallet authentication"
    
    @staticmethod
    def connect_wallet(user_id, wallet_address):
        """
        Connect a wallet address to an existing user account.
        
        Args:
            user_id: User ID
            wallet_address: Ethereum wallet address
            
        Returns:
            (success, error): (True, None) if successful, (False, error_message) otherwise
        """
        try:
            # Check if wallet is already connected to another account
            existing_user = User.find_by_wallet_address(wallet_address)
            if existing_user and str(existing_user.id) != user_id:
                return False, "Wallet address is already connected to another account"
            
            # Get user
            user = User.objects(id=user_id).first()
            if not user:
                return False, "User not found"
            
            # Update wallet address
            user.wallet_address = wallet_address.lower()
            user.updated_at = datetime.utcnow()
            user.save()
            
            logger.info(f"Wallet connected successfully for user: {user.username}")
            return True, None
            
        except Exception as e:
            logger.error(f"Error connecting wallet: {e}")
            return False, "An error occurred while connecting wallet"
    
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
    
    @staticmethod
    def generate_verification_token():
        """
        Generate a secure random email verification token.
        
        Returns:
            String: Random verification token
        """
        # Generate a random 32-character token
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(32))
    
    @staticmethod
    def send_verification_email(user):
        """
        Generate and store verification token and send a verification email.
        
        Args:
            user: User object
            
        Returns:
            (success, message, token): (True, success_message, verification_token) if successful,
                                      (False, error_message, None) otherwise
        """
        try:
            # Generate verification token
            verification_token = AuthService.generate_verification_token()
            
            # Save token to user
            user.verification_token = verification_token
            user.verification_token_expires = datetime.utcnow() + timedelta(days=7)
            user.save()
            
            # Get the app URL from config or use a default for development
            from flask import current_app
            base_url = current_app.config.get('FRONTEND_URL', 'http://localhost:5173')
            verification_url = f"{base_url}/verify-email?token={verification_token}"
            
            # Create email content
            subject = "TrueCred: Verify Your Email Address"
            message = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; background-color: #f9f9f9; margin: 0; padding: 0;">
                <div style="max-width: 600px; margin: 20px auto; padding: 30px; background-color: #ffffff; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                    <div style="text-align: center; margin-bottom: 30px;">
                        <img src="https://placeholder.com/wp-content/uploads/2018/10/placeholder.com-logo1.png" alt="TrueCred Logo" style="max-width: 200px; height: auto;">
                    </div>
                    <h2 style="color: #6047ff; text-align: center; margin-bottom: 20px;">Verify Your Email Address</h2>
                    <p>Hello {user.first_name or user.username},</p>
                    <p>Thank you for registering with TrueCred. To complete your registration and access your account, please verify your email address by clicking the button below:</p>
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{verification_url}" style="background-color: #6047ff; color: white; padding: 14px 28px; text-decoration: none; border-radius: 6px; font-weight: bold; display: inline-block;">Verify My Email</a>
                    </div>
                    <p style="font-size: 13px; color: #666;">If the button doesn't work, copy and paste this link into your browser:</p>
                    <p style="background-color: #f5f5f5; padding: 10px; border-radius: 4px; word-break: break-all; font-size: 13px;"><a href="{verification_url}" style="color: #6047ff; text-decoration: none;">{verification_url}</a></p>
                    <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; font-size: 13px; color: #666;">
                        <p><strong>Important:</strong> This link will expire in 7 days.</p>
                        <p>If you did not create a TrueCred account, you can safely ignore this email.</p>
                        <p>For help or questions, contact our support team at support@truecred.com</p>
                        <p style="text-align: center; margin-top: 20px;">© 2023 TrueCred. All rights reserved.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Import here to avoid circular imports
            from services.notification_service import NotificationService
            
            # Send the email using NotificationService
            notification_result = NotificationService.send_notification(
                to=user.email,
                subject=subject,
                message=message,
                notification_type='email',
                metadata={'html': True, 'verification_token': verification_token}
            )
            
            # Log for development purposes
            logger.info(f"Verification email would be sent to: {user.email} with token: {verification_token}")
            
            return True, "Verification email sent", verification_token
            
        except Exception as e:
            logger.error(f"Error sending verification email: {e}")
            return False, "An error occurred while sending verification email", None
    
    @staticmethod
    def verify_email(verification_token):
        """
        Verify a user's email using a verification token.
        
        Args:
            verification_token: Verification token
            
        Returns:
            (success, message, user): (True, success_message, user) if successful,
                                     (False, error_message, None) otherwise
        """
        try:
            # Find user with matching verification token
            user = User.objects(
                verification_token=verification_token,
                verification_token_expires__gt=datetime.utcnow()
            ).first()
            
            if not user:
                return False, "Invalid or expired verification token", None
            
            # Mark email as verified and clear verification token
            user.email_verified = True
            user.verification_token = None
            user.verification_token_expires = None
            user.updated_at = datetime.utcnow()
            user.save()
            
            logger.info(f"Email verified successfully for user: {user.username}")
            return True, "Email has been verified successfully", user
            
        except Exception as e:
            logger.error(f"Error verifying email: {e}")
            return False, "An error occurred while verifying email", None
    
    @staticmethod
    def verify_refresh_token(refresh_token):
        """
        Verify a refresh token and extract the user ID.
        
        Args:
            refresh_token: JWT refresh token
            
        Returns:
            user_id: User ID if token is valid, None otherwise
        """
        try:
            from utils.jwt_helpers import verify_token
            
            # Verify the token
            payload = verify_token(refresh_token, is_refresh=True)
            
            if not payload:
                logger.error("Invalid refresh token")
                return None
            
            # Extract user ID from the token payload
            user_id = payload.get('sub') or payload.get('identity')
            
            if not user_id:
                logger.error("No user ID in refresh token")
                return None
            
            # Check if user exists
            user = User.objects(id=user_id).first()
            
            if not user:
                logger.error(f"User not found for ID: {user_id}")
                return None
            
            return user_id
            
        except Exception as e:
            logger.error(f"Error verifying refresh token: {e}")
            return None
