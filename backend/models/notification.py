"""
Notification model for the TrueCred application.
"""
from mongoengine import Document, StringField, DateTimeField, DictField, ReferenceField
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class Notification(Document):
    """
    Model for storing user notifications.
    """
    user_id = StringField(required=True)
    type = StringField(required=True)  # e.g., 'credential_issued', 'verification_request'
    title = StringField(required=True)
    message = StringField(required=True)
    data = DictField()  # Additional data like request_id, credential_id
    created_at = DateTimeField(default=datetime.utcnow)
    read_at = DateTimeField()

    meta = {
        'collection': 'notifications',
        'indexes': [
            'user_id',
            'type',
            'created_at',
            '-created_at'  # Descending index for recent notifications
        ]
    }

    def to_json(self):
        """Convert notification to JSON-serializable dict."""
        return {
            'id': str(self.id),
            'user_id': self.user_id,
            'type': self.type,
            'title': self.title,
            'message': self.message,
            'data': self.data,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'read_at': self.read_at.isoformat() if self.read_at else None
        }

    @classmethod
    def create_notification(cls, user_id, notification_type, title, message, data=None):
        """
        Create and save a new notification.

        Args:
            user_id: ID of the user to notify
            notification_type: Type of notification
            title: Notification title
            message: Notification message
            data: Additional data

        Returns:
            Notification instance or None if failed
        """
        try:
            notification = cls(
                user_id=user_id,
                type=notification_type,
                title=title,
                message=message,
                data=data or {}
            )
            notification.save()
            logger.info(f"Created notification {notification.id} for user {user_id}")
            return notification
        except Exception as e:
            logger.error(f"Failed to create notification: {e}")
            return None