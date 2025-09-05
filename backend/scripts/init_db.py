"""
Database initialization script for TrueCred.
"""
from mongoengine import connect, disconnect
from dotenv import load_dotenv
import os
import logging
from models.user import User
from models.credential import Credential
from models.experience import Experience

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db():
    """
    Initialize the database connection and create indexes.
    
    Returns:
        MongoDB connection instance
    """
    # Load environment variables
    load_dotenv()
    
    # Get MongoDB URI from environment
    mongo_uri = os.environ.get('MONGO_URI')
    
    if not mongo_uri:
        logger.error("MONGO_URI not found in environment variables")
        raise ValueError("MONGO_URI not set in environment variables")
    
    logger.info("Connecting to MongoDB...")
    
    try:
        # Disconnect from any existing connections
        disconnect()
        
        # Connect to MongoDB using MongoEngine
        conn = connect(
            host=mongo_uri,
            alias='default'
        )
        
        logger.info("Connected to MongoDB successfully")
        
        # Create indexes
        logger.info("Creating indexes...")
        
        # User indexes
        User.ensure_indexes()
        logger.info("Created User indexes")
        
        # Credential indexes
        Credential.ensure_indexes()
        logger.info("Created Credential indexes")
        
        # Experience indexes
        Experience.ensure_indexes()
        logger.info("Created Experience indexes")
        
        logger.info("All indexes created successfully")
        
        return conn
    
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise

if __name__ == "__main__":
    """
    Run database initialization when script is executed directly.
    """
    try:
        init_db()
        print("Database initialized successfully")
    except Exception as e:
        print(f"Error initializing database: {e}")
