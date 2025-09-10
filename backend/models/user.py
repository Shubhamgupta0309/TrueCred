"""
User model for the TrueCred application.
"""
from datetime import datetime
import re
from mongoengine import (
    Document, StringField, EmailField, DateTimeField, 
    BooleanField, ListField, ReferenceField, DENY
)
from mongoengine.errors import ValidationError

class User(Document):
    """
    User model representing a user in the TrueCred system.
    
    Attributes:
        username: User's unique username
        email: User's email address
        password: Hashed password
        role: User role (default: 'user')
        first_name: User's first name (optional)
        last_name: User's last name (optional)
        is_active: Whether the user account is active
        created_at: Timestamp when the user was created
        updated_at: Timestamp when the user was last updated
    """
    
    # Basic user information
    username = StringField(
        required=True, 
        unique=True, 
        min_length=3, 
        max_length=50,
        regex=r'^[a-zA-Z0-9_]+$'  # Only alphanumeric and underscore
    )
    email = EmailField(required=True, unique=True)
    password = StringField(required=True, min_length=8)  # Stores hashed password
    
    # User details
    role = StringField(
        required=True, 
        choices=['user', 'issuer', 'admin', 'student', 'college', 'company'],
        default='user'
    )
    first_name = StringField(max_length=50)
    last_name = StringField(max_length=50)
    profile_image = StringField()  # URL or path to profile image
    wallet_address = StringField(unique=True, sparse=True)  # Ethereum wallet address
    
    # Account status
    is_active = BooleanField(default=True)
    email_verified = BooleanField(default=False)
    
    # Password reset
    reset_token = StringField()
    reset_token_expires = DateTimeField()
    
    # Email verification
    verification_token = StringField()
    verification_token_expires = DateTimeField()
    
    # Metadata
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    
    # Configuration
    meta = {
        'collection': 'users',
        'indexes': [
            {'fields': ['username'], 'unique': True},
            {'fields': ['email'], 'unique': True}
        ],
        'ordering': ['-created_at']
    }
    
    def clean(self):
        """
        Custom validation for the user model.
        """
        # Ensure email is lowercase
        if self.email:
            self.email = self.email.lower()
        
        # Username validation - more complex than just the regex
        if self.username:
            if not re.match(r'^[a-zA-Z0-9_]+$', self.username):
                raise ValidationError('Username can only contain letters, numbers, and underscores')
            
            if self.username.isdigit():
                raise ValidationError('Username cannot be all numbers')
    
    def save(self, *args, **kwargs):
        """
        Override save method to update the updated_at field.
        """
        self.updated_at = datetime.utcnow()
        return super(User, self).save(*args, **kwargs)
    
    @classmethod
    def find_by_email(cls, email):
        """
        Find a user by email.
        
        Args:
            email: Email to search for
        
        Returns:
            User document or None if not found
        """
        return cls.objects(email=email.lower()).first()
    
    @classmethod
    def find_by_username(cls, username):
        """
        Find a user by username.
        
        Args:
            username: Username to search for
        
        Returns:
            User document or None if not found
        """
        return cls.objects(username=username).first()
    
    def to_json(self):
        """
        Convert user to JSON-serializable dictionary.
        
        Returns:
            Dictionary representation of the user (excluding password)
        """
        return {
            'id': str(self.id),
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'profile_image': self.profile_image,
            'wallet_address': self.wallet_address,
            'is_active': self.is_active,
            'email_verified': self.email_verified,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __str__(self):
        """String representation of the user."""
        return f"User(username={self.username}, email={self.email}, role={self.role})"
    
    @classmethod
    def find_by_email(cls, email):
        """
        Find a user by email.
        
        Args:
            email: Email to search for
        
        Returns:
            User document or None if not found
        """
        return cls.objects(email=email.lower()).first()
    
    @classmethod
    def find_by_username(cls, username):
        """
        Find a user by username.
        
        Args:
            username: Username to search for
        
        Returns:
            User document or None if not found
        """
        return cls.objects(username=username).first()
    
    @classmethod
    def find_by_wallet_address(cls, wallet_address):
        """
        Find a user by wallet address.
        
        Args:
            wallet_address: Ethereum wallet address to search for
        
        Returns:
            User document or None if not found
        """
        import logging
        logger = logging.getLogger(__name__)
        
        if not wallet_address:
            logger.warning("Empty wallet address provided to find_by_wallet_address")
            return None
            
        # Normalize the wallet address to lowercase
        normalized_address = wallet_address.lower()
        logger.info(f"Looking up user with normalized wallet address: {normalized_address}")
        
        # Try to find the user
        user = cls.objects(wallet_address=normalized_address).first()
        
        if user:
            logger.info(f"Found user {user.username} with wallet address: {normalized_address}")
        else:
            logger.info(f"No user found with wallet address: {normalized_address}")
            
        return user
