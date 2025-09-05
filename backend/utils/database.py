"""
Database utility for MongoDB connection in the TrueCred application.
"""
from flask_pymongo import PyMongo

# MongoDB instance
mongo = None

def init_db(app):
    """
    Initialize the MongoDB connection.
    
    Args:
        app: Flask application instance
    
    Returns:
        PyMongo instance
    """
    global mongo
    mongo = PyMongo(app)
    return mongo

def get_db():
    """
    Get the MongoDB connection.
    
    Returns:
        PyMongo instance
    """
    global mongo
    return mongo
