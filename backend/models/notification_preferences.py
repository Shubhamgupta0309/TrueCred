"""
Notification Preferences Model for TrueCred

This model stores user preferences for different types of notifications.
"""
from mongoengine import Document, StringField, BooleanField, DateTimeField, DictField
from datetime import datetime
import mongoengine as me

class NotificationPreferences(Document):
    """
    Model for storing user notification preferences
    """
    user_id = StringField(required=True, unique=True)

    # Email preferences
    email_enabled = BooleanField(default=True)
    email_experience_verifications = BooleanField(default=True)
    email_credential_issued = BooleanField(default=True)
    email_credential_requests = BooleanField(default=True)
    email_system_updates = BooleanField(default=True)

    # Push notification preferences
    push_enabled = BooleanField(default=True)
    push_experience_verifications = BooleanField(default=True)
    push_credential_issued = BooleanField(default=True)
    push_credential_requests = BooleanField(default=True)
    push_system_updates = BooleanField(default=True)

    # WebSocket/real-time preferences
    websocket_enabled = BooleanField(default=True)
    websocket_experience_verifications = BooleanField(default=True)
    websocket_credential_issued = BooleanField(default=True)
    websocket_credential_requests = BooleanField(default=True)
    websocket_system_updates = BooleanField(default=True)

    # Browser notification preferences
    browser_enabled = BooleanField(default=True)
    browser_experience_verifications = BooleanField(default=True)
    browser_credential_issued = BooleanField(default=True)
    browser_credential_requests = BooleanField(default=True)
    browser_system_updates = BooleanField(default=True)

    # Quiet hours
    quiet_hours_enabled = BooleanField(default=False)
    quiet_hours_start = StringField(default="22:00")  # 24-hour format
    quiet_hours_end = StringField(default="08:00")

    # Additional preferences
    preferences = DictField(default=dict)  # For future extensibility

    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)

    meta = {
        'collection': 'notification_preferences',
        'indexes': [
            'user_id',
        ]
    }

    @classmethod
    def get_or_create_for_user(cls, user_id):
        """
        Get notification preferences for a user, creating default preferences if they don't exist

        Args:
            user_id: User ID

        Returns:
            NotificationPreferences instance
        """
        preferences = cls.objects(user_id=user_id).first()
        if not preferences:
            preferences = cls(user_id=user_id).save()
        return preferences

    def should_send_notification(self, notification_type, channel='email'):
        """
        Check if a notification should be sent based on user preferences

        Args:
            notification_type: Type of notification (experience_verifications, credential_issued, etc.)
            channel: Notification channel (email, push, websocket, browser)

        Returns:
            Boolean indicating if notification should be sent
        """
        # Check if channel is enabled
        channel_enabled = getattr(self, f'{channel}_enabled', True)
        if not channel_enabled:
            return False

        # Check if specific notification type is enabled for this channel
        type_enabled = getattr(self, f'{channel}_{notification_type}', True)
        if not type_enabled:
            return False

        # Check quiet hours
        if self.quiet_hours_enabled and channel in ['push', 'browser']:
            if self._is_quiet_hour():
                return False

        return True

    def _is_quiet_hour(self):
        """
        Check if current time is within quiet hours

        Returns:
            Boolean indicating if current time is quiet hour
        """
        try:
            from datetime import datetime
            now = datetime.now()
            current_time = now.strftime("%H:%M")

            start_time = self.quiet_hours_start
            end_time = self.quiet_hours_end

            if start_time <= end_time:
                # Same day range
                return start_time <= current_time <= end_time
            else:
                # Overnight range
                return current_time >= start_time or current_time <= end_time

        except Exception:
            # If there's any error parsing times, don't enforce quiet hours
            return False

    def update_preferences(self, updates):
        """
        Update notification preferences

        Args:
            updates: Dictionary of preference updates

        Returns:
            Updated NotificationPreferences instance
        """
        # List of allowed fields to update
        allowed_fields = [
            'email_enabled', 'email_experience_verifications', 'email_credential_issued',
            'email_credential_requests', 'email_system_updates',
            'push_enabled', 'push_experience_verifications', 'push_credential_issued',
            'push_credential_requests', 'push_system_updates',
            'websocket_enabled', 'websocket_experience_verifications', 'websocket_credential_issued',
            'websocket_credential_requests', 'websocket_system_updates',
            'browser_enabled', 'browser_experience_verifications', 'browser_credential_issued',
            'browser_credential_requests', 'browser_system_updates',
            'quiet_hours_enabled', 'quiet_hours_start', 'quiet_hours_end'
        ]

        for field, value in updates.items():
            if field in allowed_fields:
                setattr(self, field, value)

        self.updated_at = datetime.utcnow()
        self.save()
        return self

    def to_dict(self):
        """
        Convert preferences to dictionary representation
        """
        return {
            'user_id': self.user_id,
            'email_enabled': self.email_enabled,
            'email_experience_verifications': self.email_experience_verifications,
            'email_credential_issued': self.email_credential_issued,
            'email_credential_requests': self.email_credential_requests,
            'email_system_updates': self.email_system_updates,
            'push_enabled': self.push_enabled,
            'push_experience_verifications': self.push_experience_verifications,
            'push_credential_issued': self.push_credential_issued,
            'push_credential_requests': self.push_credential_requests,
            'push_system_updates': self.push_system_updates,
            'websocket_enabled': self.websocket_enabled,
            'websocket_experience_verifications': self.websocket_experience_verifications,
            'websocket_credential_issued': self.websocket_credential_issued,
            'websocket_credential_requests': self.websocket_credential_requests,
            'websocket_system_updates': self.websocket_system_updates,
            'browser_enabled': self.browser_enabled,
            'browser_experience_verifications': self.browser_experience_verifications,
            'browser_credential_issued': self.browser_credential_issued,
            'browser_credential_requests': self.browser_credential_requests,
            'browser_system_updates': self.browser_system_updates,
            'quiet_hours_enabled': self.quiet_hours_enabled,
            'quiet_hours_start': self.quiet_hours_start,
            'quiet_hours_end': self.quiet_hours_end,
            'preferences': self.preferences,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    @classmethod
    def get_notification_type_from_string(cls, notification_type_str):
        """
        Convert notification type string to internal type

        Args:
            notification_type_str: String representation of notification type

        Returns:
            Internal notification type string
        """
        type_mapping = {
            'experience_verified': 'experience_verifications',
            'experience_verification': 'experience_verifications',
            'experience_rejected': 'experience_verifications',
            'credential_issued': 'credential_issued',
            'credential_request': 'credential_requests',
            'system_update': 'system_updates',
            'system': 'system_updates'
        }

        return type_mapping.get(notification_type_str, notification_type_str)