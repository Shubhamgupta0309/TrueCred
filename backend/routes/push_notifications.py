"""
Push Notification Routes for TrueCred

This module provides API endpoints for managing push notification tokens
and sending push notifications.
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.push_token import PushToken
from services.push_notification_service import push_notification_service
from services.notification_service import NotificationService
from utils.api_response import success_response, error_response
import logging

logger = logging.getLogger(__name__)

# Create blueprint
push_bp = Blueprint('push', __name__, url_prefix='/api/push')

@push_bp.route('/register-token', methods=['POST'])
@jwt_required()
def register_push_token():
    """
    Register a push notification token for the current user

    Expected JSON payload:
    {
        "token": "fcm_registration_token",
        "device_type": "ios|android|web",
        "device_id": "unique_device_identifier"
    }
    """
    try:
        user_id = get_jwt_identity()
        data = request.get_json()

        if not data or 'token' not in data:
            return error_response('Token is required', 400)

        token = data['token']
        device_type = data.get('device_type', 'web')
        device_id = data.get('device_id')

        # Validate device type
        if device_type not in ['ios', 'android', 'web']:
            return error_response('Invalid device type. Must be ios, android, or web', 400)

        # Register the token
        push_token = PushToken.register_token(
            user_id=user_id,
            token=token,
            device_type=device_type,
            device_id=device_id
        )

        logger.info(f"Push token registered for user {user_id}, device {device_type}")

        return success_response(
            data={
                'token_id': str(push_token.id),
                'device_type': push_token.device_type,
                'registered_at': push_token.created_at.isoformat()
            },
            message='Push token registered successfully'
        )

    except Exception as e:
        logger.error(f"Error registering push token: {e}")
        return error_response('Failed to register push token', 500)

@push_bp.route('/unregister-token', methods=['POST'])
@jwt_required()
def unregister_push_token():
    """
    Unregister a push notification token

    Expected JSON payload:
    {
        "token": "fcm_registration_token"
    }
    """
    try:
        user_id = get_jwt_identity()
        data = request.get_json()

        if not data or 'token' not in data:
            return error_response('Token is required', 400)

        token = data['token']

        # Deactivate the token
        success = PushToken.deactivate_token(token)

        if success:
            logger.info(f"Push token unregistered for user {user_id}")
            return success_response(message='Push token unregistered successfully')
        else:
            return error_response('Token not found', 404)

    except Exception as e:
        logger.error(f"Error unregistering push token: {e}")
        return error_response('Failed to unregister push token', 500)

@push_bp.route('/tokens', methods=['GET'])
@jwt_required()
def get_push_tokens():
    """
    Get all active push tokens for the current user
    """
    try:
        user_id = get_jwt_identity()

        tokens = PushToken.get_active_tokens_for_user(user_id)
        token_data = [token.to_dict() for token in tokens]

        return success_response(
            data={
                'tokens': token_data,
                'count': len(token_data)
            }
        )

    except Exception as e:
        logger.error(f"Error retrieving push tokens: {e}")
        return error_response('Failed to retrieve push tokens', 500)

@push_bp.route('/test-notification', methods=['POST'])
@jwt_required()
def test_push_notification():
    """
    Send a test push notification to the current user's devices

    Expected JSON payload:
    {
        "title": "Test Notification",
        "body": "This is a test push notification"
    }
    """
    try:
        user_id = get_jwt_identity()
        data = request.get_json()

        title = data.get('title', 'Test Notification')
        body = data.get('body', 'This is a test push notification')

        # Get user's active tokens
        tokens = PushToken.get_active_tokens_for_user(user_id)

        if not tokens:
            return error_response('No active push tokens found for user', 404)

        # Send push notification to all user's devices
        token_strings = [token.token for token in tokens]

        result = push_notification_service.send_multicast_notification(
            tokens=token_strings,
            title=title,
            body=body,
            data={
                'type': 'test',
                'user_id': user_id
            }
        )

        return success_response(
            data=result,
            message='Test push notification sent'
        )

    except Exception as e:
        logger.error(f"Error sending test push notification: {e}")
        return error_response('Failed to send test push notification', 500)

@push_bp.route('/send-notification/<user_id>', methods=['POST'])
@jwt_required()
def send_push_notification_to_user(user_id):
    """
    Send a push notification to a specific user (admin only)

    Expected JSON payload:
    {
        "title": "Notification Title",
        "body": "Notification body",
        "data": {"key": "value"}
    }
    """
    try:
        # TODO: Add admin permission check here
        data = request.get_json()

        if not data or 'title' not in data or 'body' not in data:
            return error_response('Title and body are required', 400)

        title = data['title']
        body = data['body']
        notification_data = data.get('data', {})

        # Get user's active tokens
        tokens = PushToken.get_active_tokens_for_user(user_id)

        if not tokens:
            return error_response('No active push tokens found for user', 404)

        # Send push notification to all user's devices
        token_strings = [token.token for token in tokens]

        result = push_notification_service.send_multicast_notification(
            tokens=token_strings,
            title=title,
            body=body,
            data=notification_data
        )

        return success_response(
            data=result,
            message=f'Push notification sent to user {user_id}'
        )

    except Exception as e:
        logger.error(f"Error sending push notification to user: {e}")
        return error_response('Failed to send push notification', 500)

@push_bp.route('/cleanup-tokens', methods=['POST'])
@jwt_required()
def cleanup_push_tokens():
    """
    Clean up inactive push tokens (admin only)

    Expected JSON payload:
    {
        "days_old": 30
    }
    """
    try:
        # TODO: Add admin permission check here
        data = request.get_json()
        days_old = data.get('days_old', 30) if data else 30

        cleaned_count = PushToken.cleanup_inactive_tokens(days_old)

        return success_response(
            data={'cleaned_count': cleaned_count},
            message=f'Cleaned up {cleaned_count} inactive push tokens'
        )

    except Exception as e:
        logger.error(f"Error cleaning up push tokens: {e}")
        return error_response('Failed to cleanup push tokens', 500)

# Integration with notification service
def send_push_for_notification(user_id, notification_data):
    """
    Send push notification when a database notification is created

    Args:
        user_id: User ID to send push notification to
        notification_data: Notification data dictionary
    """
    try:
        # Get user's active tokens
        tokens = PushToken.get_active_tokens_for_user(user_id)

        if not tokens:
            logger.debug(f"No active push tokens found for user {user_id}")
            return

        # Send push notification to all user's devices
        token_strings = [token.token for token in tokens]

        result = push_notification_service.send_multicast_notification(
            tokens=token_strings,
            title=notification_data.get('title', 'TrueCred Notification'),
            body=notification_data.get('message', ''),
            data={
                'type': 'notification',
                'notification_id': notification_data.get('id'),
                'notification_type': notification_data.get('type'),
                'user_id': user_id
            }
        )

        if result['status'] == 'completed':
            logger.info(f"Push notification sent for notification {notification_data.get('id')} to {result['success_count']} devices")
        else:
            logger.warning(f"Failed to send push notification for notification {notification_data.get('id')}")

    except Exception as e:
        logger.error(f"Error sending push notification for notification: {e}")

# Register the push notification handler with the notification service
def register_push_notification_handler():
    """Register push notification handler with notification service"""
    # This will be called during app initialization
    pass