"""
Test script for MongoEngine models.

This script tests the MongoEngine models by creating sample documents
and performing basic CRUD operations.
"""
import os
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add the parent directory to the path so we can import from the root
parent_dir = str(Path(__file__).parent.parent)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from dotenv import load_dotenv
from mongoengine import connect, disconnect
import logging

# Import models
from models.user import User
from models.credential import Credential
from models.experience import Experience

# Set up logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_models():
    """
    Test the MongoEngine models by performing CRUD operations.
    """
    # Load environment variables
    load_dotenv()
    
    # Get MongoDB URI
    mongo_uri = os.getenv('MONGO_URI')
    
    if not mongo_uri:
        logger.error("MONGO_URI not found in environment variables")
        sys.exit(1)
    
    logger.info("Connecting to MongoDB...")
    
    try:
        # Disconnect any existing connections
        disconnect()
        
        # Connect to MongoDB
        connect(host=mongo_uri)
        logger.info("Connected to MongoDB successfully")
        
        # Test User model
        logger.info("Testing User model...")
        test_user_model()
        
        # Test Credential model
        logger.info("Testing Credential model...")
        test_credential_model()
        
        # Test Experience model
        logger.info("Testing Experience model...")
        test_experience_model()
        
        logger.info("All tests completed successfully")
        
    except Exception as e:
        logger.error(f"Error testing models: {e}")
        sys.exit(1)
    
    finally:
        # Disconnect from MongoDB
        disconnect()
        logger.info("Disconnected from MongoDB")

def test_user_model():
    """
    Test the User model by creating a sample user.
    """
    # Clean up any existing test users
    User.objects(username='testuser').delete()
    
    # Create a test user
    user = User(
        username='testuser',
        email='test@example.com',
        password='hashed_password',  # In a real app, this would be hashed
        role='user',
        first_name='Test',
        last_name='User'
    )
    user.save()
    logger.info(f"Created test user: {user}")
    
    # Retrieve the user
    retrieved_user = User.objects(username='testuser').first()
    logger.info(f"Retrieved test user: {retrieved_user}")
    
    # Update the user
    retrieved_user.first_name = 'Updated'
    retrieved_user.save()
    logger.info(f"Updated test user: {retrieved_user}")
    
    # Convert to JSON
    user_json = retrieved_user.to_json()
    logger.info(f"User JSON: {user_json}")
    
    # Clean up
    retrieved_user.delete()
    logger.info("Deleted test user")

def test_credential_model():
    """
    Test the Credential model by creating a sample credential.
    """
    # Create a test user first
    User.objects(username='testuser').delete()
    user = User(
        username='testuser',
        email='test@example.com',
        password='hashed_password',
        role='user'
    )
    user.save()
    
    # Clean up any existing test credentials
    Credential.objects(title='Test Credential').delete()
    
    # Create a test credential
    credential = Credential(
        user=user,
        title='Test Credential',
        issuer='Test Issuer',
        description='This is a test credential',
        type='certificate',
        issue_date=datetime.utcnow(),
        blockchain_hash='0x123456789abcdef',
        ipfs_hash='QmT78zSuBmuS4z925WZfrqQ1qHaJ56DQaTfyMUF7F8ff5o'
    )
    credential.save()
    logger.info(f"Created test credential: {credential}")
    
    # Retrieve the credential
    retrieved_credential = Credential.objects(title='Test Credential').first()
    logger.info(f"Retrieved test credential: {retrieved_credential}")
    
    # Update the credential
    retrieved_credential.description = 'Updated description'
    retrieved_credential.save()
    logger.info(f"Updated test credential: {retrieved_credential}")
    
    # Verify the credential
    retrieved_credential.verify({'verification_method': 'test'})
    logger.info(f"Verified test credential: {retrieved_credential}")
    
    # Convert to JSON
    credential_json = retrieved_credential.to_json()
    logger.info(f"Credential JSON: {credential_json}")
    
    # Clean up
    retrieved_credential.delete()
    logger.info("Deleted test credential")
    user.delete()
    logger.info("Deleted test user")

def test_experience_model():
    """
    Test the Experience model by creating a sample experience.
    """
    # Create a test user first
    User.objects(username='testuser').delete()
    user = User(
        username='testuser',
        email='test@example.com',
        password='hashed_password',
        role='user'
    )
    user.save()
    
    # Create a verifier user
    User.objects(username='verifier').delete()
    verifier = User(
        username='verifier',
        email='verifier@example.com',
        password='hashed_password',
        role='issuer'
    )
    verifier.save()
    
    # Clean up any existing test experiences
    Experience.objects(title='Test Experience').delete()
    
    # Create a test experience
    start_date = datetime.utcnow() - timedelta(days=365)
    end_date = datetime.utcnow() - timedelta(days=30)
    
    experience = Experience(
        user=user,
        title='Test Experience',
        organization='Test Company',
        start_date=start_date,
        end_date=end_date,
        description='This is a test experience',
        location='Test Location',
        skills=['Python', 'MongoDB', 'Flask'],
        is_current=False
    )
    experience.save()
    logger.info(f"Created test experience: {experience}")
    
    # Retrieve the experience
    retrieved_experience = Experience.objects(title='Test Experience').first()
    logger.info(f"Retrieved test experience: {retrieved_experience}")
    
    # Update the experience
    retrieved_experience.description = 'Updated description'
    retrieved_experience.save()
    logger.info(f"Updated test experience: {retrieved_experience}")
    
    # Verify the experience
    retrieved_experience.verify(verifier, {'verification_method': 'test'})
    logger.info(f"Verified test experience: {retrieved_experience}")
    
    # Convert to JSON
    experience_json = retrieved_experience.to_json()
    logger.info(f"Experience JSON: {experience_json}")
    
    # Clean up
    retrieved_experience.delete()
    logger.info("Deleted test experience")
    user.delete()
    logger.info("Deleted test user")
    verifier.delete()
    logger.info("Deleted verifier user")

if __name__ == "__main__":
    print("TrueCred MongoEngine Models Test Script")
    test_models()
