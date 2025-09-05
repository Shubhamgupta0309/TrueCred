"""
Script to drop existing indexes and recreate them properly.
"""
import os
import sys
from pathlib import Path

# Add the parent directory to the path so we can import from the root
parent_dir = str(Path(__file__).parent.parent)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from dotenv import load_dotenv
from mongoengine import connect, disconnect
import pymongo
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def reset_indexes():
    """
    Drop existing indexes and recreate them properly.
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
        # Connect directly with PyMongo
        client = pymongo.MongoClient(mongo_uri)
        db = client.get_database()
        
        # Drop indexes for users collection
        logger.info("Dropping indexes for users collection...")
        db.users.drop_indexes()
        logger.info("Successfully dropped indexes for users collection")
        
        # Drop indexes for credentials collection
        logger.info("Dropping indexes for credentials collection...")
        db.credentials.drop_indexes()
        logger.info("Successfully dropped indexes for credentials collection")
        
        # Drop indexes for experiences collection
        logger.info("Dropping indexes for experiences collection...")
        db.experiences.drop_indexes()
        logger.info("Successfully dropped indexes for experiences collection")
        
        # Close PyMongo connection
        client.close()
        
        # Now reconnect with MongoEngine to create the proper indexes
        logger.info("Connecting with MongoEngine to create proper indexes...")
        disconnect()
        connect(host=mongo_uri)
        
        # Import models
        from models.user import User
        from models.credential import Credential
        from models.experience import Experience
        
        # Create indexes
        logger.info("Creating indexes for User model...")
        User.ensure_indexes()
        
        logger.info("Creating indexes for Credential model...")
        Credential.ensure_indexes()
        
        logger.info("Creating indexes for Experience model...")
        Experience.ensure_indexes()
        
        logger.info("Successfully created all indexes")
        
    except Exception as e:
        logger.error(f"Error resetting indexes: {e}")
        sys.exit(1)
    
    finally:
        # Disconnect from MongoDB
        disconnect()
        logger.info("Disconnected from MongoDB")

if __name__ == "__main__":
    print("TrueCred - Reset MongoDB Indexes")
    reset_indexes()
    print("MongoDB indexes have been reset successfully")
