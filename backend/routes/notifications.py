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
        # Get pagination parameters
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 20)), 50)
        unread_only = request.args.get('unread_only', 'false').lower() == 'true'
        
        # Build query
        query = {'user_id': str(current_user_id)}
        if unread_only:
            query['read_at'] = None
        
        # Get total count
        total_count = Notification.objects(**query).count()
        total_pages = (total_count + per_page - 1) // per_page
        
        # Get notifications with pagination
        notifications = Notification.objects(**query).order_by('-created_at').skip((page - 1) * per_page).limit(per_page)
        
        # Convert to JSON
        notifications_data = []
        for notification in notifications:
            notifications_data.append(notification.to_json())
        
        return success_response(
            data={
                "notifications": notifications_data,
                "pagination": {
                    "total_count": total_count,
                    "total_pages": total_pages,
                    "current_page": page,
                    "per_page": per_page,
                    "has_next": page < total_pages,
                    "has_prev": page > 1
                }
            },
            message="Notifications retrieved successfully"
        )
    except Exception as e:
        logger.exception(f"Error getting notifications: {str(e)}")
        return error_response(
            message="Failed to retrieve notifications",
            status_code=500,
            error_code="notifications_fetch_error"
        )


@notifications_bp.route('/<notification_id>/read', methods=['POST'])
@jwt_required()
def mark_notification_read(notification_id):
    """
    Mark a notification as read.
    
    Path Parameters:
      notification_id: ID of the notification to mark as read
    
    Returns:
      Success message
    """
    current_user_id = get_jwt_identity()
    
    try:
        # Find notification
        notification = Notification.objects(id=notification_id, user_id=str(current_user_id)).first()
        if not notification:
            return error_response(message="Notification not found", status_code=404)
        
        # Mark as read
        from datetime import datetime
        notification.read_at = datetime.utcnow()
        notification.save()
        
        return success_response(message="Notification marked as read")
    except Exception as e:
        logger.exception(f"Error marking notification as read: {str(e)}")
        return error_response(message="Failed to mark notification as read", status_code=500)


@notifications_bp.route('/read-all', methods=['POST'])
@jwt_required()
def mark_all_notifications_read():
    """
    Mark all notifications as read for the current user.
    
    Returns:
      Success message with count of notifications marked as read
    """
    current_user_id = get_jwt_identity()
    
    try:
        from datetime import datetime
        
        # Update all unread notifications for this user
        updated_count = Notification.objects(
            user_id=str(current_user_id),
            read_at=None
        ).update(read_at=datetime.utcnow())
        
        return success_response(
            message=f"Marked {updated_count} notifications as read",
            data={"updated_count": updated_count}
        )
    except Exception as e:
        logger.exception(f"Error marking all notifications as read: {str(e)}")
        return error_response(message="Failed to mark notifications as read", status_code=500)


@notifications_bp.route('/unread-count', methods=['GET'])
@jwt_required()
def get_unread_count():
    """
    Get the count of unread notifications for the current user.
    
    Returns:
      Unread notification count
    """
    current_user_id = get_jwt_identity()
    
    try:
        # Count unread notifications
        unread_count = Notification.objects(
            user_id=str(current_user_id),
            read_at=None
        ).count()
        
        return success_response(
            data={"unread_count": unread_count},
            message="Unread count retrieved successfully"
        )
    except Exception as e:
        logger.exception(f"Error getting unread count: {str(e)}")
        return error_response(message="Failed to get unread count", status_code=500)
