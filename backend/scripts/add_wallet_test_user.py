"""
Create a test user with a specific wallet address for testing wallet authentication
"""
import sys
import os
import logging
import traceback
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add parent directory to path so we can import app context
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    # Import the create_app function
    from app import create_app
    from models.user import User
    from mongoengine import connect, disconnect
    from passlib.hash import pbkdf2_sha256
except Exception as e:
    logger.error(f"Error importing modules: {e}")
    traceback.print_exc()
    sys.exit(1)

# Test wallet address from the error logs
TEST_WALLET = "0x21e3812906ff2c3dc96c255d98d2d99156ff3fac"

def main():
    print("Starting script to create wallet test user...")
    try:
        # Create a Flask app context
        app = create_app()
        
        with app.app_context():
            # Create or update user with the test wallet address
            try:
                # Check if user already exists with this wallet
                existing_user = User.find_by_wallet_address(TEST_WALLET)
                
                if existing_user:
                    print(f"User already exists with wallet address: {TEST_WALLET}")
                    print(f"Username: {existing_user.username}")
                    print(f"Email: {existing_user.email}")
                    return
                
                # Create a new test user
                username = "wallet_test_user"
                email = "wallet_test@example.com"
                
                # Hash a simple password
                password = pbkdf2_sha256.hash("TestPassword123!")
                
                print(f"Creating new user with wallet address: {TEST_WALLET}")
                new_user = User(
                    username=username,
                    email=email,
                    password=password,
                    wallet_address=TEST_WALLET.lower(),  # Store wallet address in lowercase
                    role="user",
                    is_active=True,
                    is_email_verified=True,  # Set to True to avoid verification issues
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                new_user.save()
                
                print(f"Successfully created user with wallet address: {TEST_WALLET}")
                print(f"Username: {username}")
                print(f"Email: {email}")
                
            except Exception as e:
                print(f"Error creating wallet test user: {e}")
                traceback.print_exc()
                raise
    except Exception as e:
        print(f"Error in main function: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()
    print("Script completed.")
