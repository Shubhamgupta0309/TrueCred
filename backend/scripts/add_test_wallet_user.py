"""
Create a test user with a specific wallet address for testing wallet authentication
"""
import sys
import os
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add parent directory to path so we can import app context
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Test wallet address from the error logs
TEST_WALLET = "0x21e3812906ff2c3dc96c255d98d2d99156ff3fac"

def main():
    try:
        # Import here to avoid circular imports
        from app import create_app
        from models.user import User
        from passlib.hash import pbkdf2_sha256
        
        # Create the Flask app and use its context
        app = create_app()
        
        with app.app_context():
            # Check if user already exists with this wallet
            existing_user = User.find_by_wallet_address(TEST_WALLET)
            
            if existing_user:
                logger.info(f"User already exists with wallet address: {TEST_WALLET}")
                logger.info(f"Username: {existing_user.username}")
                logger.info(f"Email: {existing_user.email}")
                return
            
            # Check if test user exists (to update it)
            test_user = User.find_by_username("testuser") or User.find_by_email("testuser@example.com")
            
            if test_user:
                logger.info(f"Updating existing test user with wallet address: {TEST_WALLET}")
                test_user.wallet_address = TEST_WALLET
                test_user.save()
                logger.info(f"Updated user {test_user.username} with wallet address: {TEST_WALLET}")
                return
            
            # Create new user
            logger.info(f"Creating new test user with wallet address: {TEST_WALLET}")
            user = User(
                username="testuser",
                email="testuser@example.com",
                password=pbkdf2_sha256.hash("password123"),
                first_name="Test",
                last_name="User",
                wallet_address=TEST_WALLET,
                role="student",
                is_active=True
            )
            user.save()
            
            logger.info(f"Created test user 'testuser' with wallet address: {TEST_WALLET}")
        
    except Exception as e:
        logger.error(f"Error in script: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
