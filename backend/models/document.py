"""
Document model for TrueCred.

This model represents uploaded documents with IPFS storage
and blockchain verification capabilities.
"""
from mongoengine import Document as MongoDocument, StringField, IntField, BooleanField, DateTimeField, ObjectIdField
from datetime import datetime
from typing import Optional

class Document(MongoDocument):
    """Document model for storing document metadata."""

    # Primary identifiers
    document_id = StringField(required=True, unique=True)
    user_id = ObjectIdField(required=True)

    # File information
    filename = StringField(required=True)  # Secure filename
    original_filename = StringField(required=True)  # Original filename
    file_size = IntField(required=True)
    mime_type = StringField(required=True)

    # Document metadata
    document_type = StringField(required=True, default='general')  # degree, transcript, certificate, etc.
    title = StringField(required=True)
    description = StringField(default='')

    # IPFS storage
    ipfs_hash = StringField(required=True)
    file_hash = StringField(required=True)  # SHA-256 hash for integrity

    # Access control
    is_public = BooleanField(default=False)

    # Status fields
    upload_status = StringField(default='pending')  # pending, completed, failed
    blockchain_status = StringField(default='pending')  # pending, storing, stored, failed

    # Verification fields
    verification_status = StringField(default='pending')  # pending, verified, rejected
    verified_by = StringField()
    verified_at = DateTimeField()
    verification_comments = StringField()

    # Blockchain integration
    blockchain_tx_hash = StringField()
    credential_id = StringField()

    # Timestamps
    upload_timestamp = DateTimeField(default=datetime.utcnow)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)

    meta = {
        'collection': 'documents',
        'indexes': [
            'document_id',
            'user_id',
            'document_type',
            'verification_status',
            'upload_timestamp',
            'ipfs_hash'
        ]
    }

    def save(self, *args, **kwargs):
        """Override save to update timestamp."""
        self.updated_at = datetime.utcnow()
        return super().save(*args, **kwargs)

    def to_dict(self) -> dict:
        """Convert document to dictionary."""
        return {
            'document_id': self.document_id,
            'user_id': str(self.user_id),
            'filename': self.filename,
            'original_filename': self.original_filename,
            'file_size': self.file_size,
            'mime_type': self.mime_type,
            'document_type': self.document_type,
            'title': self.title,
            'description': self.description,
            'ipfs_hash': self.ipfs_hash,
            'file_hash': self.file_hash,
            'is_public': self.is_public,
            'upload_status': self.upload_status,
            'blockchain_status': self.blockchain_status,
            'verification_status': self.verification_status,
            'verified_by': self.verified_by,
            'verified_at': self.verified_at.isoformat() if self.verified_at else None,
            'verification_comments': self.verification_comments,
            'blockchain_tx_hash': self.blockchain_tx_hash,
            'credential_id': self.credential_id,
            'upload_timestamp': self.upload_timestamp.isoformat(),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    @classmethod
    def get_by_document_id(cls, document_id: str) -> Optional['Document']:
        """Get document by document ID."""
        return cls.objects(document_id=document_id).first()

    @classmethod
    def get_user_documents(cls, user_id: str) -> list:
        """Get all documents for a user."""
        return list(cls.objects(user_id=user_id).order_by('-upload_timestamp'))

    @classmethod
    def get_pending_verification(cls) -> list:
        """Get documents pending verification."""
        return list(cls.objects(verification_status='pending').order_by('-upload_timestamp'))

    @classmethod
    def get_verified_documents(cls) -> list:
        """Get verified documents."""
        return list(cls.objects(verification_status='verified').order_by('-upload_timestamp'))

    @classmethod
    def get_rejected_documents(cls) -> list:
        """Get rejected documents."""
        return list(cls.objects(verification_status='rejected').order_by('-upload_timestamp'))

    def mark_as_verified(self, verified_by: str, comments: str = '') -> None:
        """Mark document as verified."""
        self.verification_status = 'verified'
        self.verified_by = verified_by
        self.verified_at = datetime.utcnow()
        self.verification_comments = comments
        self.save()

    def mark_as_rejected(self, verified_by: str, comments: str = '') -> None:
        """Mark document as rejected."""
        self.verification_status = 'rejected'
        self.verified_by = verified_by
        self.verified_at = datetime.utcnow()
        self.verification_comments = comments
        self.save()

    def update_blockchain_status(self, status: str, tx_hash: str = None, credential_id: str = None) -> None:
        """Update blockchain storage status."""
        self.blockchain_status = status
        if tx_hash:
            self.blockchain_tx_hash = tx_hash
        if credential_id:
            self.credential_id = credential_id
        self.save()