"""
Notification Preferences Routes for TrueCred

This module provides API endpoints for managing user notification preferences.
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.notification_preferences import NotificationPreferences
from utils.api_response import success_response, error_response
import logging

logger = logging.getLogger(__name__)

# Create blueprint
notification_preferences_bp = Blueprint('notification_preferences', __name__, url_prefix='/api/notification-preferences')

@notification_preferences_bp.route('', methods=['GET'])
@jwt_required()
def get_notification_preferences():
    """
    Get notification preferences for the current user
    """
    try:
        user_id = get_jwt_identity()

        preferences = NotificationPreferences.get_or_create_for_user(user_id)

        return success_response(
            data=preferences.to_dict(),
            message='Notification preferences retrieved successfully'
        )

    except Exception as e:
        logger.error(f"Error retrieving notification preferences: {e}")
        return error_response('Failed to retrieve notification preferences', 500)

@notification_preferences_bp.route('', methods=['PUT'])
@jwt_required()
def update_notification_preferences():
    """
    Update notification preferences for the current user

    Expected JSON payload:
    {
        "email_enabled": true,
        "push_enabled": true,
        "quiet_hours_enabled": false,
        "quiet_hours_start": "22:00",
        "quiet_hours_end": "08:00",
        ...
    }
    """
    try:
        user_id = get_jwt_identity()
        data = request.get_json()

        if not data:
            return error_response('Request body is required', 400)

        preferences = NotificationPreferences.get_or_create_for_user(user_id)
        updated_preferences = preferences.update_preferences(data)

        logger.info(f"Notification preferences updated for user {user_id}")

        return success_response(
            data=updated_preferences.to_dict(),
            message='Notification preferences updated successfully'
        )

    except Exception as e:
        logger.error(f"Error updating notification preferences: {e}")
        return error_response('Failed to update notification preferences', 500)

@notification_preferences_bp.route('/reset', methods=['POST'])
@jwt_required()
def reset_notification_preferences():
    """
    Reset notification preferences to default values for the current user
    """
    try:
        user_id = get_jwt_identity()

        # Delete existing preferences to create fresh defaults
        NotificationPreferences.objects(user_id=user_id).delete()

        # Create new default preferences
        preferences = NotificationPreferences.get_or_create_for_user(user_id)

        logger.info(f"Notification preferences reset for user {user_id}")

        return success_response(
            data=preferences.to_dict(),
            message='Notification preferences reset to defaults successfully'
        )

    except Exception as e:
        logger.error(f"Error resetting notification preferences: {e}")
        return error_response('Failed to reset notification preferences', 500)

@notification_preferences_bp.route('/channels', methods=['GET'])
@jwt_required()
def get_available_channels():
    """
    Get available notification channels and their descriptions
    """
    channels = {
        'email': {
            'name': 'Email',
            'description': 'Receive notifications via email',
            'types': {
                'experience_verifications': 'Experience verification updates',
                'credential_issued': 'New credentials issued',
                'credential_requests': 'Credential verification requests',
                'system_updates': 'System and platform updates'
            }
        },
        'push': {
            'name': 'Push Notifications',
            'description': 'Receive push notifications on mobile devices',
            'types': {
                'experience_verifications': 'Experience verification updates',
                'credential_issued': 'New credentials issued',
                'credential_requests': 'Credential verification requests',
                'system_updates': 'System and platform updates'
            }
        },
        'websocket': {
            'name': 'Real-time Notifications',
            'description': 'Receive real-time notifications in the browser',
            'types': {
                'experience_verifications': 'Experience verification updates',
                'credential_issued': 'New credentials issued',
                'credential_requests': 'Credential verification requests',
                'system_updates': 'System and platform updates'
            }
        },
        'browser': {
            'name': 'Browser Notifications',
            'description': 'Receive browser notifications when app is open',
            'types': {
                'experience_verifications': 'Experience verification updates',
                'credential_issued': 'New credentials issued',
                'credential_requests': 'Credential verification requests',
                'system_updates': 'System and platform updates'
            }
        }
    }

    return success_response(
        data={'channels': channels},
        message='Available notification channels retrieved successfully'
    )

@notification_preferences_bp.route('/test/<channel>', methods=['POST'])
@jwt_required()
def test_notification_channel(channel):
    """
    Send a test notification via the specified channel

    Args:
        channel: Notification channel (email, push, websocket, browser)
    """
    try:
        user_id = get_jwt_identity()

        if channel not in ['email', 'push', 'websocket', 'browser']:
            return error_response('Invalid notification channel', 400)

        preferences = NotificationPreferences.get_or_create_for_user(user_id)

        # Check if channel is enabled
        if not getattr(preferences, f'{channel}_enabled', True):
            return error_response(f'{channel.capitalize()} notifications are disabled', 400)

        # Send test notification based on channel
        if channel == 'email':
            from services.notification_service import NotificationService
            result = NotificationService.create_db_notification(
                user_id=user_id,
                notification_type='system_updates',
                title='Test Email Notification',
                message='This is a test email notification to verify your email preferences.',
                data={'test': True, 'channel': 'email'}
            )
        elif channel == 'push':
            # Test push notification
            from routes.push_notifications import send_push_for_notification
            send_push_for_notification(user_id, {
                'id': 'test_push',
                'type': 'system_updates',
                'title': 'Test Push Notification',
                'message': 'This is a test push notification to verify your push preferences.',
                'data': {'test': True, 'channel': 'push'}
            })
            result = {'status': 'sent'}
        elif channel == 'websocket':
            # Test WebSocket notification
            from services.websocket_service import websocket_service
            websocket_service.emit_notification(user_id, {
                'id': 'test_websocket',
                'type': 'system_updates',
                'title': 'Test Real-time Notification',
                'message': 'This is a test real-time notification to verify your WebSocket preferences.',
                'data': {'test': True, 'channel': 'websocket'},
                'timestamp': '2024-01-01T00:00:00Z'
            })
            result = {'status': 'sent'}
        elif channel == 'browser':
            # For browser notifications, we'll send via WebSocket and handle in frontend
            from services.websocket_service import websocket_service
            websocket_service.emit_notification(user_id, {
                'id': 'test_browser',
                'type': 'system_updates',
                'title': 'Test Browser Notification',
                'message': 'This is a test browser notification to verify your browser preferences.',
                'data': {'test': True, 'channel': 'browser'},
                'timestamp': '2024-01-01T00:00:00Z'
            })
            result = {'status': 'sent'}

        logger.info(f"Test {channel} notification sent for user {user_id}")

        return success_response(
            data={'channel': channel, 'result': result},
            message=f'Test {channel} notification sent successfully'
        )

    except Exception as e:
        logger.error(f"Error sending test {channel} notification: {e}")
        return error_response(f'Failed to send test {channel} notification', 500)