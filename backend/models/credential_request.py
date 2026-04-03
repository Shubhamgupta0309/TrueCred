from datetime import datetime
from mongoengine import Document, StringField, DateTimeField, ListField, DictField, ReferenceField, BooleanField, IntField


class CredentialRequest(Document):
    """Model representing a student's credential request."""
    user_id = StringField(required=True)
    title = StringField(required=True)
    issuer = StringField()  # Name of issuing org (optional)
    issuer_id = StringField()  # ID of issuing organization when known
    type = StringField(default='credential')
    metadata = DictField()
    attachments = ListField(DictField())  # list of {uri, filename, verified}
    status = StringField(default='pending')  # pending|issued|rejected
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    
    # Blockchain integration fields
    blockchain_tx_hash = StringField()  # Transaction hash from blockchain
    blockchain_credential_id = StringField()  # Credential ID from smart contract
    
    # OCR and automatic verification fields
    ocr_verified = BooleanField(default=False)  # Whether OCR verification was performed
    confidence_score = IntField(default=0)  # 0-100 confidence score from OCR
    matched_template_id = StringField()  # ID of matched template
    matched_template_name = StringField()  # Name of matched template
    verification_status = StringField()  # verified|pending_review|rejected|no_template
    ocr_extracted_data = DictField()  # Extracted key fields from OCR
    ocr_full_text = StringField()  # Full extracted text (optional, for debugging)
    ocr_decision_details = DictField()  # Matching breakdown and decision explanation
    manual_review_required = BooleanField(default=False)  # Flag for manual review

    meta = {
        'collection': 'credential_requests',
        'indexes': [
            {'fields': ['user_id']},
            {'fields': ['status']},
            {'fields': ['blockchain_tx_hash']},
            {'fields': ['blockchain_credential_id']},
            {'fields': ['verification_status']},
            {'fields': ['ocr_verified']},
            {'fields': ['confidence_score']}
        ]
    }

    def save(self, *args, **kwargs):
        self.updated_at = datetime.utcnow()
        return super(CredentialRequest, self).save(*args, **kwargs)
