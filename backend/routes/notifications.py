"""
Notifications routes for the TrueCred API.

This module defines the notifications endpoints for the TrueCred API.
"""
from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from utils.api_response import success_response, error_response
from models.user import User
from models.notification import Notification
import logging

# Set up logging
logger = logging.getLogger(__name__)

# Notifications blueprint
notifications_bp = Blueprint('notifications', __name__)

@notifications_bp.route('/')
@jwt_required()
def get_notifications():
    """
    Get notifications for the current user.
    
    Returns:
        JSON response with the user's notifications
    """
    # Get the current user ID from the JWT
    current_user_id = get_jwt_identity()
    
    try:
        # Ensure the user exists.
        user = User.objects(id=current_user_id).first()
        if not user:
            return error_response(
                message="User not found",
                status_code=404,
                error_code="user_not_found"
            )

        # Primary source: Notification model collection.
        notifications = []
        try:
            docs = Notification.objects(user_id=str(current_user_id)).order_by('-created_at').limit(50)
            notifications = [doc.to_json() for doc in docs]
        except Exception as e:
            logger.exception('Failed to fetch notifications via Notification model: %s', e)

        # Backward-compatible fallback for deployments that still use a raw pymongo collection.
        if not notifications:
            try:
                if hasattr(current_app, 'db') and current_app.db is not None:
                    cursor = current_app.db.notifications.find({'user_id': str(current_user_id)}).sort('created_at', -1).limit(50)
                    raw_docs = list(cursor)
                    for n in raw_docs:
                        n['_id'] = str(n.get('_id'))
                        if 'created_at' in n and hasattr(n['created_at'], 'isoformat'):
                            n['created_at'] = n['created_at'].isoformat()
                    notifications = raw_docs
            except Exception as e:
                logger.exception('Fallback pymongo notifications fetch failed: %s', e)

        return success_response(
            data={"notifications": notifications},
            message="Notifications retrieved successfully"
        )
    except Exception as e:
        logger.exception(f"Error getting notifications: {str(e)}")
        return error_response(
            message="Failed to retrieve notifications",
            status_code=500,
            error_code="notifications_fetch_error"
        )
