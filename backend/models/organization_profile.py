"""
Organization Profile model for storing detailed information about organizations.
"""
from mongoengine import Document, StringField, DateTimeField, ReferenceField
from datetime import datetime

class OrganizationProfile(Document):
    """
    Represents a detailed profile for an organization (college or company).
    """
    # Reference to the user
    user_id = StringField(required=True)
    
    # Basic information
    name = StringField(required=True, default='')  # Short name
    fullName = StringField(default='')  # Full legal name
    
    # Address information
    address = StringField()
    city = StringField()
    state = StringField()
    country = StringField()
    postalCode = StringField()
    
    # Contact information
    website = StringField()
    phone = StringField()
    email = StringField()
    
    # Additional information for educational institutions
    accreditationBody = StringField()
    establishmentYear = StringField()
    
    # General description
    description = StringField()
    
    # Timestamps
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    
    def to_json(self):
        """
        Convert the model to a JSON-serializable dictionary.
        
        Returns:
            dict: A dictionary representation of the model.
        """
        return {
            'id': str(self.id),
            'user_id': self.user_id,
            'name': self.name or '',
            'fullName': self.fullName or '',
            'address': self.address or '',
            'city': self.city or '',
            'state': self.state or '',
            'country': self.country or '',
            'postalCode': self.postalCode or '',
            'website': self.website or '',
            'phone': self.phone or '',
            'email': self.email or '',
            'accreditationBody': self.accreditationBody or '',
            'establishmentYear': self.establishmentYear or '',
            'description': self.description or '',
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    meta = {
        'collection': 'organization_profiles',
        'indexes': ['user_id']
    }
