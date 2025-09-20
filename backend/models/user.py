"""
User model for the TrueCred application.
"""
from datetime import datetime
import re
from mongoengine import (
    Document, StringField, EmailField, DateTimeField, 
    BooleanField, ListField, ReferenceField, DENY,
    EmbeddedDocument, EmbeddedDocumentListField, DictField
)
from mongoengine.errors import ValidationError

# Define Education embedded document
class Education(EmbeddedDocument):
    """Education entry for a user's profile"""
    institution = StringField(required=True, max_length=255)
    institution_id = StringField()
    degree = StringField(required=True, max_length=255)
    field_of_study = StringField(required=True, max_length=255)
    start_date = StringField(required=True, max_length=25)
    end_date = StringField(max_length=25)
    current = BooleanField(default=False)

    def clean(self):
        """Validate Education fields on save."""
        # Basic required checks are handled by mongoengine, but add
        # a sanity check for string lengths and that end_date is present
        # when current is False.
        if not self.institution or not self.institution.strip():
            raise ValidationError('Education.institution is required')
        if not self.degree or not self.degree.strip():
            raise ValidationError('Education.degree is required')
        if not self.field_of_study or not self.field_of_study.strip():
            raise ValidationError('Education.field_of_study is required')
        if not self.start_date or not self.start_date.strip():
            raise ValidationError('Education.start_date is required')
        if not self.current:
            # If not current, end_date should be provided (but allow empty for legacy)
            if not self.end_date or not self.end_date.strip():
                raise ValidationError('Education.end_date is required when not current')

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
    truecred_id = StringField(unique=True, sparse=True)  # Unique ID format: TC + 6 random digits
    affiliated_organizations = ListField(StringField())  # List of organizations/colleges the user is affiliated with
    
    # Education and profile information
    education = EmbeddedDocumentListField(Education)  # List of education history
    profile_completed = BooleanField(default=False)  # Whether the user has completed their profile
    
    # Account status
    is_active = BooleanField(default=True)
    is_email_verified = BooleanField(default=False)
    organization = StringField()  # For college/company admin users
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

        # If education present, run embedded document validation
        if hasattr(self, 'education') and self.education:
            valid_edu = []
            for edu in self.education:
                try:
                    # call clean on embedded document to validate
                    edu.clean()
                    valid_edu.append(edu)
                except ValidationError as e:
                    # re-raise with context
                    raise ValidationError(f'Invalid education entry: {str(e)}')

        # Auto-set profile_completed: true if at least one valid education exists
        try:
            if hasattr(self, 'education') and self.education and len(self.education) > 0:
                self.profile_completed = True
        except Exception:
            # don't block save for unexpected reasons here
            pass
    
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
        # Convert education embedded documents to dictionaries
        education_list = []
        if hasattr(self, 'education') and self.education:
            for edu in self.education:
                education_list.append({
                    'institution': edu.institution,
                    'institution_id': edu.institution_id,
                    'degree': edu.degree,
                    'field_of_study': edu.field_of_study,
                    'start_date': edu.start_date,
                    'end_date': edu.end_date,
                    'current': edu.current
                })
        
        return {
            'id': str(self.id),
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'profile_image': self.profile_image,
            'wallet_address': self.wallet_address,
            'truecred_id': self.truecred_id,
            'is_active': self.is_active,
            'email_verified': self.email_verified,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'education': education_list,
            'profile_completed': self.profile_completed if hasattr(self, 'profile_completed') else False
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
