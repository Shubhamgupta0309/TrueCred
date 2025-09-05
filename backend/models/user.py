"""
User model for the TrueCred application.
"""
from datetime import datetime
from flask_pymongo import PyMongo
from bson import ObjectId

class User:
    """
    User model representing a user in the TrueCred system.
    """
    
    collection_name = 'users'
    
    def __init__(self, mongo):
        """
        Initialize the User model with the MongoDB connection.
        
        Args:
            mongo: PyMongo instance for database operations
        """
        self.mongo = mongo
        self.collection = self.mongo.db[self.collection_name]
    
    def create(self, username, email, password_hash, role='user'):
        """
        Create a new user in the database.
        
        Args:
            username: User's username
            email: User's email address
            password_hash: Hashed password
            role: User role (default: 'user')
        
        Returns:
            User ID if successful
        """
        user_data = {
            'username': username,
            'email': email,
            'password': password_hash,
            'role': role,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        result = self.collection.insert_one(user_data)
        return str(result.inserted_id)
    
    def find_by_id(self, user_id):
        """
        Find a user by ID.
        
        Args:
            user_id: User ID to search for
        
        Returns:
            User document or None if not found
        """
        return self.collection.find_one({'_id': ObjectId(user_id)})
    
    def find_by_email(self, email):
        """
        Find a user by email.
        
        Args:
            email: Email to search for
        
        Returns:
            User document or None if not found
        """
        return self.collection.find_one({'email': email})
    
    def find_by_username(self, username):
        """
        Find a user by username.
        
        Args:
            username: Username to search for
        
        Returns:
            User document or None if not found
        """
        return self.collection.find_one({'username': username})
    
    def update(self, user_id, update_data):
        """
        Update a user's information.
        
        Args:
            user_id: User ID to update
            update_data: Dictionary of fields to update
        
        Returns:
            True if successful, False otherwise
        """
        update_data['updated_at'] = datetime.utcnow()
        result = self.collection.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': update_data}
        )
        return result.modified_count > 0
