"""
Experience model for the TrueCred application.
"""
from datetime import datetime
from mongoengine import (
    Document, StringField, DateTimeField, ReferenceField, 
    ListField, BooleanField, DictField, DENY
)
from models.user import User

class Experience(Document):
    """
    Experience model representing a professional or educational experience in the TrueCred system.
    
    Attributes:
        user: Reference to the User who owns this experience
        title: Title/role of the experience
        organization: Company or institution name
        start_date: Start date of the experience
        end_date: End date of the experience (None for current)
        description: Description of the experience
        location: Location of the experience
        skills: List of skills associated with this experience
        is_current: Whether this is a current experience
        is_verified: Whether this experience has been verified
        verified_by: Reference to the User who verified this experience
        verified_at: Timestamp when the experience was verified
        verification_data: Additional data about the verification
        metadata: Additional metadata about the experience
        created_at: Timestamp when the record was created
        updated_at: Timestamp when the record was last updated
    """
    
    # Relationships
    user = ReferenceField(User, required=True, reverse_delete_rule=DENY)
    
    # Basic experience information
    title = StringField(required=True, max_length=200)
    organization = StringField(required=True, max_length=200)
    start_date = DateTimeField(required=True)
    end_date = DateTimeField()
    description = StringField(max_length=2000)
    location = StringField(max_length=200)
    
    # Skills
    skills = ListField(StringField(max_length=50))
    
    # Status
    is_current = BooleanField(default=False)
    
    # Verification
    is_verified = BooleanField(default=False)
    verified_by = ReferenceField(User, reverse_delete_rule=DENY)
    verified_at = DateTimeField()
    verification_data = DictField()
    
    # Additional information
    metadata = DictField()
    
    # Timestamps
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    
    # Configuration
    meta = {
        'collection': 'experiences',
        'indexes': [
            'user',
            'organization',
            'start_date',
            'end_date',
            'is_current',
            'is_verified'
        ],
        'ordering': ['-start_date']
    }
    
    def clean(self):
        """
        Custom validation for the experience model.
        """
        # Set is_current if end_date is None
        if self.end_date is None:
            self.is_current = True
        
        # Ensure end_date is after start_date if provided
        if self.end_date and self.start_date and self.end_date < self.start_date:
            from mongoengine.errors import ValidationError
            raise ValidationError('End date must be after start date')
    
    def save(self, *args, **kwargs):
        """
        Override save method to update the updated_at field.
        """
        self.updated_at = datetime.utcnow()
        return super(Experience, self).save(*args, **kwargs)
    
    def verify(self, verified_by, verification_data=None):
        """
        Mark an experience as verified.
        
        Args:
            verified_by: User who verified this experience
            verification_data: Optional data about the verification
        
        Returns:
            Self for method chaining
        """
        self.is_verified = True
        self.verified_by = verified_by
        self.verified_at = datetime.utcnow()
        
        if verification_data:
            self.verification_data = verification_data
            
        self.save()
        return self
    
    def to_json(self):
        """
        Convert experience to JSON-serializable dictionary.
        
        Returns:
            Dictionary representation of the experience
        """
        return {
            'id': str(self.id),
            'user_id': str(self.user.id) if self.user else None,
            'title': self.title,
            'organization': self.organization,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'description': self.description,
            'location': self.location,
            'skills': self.skills,
            'is_current': self.is_current,
            'is_verified': self.is_verified,
            'verified_by': str(self.verified_by.id) if self.verified_by else None,
            'verified_at': self.verified_at.isoformat() if self.verified_at else None,
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __str__(self):
        """String representation of the experience."""
        return f"Experience(title={self.title}, organization={self.organization}, verified={self.is_verified})"
