"""
Email Verification Test Script

This script helps test the email verification flow by:
1. Creating a test user
2. Generating a verification token
3. Sending a verification email
4. Verifying the token

Usage:
    python test_email_verification.py
"""
import sys
import os
import logging
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create Flask app context
from app import create_app
app = create_app('development')

def test_verification_flow():
    """Test the full email verification flow"""
    
    with app.app_context():
        from models.user import User
        from services.auth_service import AuthService
        
        # Check if test user exists
        test_email = "test_user@example.com"
        test_user = User.objects(email=test_email).first()
        
        if not test_user:
            logger.info(f"Creating test user with email: {test_email}")
            # Create a test user
            test_user = User(
                username="test_user",
                email=test_email,
                first_name="Test",
                last_name="User",
                role="student",
                email_verified=False,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            test_user.set_password("Test@123")
            test_user.save()
            logger.info(f"Test user created with ID: {test_user.id}")
        else:
            logger.info(f"Test user already exists with ID: {test_user.id}")
            # Reset verification status for testing
            test_user.email_verified = False
            test_user.verification_token = None
            test_user.verification_token_expires = None
            test_user.save()
        
        # Generate and send verification email
        logger.info("Sending verification email...")
        success, message, token = AuthService.send_verification_email(test_user)
        
        if success:
            logger.info(f"Verification email sent successfully: {message}")
            logger.info(f"Verification token: {token}")
            
            # Verify the token
            logger.info("Verifying the token...")
            success, message, user = AuthService.verify_email(token)
            
            if success:
                logger.info(f"Email verification successful: {message}")
                
                # Check if email_verified flag is set
                user.reload()
                if user.email_verified:
                    logger.info("User email_verified flag is set to True ✅")
                else:
                    logger.error("User email_verified flag is not set to True ❌")
            else:
                logger.error(f"Email verification failed: {message}")
        else:
            logger.error(f"Failed to send verification email: {message}")

if __name__ == "__main__":
    logger.info("Starting email verification test")
    test_verification_flow()
    logger.info("Email verification test completed")
