"""
Credential model for the TrueCred application.
"""
from datetime import datetime
from mongoengine import (
    Document, StringField, DateTimeField, BooleanField, 
    ReferenceField, DictField, URLField, DENY
)
from models.user import User

class Credential(Document):
    """
    Credential model representing a verifiable credential in the TrueCred system.
    
    Attributes:
        user: Reference to the User who owns this credential
        title: Title of the credential
        issuer: Organization or entity that issued the credential
        description: Description of the credential
        type: Type of credential (e.g., 'diploma', 'certificate', 'badge')
        issue_date: Date when the credential was issued
        expiry_date: Date when the credential expires (optional)
        blockchain_hash: Hash of the credential on the blockchain (optional)
        ipfs_hash: IPFS hash for document storage (optional)
        document_url: URL to the credential document (optional)
        verified: Whether the credential has been verified
        verified_at: Timestamp when the credential was verified
        verification_data: Additional data about the verification
        metadata: Additional metadata about the credential
        created_at: Timestamp when the record was created
        updated_at: Timestamp when the record was last updated
    """
    
    # Relationships
    user = ReferenceField(User, required=True, reverse_delete_rule=DENY)
    
    # Basic credential information
    title = StringField(required=True, max_length=200)
    issuer = StringField(required=True, max_length=200)
    description = StringField(max_length=2000)
    type = StringField(choices=[
        'diploma', 'degree', 'certificate', 'badge', 'award', 'license', 'other'
    ])
    
    # Dates
    issue_date = DateTimeField()
    expiry_date = DateTimeField()
    
    # Verification information
    blockchain_hash = StringField()
    ipfs_hash = StringField()
    document_url = URLField()
    verified = BooleanField(default=False)
    verified_at = DateTimeField()
    verification_data = DictField()
    
    # Additional information
    metadata = DictField()
    
    # Timestamps
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    
    # Configuration
    meta = {
        'collection': 'credentials',
        'indexes': [
            {'fields': ['user']},
            {'fields': ['title']},
            {'fields': ['issuer']},
            {'fields': ['type']},
            {'fields': ['blockchain_hash'], 'sparse': True, 'unique': True, 'name': 'blockchain_hash_unique'},
            {'fields': ['ipfs_hash'], 'sparse': True, 'unique': True, 'name': 'ipfs_hash_unique'}
        ],
        'ordering': ['-created_at']
    }
    
    def save(self, *args, **kwargs):
        """
        Override save method to update the updated_at field.
        """
        self.updated_at = datetime.utcnow()
        return super(Credential, self).save(*args, **kwargs)
    
    def verify(self, verification_data=None):
        """
        Mark a credential as verified.
        
        Args:
            verification_data: Optional data about the verification
        
        Returns:
            Self for method chaining
        """
        self.verified = True
        self.verified_at = datetime.utcnow()
        
        if verification_data:
            self.verification_data = verification_data
            
        self.save()
        return self
    
    def to_json(self):
        """
        Convert credential to JSON-serializable dictionary.
        
        Returns:
            Dictionary representation of the credential
        """
        return {
            'id': str(self.id),
            'user_id': str(self.user.id) if self.user else None,
            'title': self.title,
            'issuer': self.issuer,
            'description': self.description,
            'type': self.type,
            'issue_date': self.issue_date.isoformat() if self.issue_date else None,
            'expiry_date': self.expiry_date.isoformat() if self.expiry_date else None,
            'blockchain_hash': self.blockchain_hash,
            'ipfs_hash': self.ipfs_hash,
            'document_url': self.document_url,
            'verified': self.verified,
            'verified_at': self.verified_at.isoformat() if self.verified_at else None,
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __str__(self):
        """String representation of the credential."""
        return f"Credential(title={self.title}, issuer={self.issuer}, verified={self.verified})"
    
    def verify(self, verification_data=None):
        """
        Mark a credential as verified.
        
        Args:
            verification_data: Optional data about the verification
        
        Returns:
            Self for method chaining
        """
        self.verified = True
        self.verified_at = datetime.utcnow()
        
        if verification_data:
            self.verification_data = verification_data
            
        self.save()
        return self
    
    def to_json(self):
        """
        Convert credential to JSON-serializable dictionary.
        
        Returns:
            Dictionary representation of the credential
        """
        return {
            'id': str(self.id),
            'user_id': str(self.user.id) if self.user else None,
            'title': self.title,
            'issuer': self.issuer,
            'description': self.description,
            'type': self.type,
            'issue_date': self.issue_date.isoformat() if self.issue_date else None,
            'expiry_date': self.expiry_date.isoformat() if self.expiry_date else None,
            'blockchain_hash': self.blockchain_hash,
            'ipfs_hash': self.ipfs_hash,
            'document_url': self.document_url,
            'verified': self.verified,
            'verified_at': self.verified_at.isoformat() if self.verified_at else None,
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __str__(self):
        """String representation of the credential."""
        return f"Credential(title={self.title}, issuer={self.issuer}, verified={self.verified})"
