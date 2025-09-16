from datetime import datetime
from mongoengine import Document, StringField, DateTimeField, ListField, DictField, ReferenceField, BooleanField


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

    meta = {
        'collection': 'credential_requests',
        'indexes': [
            {'fields': ['user_id']},
            {'fields': ['status']}
        ]
    }

    def save(self, *args, **kwargs):
        self.updated_at = datetime.utcnow()
        return super(CredentialRequest, self).save(*args, **kwargs)
