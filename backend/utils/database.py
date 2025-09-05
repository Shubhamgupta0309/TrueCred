"""
Database utility for MongoDB connection in the TrueCred application.
"""
from flask_pymongo import PyMongo
from mongoengine import connect, disconnect
import logging
import os

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MongoDB instances
mongo = None
mongodb_uri = None

def init_db(app):
    """
    Initialize the MongoDB connection for both PyMongo and MongoEngine.
    
    Args:
        app: Flask application instance
    
    Returns:
        PyMongo instance
    """
    global mongo, mongodb_uri
    
    mongodb_uri = app.config.get('MONGO_URI')
    
    if not mongodb_uri:
        logger.error("MONGO_URI not found in application configuration")
        raise ValueError("MONGO_URI not set in application configuration")
    
    logger.info("Initializing MongoDB connection...")
    
    try:
        # Initialize PyMongo for Flask
        mongo = PyMongo(app)
        logger.info("PyMongo initialized successfully")
        
        # Initialize MongoEngine
        disconnect()  # Disconnect any existing connections
        connect(host=mongodb_uri, alias='default')
        logger.info("MongoEngine initialized successfully")
        
        # Test the connection
        mongo.db.command('ismaster')
        logger.info("MongoDB connection successful")
        
        # Create indexes for all models
        from models.user import User
        from models.credential import Credential
        from models.experience import Experience
        
        logger.info("Creating indexes for all models...")
        User.ensure_indexes()
        Credential.ensure_indexes()
        Experience.ensure_indexes()
        logger.info("Indexes created successfully")
    
    except Exception as e:
        logger.error(f"Error connecting to MongoDB: {e}")
        raise
    
    return mongo

def get_db():
    """
    Get the PyMongo database instance.
    
    Returns:
        PyMongo database instance
    """
    global mongo
    
    if mongo is None:
        raise ValueError("Database not initialized. Call init_db() first.")
    
    return mongo
