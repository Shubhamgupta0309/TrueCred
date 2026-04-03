"""Certificate Template Model for OCR-based verification."""
from mongoengine import Document, StringField, IntField, BooleanField, DateTimeField, DictField, ListField
from datetime import datetime


class CertificateTemplate(Document):
    """Model for storing certificate templates from organizations."""
    
    meta = {
        'collection': 'certificate_templates',
        'indexes': [
            'organization_id',
            'template_type',
            'is_active'
        ]
    }
    
    # Organization details
    organization_id = StringField(required=True)
    organization_name = StringField(required=True)
    organization_type = StringField(required=True, choices=['college', 'company'])
    
    # Template metadata
    template_name = StringField(required=True)
    template_type = StringField(required=True)  # degree, internship, work_experience, etc.
    
    # File information
    file_url = StringField(required=True)  # IPFS or cloud storage URL
    file_hash = StringField(required=True)  # For integrity verification
    
    # OCR extracted data
    extracted_text = StringField()  # Full OCR text
    key_fields = DictField()  # Structured data: {name_position, date_position, etc.}
    
    # Template features for matching
    template_features = DictField()  # Visual features: logo position, layout, etc.
    layout_hash = StringField()  # Hash for quick template matching
    
    # Statistics
    total_verifications = IntField(default=0)
    successful_matches = IntField(default=0)
    average_confidence = IntField(default=0)  # 0-100
    
    # Status
    is_active = BooleanField(default=True)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    uploaded_by = StringField(required=True)  # User who uploaded
    
    # Validation rules
    required_fields = ListField(StringField())  # Fields that must be present
    optional_fields = ListField(StringField())
    
    def to_json(self):
        """Convert template to JSON format."""
        return {
            'id': str(self.id),
            'organization_id': self.organization_id,
            'organization_name': self.organization_name,
            'organization_type': self.organization_type,
            'template_name': self.template_name,
            'template_type': self.template_type,
            'file_url': self.file_url,
            'total_verifications': self.total_verifications,
            'successful_matches': self.successful_matches,
            'average_confidence': self.average_confidence,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'uploaded_by': self.uploaded_by,
            'required_fields': self.required_fields,
            'optional_fields': self.optional_fields
        }
    
    def update_statistics(self, confidence_score, was_successful):
        """Update template statistics after verification."""
        self.total_verifications += 1
        if was_successful:
            self.successful_matches += 1
        
        # Update rolling average
        if self.total_verifications == 1:
            self.average_confidence = confidence_score
        else:
            self.average_confidence = int(
                (self.average_confidence * (self.total_verifications - 1) + confidence_score) 
                / self.total_verifications
            )
        
        self.updated_at = datetime.utcnow()
        self.save()
