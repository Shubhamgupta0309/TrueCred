"""
Experience model for the TrueCred application.
"""
from datetime import datetime
from bson import ObjectId

class Experience:
    """
    Experience model representing a professional or educational experience in the TrueCred system.
    """
    
    collection_name = 'experiences'
    
    def __init__(self, mongo):
        """
        Initialize the Experience model with the MongoDB connection.
        
        Args:
            mongo: MongoDB connection for database operations
        """
        self.mongo = mongo
        self.collection = self.mongo.db[self.collection_name]
    
    def create(self, user_id, title, organization, start_date, end_date=None, description=None, skills=None):
        """
        Create a new experience in the database.
        
        Args:
            user_id: ID of the user who owns this experience
            title: Title/role of the experience
            organization: Company or institution name
            start_date: Start date of the experience
            end_date: End date of the experience (optional, None for current)
            description: Description of the experience (optional)
            skills: List of skills associated with this experience (optional)
        
        Returns:
            Experience ID if successful
        """
        experience_data = {
            'user_id': str(user_id),
            'title': title,
            'organization': organization,
            'start_date': start_date,
            'end_date': end_date,
            'description': description,
            'skills': skills or [],
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        result = self.collection.insert_one(experience_data)
        return str(result.inserted_id)
    
    def find_by_id(self, experience_id):
        """
        Find an experience by ID.
        
        Args:
            experience_id: Experience ID to search for
        
        Returns:
            Experience document or None if not found
        """
        return self.collection.find_one({'_id': ObjectId(experience_id)})
    
    def find_by_user(self, user_id):
        """
        Find all experiences for a specific user.
        
        Args:
            user_id: User ID to search for
        
        Returns:
            Cursor of experience documents
        """
        return self.collection.find({'user_id': str(user_id)})
    
    def update(self, experience_id, update_data):
        """
        Update an experience's information.
        
        Args:
            experience_id: Experience ID to update
            update_data: Dictionary of fields to update
        
        Returns:
            True if successful, False otherwise
        """
        update_data['updated_at'] = datetime.utcnow()
        result = self.collection.update_one(
            {'_id': ObjectId(experience_id)},
            {'$set': update_data}
        )
        return result.modified_count > 0
    
    def delete(self, experience_id):
        """
        Delete an experience.
        
        Args:
            experience_id: Experience ID to delete
        
        Returns:
            True if successful, False otherwise
        """
        result = self.collection.delete_one({'_id': ObjectId(experience_id)})
        return result.deleted_count > 0
