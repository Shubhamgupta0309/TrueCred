"""
Push Token Model for TrueCred

This model stores FCM registration tokens for push notifications.
"""
from mongoengine import Document, StringField, DateTimeField, BooleanField, ReferenceField
from datetime import datetime
import mongoengine as me

class PushToken(Document):
    """
    Model for storing push notification tokens
    """
    user_id = StringField(required=True)
    token = StringField(required=True, unique=True)
    device_type = StringField(choices=['ios', 'android', 'web'], default='web')
    device_id = StringField()  # Unique device identifier
    is_active = BooleanField(default=True)
    last_used = DateTimeField(default=datetime.utcnow)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)

    meta = {
        'collection': 'push_tokens',
        'indexes': [
            'user_id',
            'token',
            ('user_id', 'device_id'),  # Compound index for user-device combinations
            '-last_used',  # Index for cleanup queries
        ]
    }

    @classmethod
    def register_token(cls, user_id, token, device_type='web', device_id=None):
        """
        Register or update a push token for a user

        Args:
            user_id: User ID
            token: FCM registration token
            device_type: Type of device (ios, android, web)
            device_id: Unique device identifier

        Returns:
            PushToken instance
        """
        # Try to find existing token
        existing_token = cls.objects(token=token).first()

        if existing_token:
            # Update existing token
            existing_token.user_id = user_id
            existing_token.device_type = device_type
            existing_token.device_id = device_id
            existing_token.is_active = True
            existing_token.last_used = datetime.utcnow()
            existing_token.updated_at = datetime.utcnow()
            existing_token.save()
            return existing_token
        else:
            # Create new token
            return cls(
                user_id=user_id,
                token=token,
                device_type=device_type,
                device_id=device_id,
                is_active=True,
                last_used=datetime.utcnow(),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            ).save()

    @classmethod
    def deactivate_token(cls, token):
        """
        Deactivate a push token (when user logs out or token becomes invalid)

        Args:
            token: FCM registration token

        Returns:
            Boolean indicating success
        """
        token_obj = cls.objects(token=token).first()
        if token_obj:
            token_obj.is_active = False
            token_obj.updated_at = datetime.utcnow()
            token_obj.save()
            return True
        return False

    @classmethod
    def get_active_tokens_for_user(cls, user_id):
        """
        Get all active push tokens for a user

        Args:
            user_id: User ID

        Returns:
            List of active PushToken instances
        """
        return cls.objects(user_id=user_id, is_active=True).all()

    @classmethod
    def cleanup_inactive_tokens(cls, days_old=30):
        """
        Clean up inactive tokens older than specified days

        Args:
            days_old: Number of days after which to clean up inactive tokens

        Returns:
            Number of tokens cleaned up
        """
        from datetime import timedelta

        cutoff_date = datetime.utcnow() - timedelta(days=days_old)
        result = cls.objects(
            is_active=False,
            updated_at__lt=cutoff_date
        ).delete()

        return result

    def to_dict(self):
        """
        Convert token to dictionary representation
        """
        return {
            'id': str(self.id),
            'user_id': self.user_id,
            'device_type': self.device_type,
            'device_id': self.device_id,
            'is_active': self.is_active,
            'last_used': self.last_used.isoformat() if self.last_used else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }