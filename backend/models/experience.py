"""
Experience model for the TrueCred application.
"""
import os
from datetime import datetime
from mongoengine import (
    Document, StringField, DateTimeField, ReferenceField, 
    ListField, BooleanField, DictField, URLField, DENY, CASCADE
)
from .user import User

class Experience(Document):
    """
    Experience model representing a professional or educational experience in the TrueCred system.
    
    Attributes:
        user: Reference to the User who owns this experience
        title: Title/role of the experience
        organization: Company or institution name
        type: Type of experience (work, education)
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
        rejection_reason: Reason for rejection if verification was declined
        credentials: List of credentials associated with this experience
        pending_verification: Whether verification is currently pending
        verification_attempts: Number of verification attempts made
        metadata: Additional metadata about the experience
        created_at: Timestamp when the record was created
        updated_at: Timestamp when the record was last updated
    """
    
    # Relationships
    user = ReferenceField(User, required=True, reverse_delete_rule=CASCADE)
    
    # Basic experience information
    title = StringField(required=True, max_length=200)
    organization = StringField(required=True, max_length=200)
    type = StringField(choices=['work', 'education'], default='work')
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
    rejection_reason = StringField(max_length=500)
    pending_verification = BooleanField(default=False)
    verification_attempts = ListField(DictField()) # Store history of verification attempts
    verification_status = StringField(default='pending', choices=[
        'pending', 'verified', 'rejected', 'revoked', 'expired'
    ])
    
    # IPFS Storage
    ipfs_hash = StringField()               # IPFS hash for the main experience document
    ipfs_metadata_hash = StringField()      # IPFS hash for experience metadata
    document_hashes = DictField()           # Dictionary of associated document IPFS hashes (key: document name, value: IPFS hash)
    document_url = URLField()               # URL to the main experience document
    blockchain_hash = StringField()         # Hash stored on the blockchain for verification
    
    # Linked credentials
    credentials = ListField(ReferenceField('Credential'))
    
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
            'is_verified',
            'pending_verification',
            'type',
            {'fields': ['ipfs_hash'], 'sparse': True, 'unique': True},
            {'fields': ['ipfs_metadata_hash'], 'sparse': True},
            {'fields': ['blockchain_hash'], 'sparse': True, 'unique': True}
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
        self.pending_verification = False
        
        # Record this verification attempt
        attempt = {
            'timestamp': datetime.utcnow(),
            'verifier': str(verified_by.id),
            'result': 'approved',
            'data': verification_data or {}
        }
        self.verification_attempts.append(attempt)
        
        if verification_data:
            self.verification_data = verification_data
            
        self.save()
        return self
    
    def reject_verification(self, verified_by, reason, verification_data=None):
        """
        Reject verification of an experience.
        
        Args:
            verified_by: User who rejected this verification
            reason: Reason for rejection
            verification_data: Optional data about the verification attempt
        
        Returns:
            Self for method chaining
        """
        self.is_verified = False
        self.pending_verification = False
        self.rejection_reason = reason
        
        # Record this verification attempt
        attempt = {
            'timestamp': datetime.utcnow(),
            'verifier': str(verified_by.id),
            'result': 'rejected',
            'reason': reason,
            'data': verification_data or {}
        }
        self.verification_attempts.append(attempt)
        
        self.save()
        return self
    
    def request_verification(self, verification_data=None):
        """
        Request verification for this experience.
        
        Args:
            verification_data: Optional data about the verification request
        
        Returns:
            Self for method chaining
        """
        self.pending_verification = True
        
        # Record this verification request
        attempt = {
            'timestamp': datetime.utcnow(),
            'requester': str(self.user.id),
            'result': 'pending',
            'data': verification_data or {}
        }
        self.verification_attempts.append(attempt)
        
        self.save()
        return self
    
    def store_in_ipfs(self, ipfs_service, document_data=None, metadata=None):
        """
        Store the experience data in IPFS.
        
        Args:
            ipfs_service: IPFS service to use for storage
            document_data: Optional document data to store (bytes)
            metadata: Optional additional metadata
            
        Returns:
            Self for method chaining
        """
        if not ipfs_service:
            raise ValueError("IPFS service is required")
            
        # Create experience data dictionary
        experience_data = self.to_json()
        
        # Add any additional metadata
        if metadata:
            experience_data.update(metadata)
        
        # Store experience data as JSON in IPFS
        result = ipfs_service.add_json(experience_data)
        
        if 'error' in result:
            raise ValueError(f"Failed to store experience data in IPFS: {result['error']}")
            
        # Update experience with IPFS hash
        self.ipfs_hash = result['Hash']
        
        # If document provided, store that too
        if document_data:
            # If this is a string path to a file, read it first
            if isinstance(document_data, str) and os.path.isfile(document_data):
                with open(document_data, 'rb') as f:
                    document_data = f.read()
            
            # Store document data
            doc_result = ipfs_service.add_file(document_data)
            
            if 'error' in doc_result:
                raise ValueError(f"Failed to store document in IPFS: {doc_result['error']}")
                
            # Initialize document_hashes if needed
            if not hasattr(self, 'document_hashes') or not self.document_hashes:
                self.document_hashes = {}
                
            # Add document hash to the experience's document hashes
            doc_name = f"experience_{self.id}_document"
            self.document_hashes[doc_name] = doc_result['Hash']
            
            # Create metadata with both hashes
            meta_data = {
                'experience_hash': self.ipfs_hash,
                'document_hash': doc_result['Hash'],
                'experience_id': str(self.id),
                'user_id': str(self.user.id),
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # Store metadata
            meta_result = ipfs_service.add_json(meta_data)
            
            if 'error' not in meta_result:
                self.ipfs_metadata_hash = meta_result['Hash']
        
        # Save changes to the database
        self.save()
        return self
        
    def add_document_to_ipfs(self, ipfs_service, document_data, document_name):
        """
        Add a document related to this experience to IPFS.
        
        Args:
            ipfs_service: IPFS service to use for storage
            document_data: Document data to store (bytes)
            document_name: Name to associate with the document
            
        Returns:
            Self for method chaining
        """
        if not ipfs_service:
            raise ValueError("IPFS service is required")
            
        # If this is a string path to a file, read it first
        if isinstance(document_data, str) and os.path.isfile(document_data):
            with open(document_data, 'rb') as f:
                document_data = f.read()
                
        # Store document in IPFS
        result = ipfs_service.add_file(document_data)
        
        if 'error' in result:
            raise ValueError(f"Failed to store document in IPFS: {result['error']}")
            
        # Initialize document_hashes if needed
        if not hasattr(self, 'document_hashes') or not self.document_hashes:
            self.document_hashes = {}
            
        # Add document hash to the experience's document hashes
        self.document_hashes[document_name] = result['Hash']
        
        # Save changes to the database
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
            'type': self.type,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'description': self.description,
            'location': self.location,
            'skills': self.skills,
            'is_current': self.is_current,
            'is_verified': self.is_verified,
            'verified_by': str(self.verified_by.id) if self.verified_by else None,
            'verified_at': self.verified_at.isoformat() if self.verified_at else None,
            'pending_verification': self.pending_verification,
            'rejection_reason': self.rejection_reason,
            'verification_attempts': self.verification_attempts,
            'credentials': [str(cred.id) for cred in self.credentials] if self.credentials else [],
            'ipfs_hash': self.ipfs_hash,
            'ipfs_metadata_hash': self.ipfs_metadata_hash,
            'document_hashes': self.document_hashes,
            'blockchain_hash': self.blockchain_hash,
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __str__(self):
        """String representation of the experience."""
        return f"Experience(title={self.title}, organization={self.organization}, verified={self.is_verified})"
