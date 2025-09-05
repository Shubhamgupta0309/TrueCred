"""
Credential model for the TrueCred application.
"""
from datetime import datetime
from flask_pymongo import PyMongo
from bson import ObjectId

class Credential:
    """
    Credential model representing a verifiable credential in the TrueCred system.
    """
    
    collection_name = 'credentials'
    
    def __init__(self, mongo):
        """
        Initialize the Credential model with the MongoDB connection.
        
        Args:
            mongo: PyMongo instance for database operations
        """
        self.mongo = mongo
        self.collection = self.mongo.db[self.collection_name]
    
    def create(self, user_id, title, issuer, description, blockchain_hash=None, ipfs_hash=None):
        """
        Create a new credential in the database.
        
        Args:
            user_id: ID of the user who owns this credential
            title: Title of the credential
            issuer: Organization or entity that issued the credential
            description: Description of the credential
            blockchain_hash: Hash of the credential on the blockchain (optional)
            ipfs_hash: IPFS hash for document storage (optional)
        
        Returns:
            Credential ID if successful
        """
        credential_data = {
            'user_id': str(user_id),
            'title': title,
            'issuer': issuer,
            'description': description,
            'blockchain_hash': blockchain_hash,
            'ipfs_hash': ipfs_hash,
            'verified': False,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        result = self.collection.insert_one(credential_data)
        return str(result.inserted_id)
    
    def find_by_id(self, credential_id):
        """
        Find a credential by ID.
        
        Args:
            credential_id: Credential ID to search for
        
        Returns:
            Credential document or None if not found
        """
        return self.collection.find_one({'_id': ObjectId(credential_id)})
    
    def find_by_user(self, user_id):
        """
        Find all credentials for a specific user.
        
        Args:
            user_id: User ID to search for
        
        Returns:
            Cursor of credential documents
        """
        return self.collection.find({'user_id': str(user_id)})
    
    def update(self, credential_id, update_data):
        """
        Update a credential's information.
        
        Args:
            credential_id: Credential ID to update
            update_data: Dictionary of fields to update
        
        Returns:
            True if successful, False otherwise
        """
        update_data['updated_at'] = datetime.utcnow()
        result = self.collection.update_one(
            {'_id': ObjectId(credential_id)},
            {'$set': update_data}
        )
        return result.modified_count > 0
    
    def verify(self, credential_id, verification_data=None):
        """
        Mark a credential as verified.
        
        Args:
            credential_id: Credential ID to verify
            verification_data: Optional data about the verification
        
        Returns:
            True if successful, False otherwise
        """
        update_data = {
            'verified': True,
            'verified_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        if verification_data:
            update_data['verification_data'] = verification_data
            
        result = self.collection.update_one(
            {'_id': ObjectId(credential_id)},
            {'$set': update_data}
        )
        return result.modified_count > 0
