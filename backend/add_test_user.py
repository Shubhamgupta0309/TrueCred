"""
Add a test user with a wallet address directly through MongoEngine
"""
import sys
import os
from datetime import datetime
from mongoengine import connect, Document, StringField, EmailField, BooleanField, DateTimeField
import logging
from passlib.hash import pbkdf2_sha256

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define a simplified User model for this script
class User(Document):
    username = StringField(required=True, unique=True)
    email = EmailField(required=True, unique=True)
    password_hash = StringField(required=True)
    first_name = StringField()
    last_name = StringField()
    role = StringField(default='student')
    wallet_address = StringField(unique=True, sparse=True)
    is_active = BooleanField(default=True)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'users',  # Use the same collection as the main User model
        'indexes': [
            'username',
            'email',
            'wallet_address'
        ]
    }

# Connect to MongoDB
def connect_to_db():
    try:
        # Get MongoDB URI from environment or use default
        mongo_uri = 'mongodb+srv://truecred:truecred@cluster0.ozrvhec.mongodb.net/truecred'
        connect(host=mongo_uri)
        logger.info("Connected to MongoDB")
    except Exception as e:
        logger.error(f"Error connecting to MongoDB: {e}")
        sys.exit(1)

# Add or update a test user
def create_test_user(username, email, password, wallet_address):
    try:
        # Check if user already exists by username, email, or wallet
        existing_user = User.objects(username=username).first() or \
                       User.objects(email=email).first() or \
                       User.objects(wallet_address=wallet_address).first()
        
        if existing_user:
            logger.info(f"User already exists: {existing_user.username}")
            
            # Update wallet address
            existing_user.wallet_address = wallet_address.lower()
            existing_user.updated_at = datetime.utcnow()
            existing_user.save()
            
            logger.info(f"Updated wallet address for user: {existing_user.username}")
            return existing_user
        
        # Create new user
        new_user = User(
            username=username,
            email=email,
            password_hash=pbkdf2_sha256.hash(password),
            wallet_address=wallet_address.lower(),
            role='student',
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        new_user.save()
        
        logger.info(f"Created test user: {username} with wallet address: {wallet_address}")
        return new_user
    
    except Exception as e:
        logger.error(f"Error creating test user: {e}")
        return None

if __name__ == '__main__':
    # Connect to database
    connect_to_db()
    
    # Test wallet address (replace with your MetaMask address)
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
