"""
Create a test user with a wallet address for testing wallet authentication
"""
import sys
import os
from datetime import datetime

# Add parent directory to path so we can import from models
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.user import User
from app import app
from mongoengine import connect
from passlib.hash import pbkdf2_sha256
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Connect to MongoDB
def setup_db():
    try:
        # Get MongoDB URI from environment or use default
        mongo_uri = os.environ.get('MONGODB_URI', 'mongodb+srv://truecred:truecred@cluster0.ozrvhec.mongodb.net/truecred')
        connect(host=mongo_uri)
        logger.info("Connected to MongoDB")
    except Exception as e:
        logger.error(f"Error connecting to MongoDB: {e}")
        sys.exit(1)

# Create a test user with wallet address
def create_test_user(username, email, password, wallet_address):
    try:
        # Check if user already exists
        existing_user = User.find_by_username(username) or User.find_by_email(email) or User.find_by_wallet_address(wallet_address)
        
        if existing_user:
            logger.info(f"User already exists: {existing_user.username}")
            
            # Update wallet address if needed
            if existing_user.wallet_address != wallet_address:
                existing_user.wallet_address = wallet_address
                existing_user.save()
                logger.info(f"Updated wallet address for user: {existing_user.username}")
            
            return existing_user
        
        # Create new user
        user = User(
            username=username,
            email=email,
            password_hash=pbkdf2_sha256.hash(password),
            wallet_address=wallet_address,
            role='student',
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        user.save()
        
        logger.info(f"Created test user: {username} with wallet address: {wallet_address}")
        return user
    
    except Exception as e:
        logger.error(f"Error creating test user: {e}")
        return None

if __name__ == '__main__':
    # Initialize database connection
    with app.app_context():
        setup_db()
        
        # Test wallet address - replace with your MetaMask address
        test_wallet = input("Enter your MetaMask wallet address: ")
        
        if not test_wallet:
            logger.error("Wallet address is required")
            sys.exit(1)
        
        # Create test user
        user = create_test_user(
            username="testuser",
            email="testuser@example.com",
            password="password123",
            wallet_address=test_wallet.lower()
        )
        
        if user:
            logger.info(f"Test user created successfully. Details:")
            logger.info(f"Username: {user.username}")
            logger.info(f"Email: {user.email}")
            logger.info(f"Wallet Address: {user.wallet_address}")
            logger.info(f"Role: {user.role}")
        else:
            logger.error("Failed to create test user")
