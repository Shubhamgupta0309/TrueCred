"""
Credential model for the TrueCred application.
"""
import os
from datetime import datetime
from mongoengine import (
    Document, StringField, DateTimeField, BooleanField, 
    ReferenceField, DictField, URLField, DENY, ListField
)
from .user import User

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
        pending_verification: Whether verification is currently pending
        rejection_reason: Reason for rejection if verification was declined
        verification_attempts: List of verification attempt records
        related_experiences: References to related Experience records
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
    ipfs_metadata_hash = StringField()      # IPFS hash for credential metadata
    document_hashes = DictField()           # Dictionary of associated document IPFS hashes (key: document name, value: IPFS hash)
    document_url = URLField()
    verified = BooleanField(default=False)
    verified_at = DateTimeField()
    verification_data = DictField()
    blockchain_data = DictField()  # Store blockchain transaction data
    
    # Blockchain integration fields
    blockchain_tx_hash = StringField()  # Transaction hash from blockchain
    blockchain_credential_id = StringField()  # Credential ID from smart contract
    
    verification_status = StringField(default='pending', choices=[
        'pending', 'verified', 'rejected', 'revoked', 'expired'
    ])
    
    # Verification status and process
    pending_verification = BooleanField(default=False)
    rejection_reason = StringField(max_length=500)
    verification_attempts = ListField(DictField())  # Store history of verification attempts
    
    # Related experiences
    related_experiences = ListField(ReferenceField('Experience'))
    
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
            {'fields': ['pending_verification']},
            {'fields': ['verified']},
            {'fields': ['blockchain_hash'], 'sparse': True, 'unique': True, 'name': 'blockchain_hash_unique'},
            {'fields': ['ipfs_hash'], 'sparse': True, 'unique': True, 'name': 'ipfs_hash_unique'},
            {'fields': ['ipfs_metadata_hash'], 'sparse': True},
            {'fields': ['blockchain_tx_hash'], 'sparse': True},
            {'fields': ['blockchain_credential_id'], 'sparse': True}
        ],
        'ordering': ['-created_at']
    }
    
    def save(self, *args, **kwargs):
        """
        Override save method to update the updated_at field.
        """
        self.updated_at = datetime.utcnow()
        return super(Credential, self).save(*args, **kwargs)
    
    def verify(self, verified_by=None, verification_data=None):
        """
        Mark a credential as verified.
        
        Args:
            verified_by: User who verified this credential (optional)
            verification_data: Optional data about the verification
        
        Returns:
            Self for method chaining
        """
        self.verified = True
        self.verified_at = datetime.utcnow()
        self.pending_verification = False
        
        # Record this verification attempt
        attempt = {
            'timestamp': datetime.utcnow(),
            'verifier': str(verified_by.id) if verified_by else 'system',
            'result': 'approved',
            'data': verification_data or {}
        }
        
        if hasattr(self, 'verification_attempts'):
            self.verification_attempts.append(attempt)
        else:
            self.verification_attempts = [attempt]
        
        if verification_data:
            self.verification_data = verification_data
            
        self.save()
        return self
        
    def reject_verification(self, verified_by, reason, verification_data=None):
        """
        Reject verification of a credential.
        
        Args:
            verified_by: User who rejected this verification
            reason: Reason for rejection
            verification_data: Optional data about the verification attempt
        
        Returns:
            Self for method chaining
        """
        self.verified = False
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
        
        if hasattr(self, 'verification_attempts'):
            self.verification_attempts.append(attempt)
        else:
            self.verification_attempts = [attempt]
        
        self.save()
        return self
    
    def request_verification(self, verification_data=None):
        """
        Request verification for this credential.
        
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
        
        if hasattr(self, 'verification_attempts'):
            self.verification_attempts.append(attempt)
        else:
            self.verification_attempts = [attempt]
        
        self.save()
        return self
    
    def link_to_experience(self, experience):
        """
        Link this credential to an experience.
        
        Args:
            experience: Experience to link to
        
        Returns:
            Self for method chaining
        """
        if not hasattr(self, 'related_experiences'):
            self.related_experiences = []
            
        if experience.id not in [e.id for e in self.related_experiences]:
            self.related_experiences.append(experience)
            self.save()
            
            # Also update the experience to link back to this credential
            if not hasattr(experience, 'credentials'):
                experience.credentials = []
                
            if self.id not in [c.id for c in experience.credentials]:
                experience.credentials.append(self)
                experience.save()
                
        return self
    
    def unlink_from_experience(self, experience):
        """
        Unlink this credential from an experience.
        
        Args:
            experience: Experience to unlink from
        
        Returns:
            Self for method chaining
        """
        if hasattr(self, 'related_experiences') and experience.id in [e.id for e in self.related_experiences]:
            self.related_experiences = [e for e in self.related_experiences if e.id != experience.id]
            self.save()
            
            # Also update the experience to unlink from this credential
            if hasattr(experience, 'credentials') and self.id in [c.id for c in experience.credentials]:
                experience.credentials = [c for c in experience.credentials if c.id != self.id]
                experience.save()
                
        return self
    
    def store_in_ipfs(self, ipfs_service, document_data=None, metadata=None):
        """
        Store the credential data in IPFS.
        
        Args:
            ipfs_service: IPFS service to use for storage
            document_data: Optional document data to store (bytes)
            metadata: Optional additional metadata
            
        Returns:
            Self for method chaining
        """
        if not ipfs_service:
            raise ValueError("IPFS service is required")
            
        # Create credential data dictionary
        credential_data = self.to_json()
        
        # Add any additional metadata
        if metadata:
            credential_data.update(metadata)
        
        # Store credential data as JSON in IPFS
        result = ipfs_service.add_json(credential_data)
        
        if 'error' in result:
            raise ValueError(f"Failed to store credential data in IPFS: {result['error']}")
            
        # Update credential with IPFS hash
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
                
            # Add document hash to the credential's document hashes
            doc_name = f"credential_{self.id}_document"
            self.document_hashes[doc_name] = doc_result['Hash']
            
            # Create metadata with both hashes
            meta_data = {
                'credential_hash': self.ipfs_hash,
                'document_hash': doc_result['Hash'],
                'credential_id': str(self.id),
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
        Add a document related to this credential to IPFS.
        
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
            
        # Add document hash to the credential's document hashes
        self.document_hashes[document_name] = result['Hash']
        
        # Save changes to the database
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
            'ipfs_metadata_hash': self.ipfs_metadata_hash,
            'document_hashes': getattr(self, 'document_hashes', {}),
            'document_url': self.document_url,
            'verified': self.verified,
            'verified_at': self.verified_at.isoformat() if self.verified_at else None,
            'pending_verification': getattr(self, 'pending_verification', False),
            'rejection_reason': getattr(self, 'rejection_reason', None),
            'verification_attempts': getattr(self, 'verification_attempts', []),
            'related_experiences': [str(exp.id) for exp in getattr(self, 'related_experiences', [])] if hasattr(self, 'related_experiences') else [],
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __str__(self):
        """String representation of the credential."""
        return f"Credential(title={self.title}, issuer={self.issuer}, verified={self.verified})"
