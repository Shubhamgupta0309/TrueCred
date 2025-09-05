"""
Setup script for MongoDB connection and initialization.
"""
import os
import sys
import subprocess
import platform
from dotenv import load_dotenv
from pathlib import Path

# Add the parent directory to the path so we can import from the root
parent_dir = str(Path(__file__).parent.parent)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

import logging
from mongoengine import connect, disconnect

# Import models to register them with MongoEngine
from models.user import User
from models.credential import Credential
from models.experience import Experience

# Set up logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_mongodb_installed():
    """
    Check if MongoDB is installed locally.
    
    Returns:
        True if MongoDB is installed, False otherwise
    """
    try:
        # Try to run mongod --version
        result = subprocess.run(
            ['mongod', '--version'], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            text=True
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False

def setup_mongodb():
    """
    Guide the user through setting up MongoDB.
    """
    print("\n=== MongoDB Setup ===")
    
    # Check if MongoDB is installed
    if check_mongodb_installed():
        print("✅ MongoDB is installed.")
    else:
        print("❌ MongoDB is not installed.")
        print("\nPlease install MongoDB:")
        
        system = platform.system()
        if system == "Windows":
            print("1. Download the MongoDB Community Server from https://www.mongodb.com/try/download/community")
            print("2. Follow the installation instructions")
        elif system == "Darwin":  # macOS
            print("1. Install using Homebrew: brew tap mongodb/brew && brew install mongodb-community")
        else:  # Linux
            print("1. Follow the instructions at https://docs.mongodb.com/manual/administration/install-on-linux/")
        
        print("\nAfter installation, run this script again.")
        return False
    
    # Check if MONGO_URI is set in .env
    load_dotenv()
    mongo_uri = os.environ.get('MONGO_URI')
    
    if not mongo_uri:
        print("❌ MONGO_URI is not set in the .env file.")
        
        # Suggest a default URI
        default_uri = "mongodb://localhost:27017/truecred"
        
        # Ask the user if they want to use the default URI
        response = input(f"Do you want to use the default URI '{default_uri}'? (y/n): ")
        
        if response.lower() == 'y':
            # Update the .env file
            with open('.env', 'a') as f:
                f.write(f"\nMONGO_URI={default_uri}\n")
            print(f"✅ Added MONGO_URI={default_uri} to .env file.")
            mongo_uri = default_uri
        else:
            uri = input("Enter your MongoDB URI: ")
            with open('.env', 'a') as f:
                f.write(f"\nMONGO_URI={uri}\n")
            print(f"✅ Added MONGO_URI={uri} to .env file.")
            mongo_uri = uri
    else:
        print(f"✅ MONGO_URI is set to {mongo_uri}")
    
    # Initialize database with MongoEngine
    initialize_mongodb(mongo_uri)
    
    return True

def initialize_mongodb(mongo_uri):
    """
    Initialize MongoDB with the required collections and indexes using MongoEngine.
    
    Args:
        mongo_uri: MongoDB connection URI
    """
    try:
        logger.info("Connecting to MongoDB with MongoEngine...")
        
        # Disconnect any existing connections
        disconnect()
        
        # Connect to MongoDB using MongoEngine
        connect(host=mongo_uri)
        logger.info("Connected to MongoDB successfully")
        
        # Ensure indexes are created for each model
        logger.info("Creating indexes for User model...")
        User.ensure_indexes()
        
        logger.info("Creating indexes for Credential model...")
        Credential.ensure_indexes()
        
        logger.info("Creating indexes for Experience model...")
        Experience.ensure_indexes()
        
        logger.info("MongoDB initialization completed successfully")
        print("✅ Successfully initialized MongoDB with required collections and indexes.")
        
    except Exception as e:
        logger.error(f"Error initializing MongoDB: {e}")
        print(f"❌ Error initializing MongoDB: {e}")
    
    finally:
        # Disconnect from MongoDB
        disconnect()
        logger.info("Disconnected from MongoDB")

if __name__ == "__main__":
    print("TrueCred MongoDB Setup Script")
    setup_mongodb()
