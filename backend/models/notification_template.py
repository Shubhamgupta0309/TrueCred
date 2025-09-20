from mongoengine import Document, StringField, ListField, BooleanField, DateTimeField, ReferenceField
from datetime import datetime
from models.user import User

class NotificationTemplate(Document):
    """Model for storing notification templates"""

    # Template metadata
    user_id = StringField(required=True)  # Reference to user who created the template
    name = StringField(required=True, max_length=100)
    type = StringField(required=True, max_length=50)  # e.g., 'credential_issued', 'verification_request'

    # Template content
    title_template = StringField(required=True, max_length=200)
    message_template = StringField(required=True, max_length=500)

    # Template configuration
    channels = ListField(StringField(choices=['websocket', 'push', 'email']), required=True)
    variables = ListField(StringField(max_length=50))  # Available variables for template
    is_active = BooleanField(default=True)

    # Timestamps
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)

    meta = {
        'collection': 'notification_templates',
        'indexes': [
            'user_id',
            'type',
            'is_active',
            ('user_id', 'type'),  # Compound index for user-specific templates
        ]
    }

    def save(self, *args, **kwargs):
        """Override save to update timestamp"""
        self.updated_at = datetime.utcnow()
        return super().save(*args, **kwargs)

    def to_dict(self):
        """Convert template to dictionary"""
        return {
            'id': str(self.id),
            'user_id': self.user_id,
            'name': self.name,
            'type': self.type,
            'title_template': self.title_template,
            'message_template': self.message_template,
            'channels': self.channels,
            'variables': self.variables,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }