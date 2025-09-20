from flask import Blueprint, request, jsonify
from models.notification_template import NotificationTemplate
from models.user import User
from services.auth_service import require_auth
from utils.api_response import ApiResponse
from mongoengine import Q
import json

notification_templates_bp = Blueprint('notification_templates', __name__)

# Default notification templates
DEFAULT_TEMPLATES = {
    'credential_issued': {
        'name': 'Credential Issued',
        'type': 'credential_issued',
        'title_template': 'New Credential Issued: {credential_title}',
        'message_template': 'Congratulations! Your credential "{credential_title}" has been successfully issued by {issuer_name}.',
        'channels': ['websocket', 'push', 'email'],
        'variables': ['credential_title', 'issuer_name', 'recipient_name']
    },
    'credential_verified': {
        'name': 'Credential Verified',
        'type': 'credential_verified',
        'title_template': 'Credential Verified: {credential_title}',
        'message_template': 'Your credential "{credential_title}" has been verified and is now active.',
        'channels': ['websocket', 'push', 'email'],
        'variables': ['credential_title', 'recipient_name']
    },
    'verification_request': {
        'name': 'Verification Request',
        'type': 'verification_request',
        'title_template': 'Verification Request from {requester_name}',
        'message_template': '{requester_name} has requested verification of their credential "{credential_title}". Please review and respond.',
        'channels': ['websocket', 'push', 'email'],
        'variables': ['requester_name', 'credential_title', 'recipient_name']
    },
    'experience_added': {
        'name': 'Experience Added',
        'type': 'experience_added',
        'title_template': 'New Experience Added',
        'message_template': '{user_name} has added a new experience: {position_title} at {company_name}.',
        'channels': ['websocket', 'push'],
        'variables': ['user_name', 'position_title', 'company_name']
    },
    'profile_updated': {
        'name': 'Profile Updated',
        'type': 'profile_updated',
        'title_template': 'Profile Updated',
        'message_template': '{user_name} has updated their profile information.',
        'channels': ['websocket'],
        'variables': ['user_name']
    },
    'system_maintenance': {
        'name': 'System Maintenance',
        'type': 'system_maintenance',
        'title_template': 'Scheduled Maintenance',
        'message_template': 'The system will be undergoing maintenance on {maintenance_date}. Expected downtime: {downtime_duration}.',
        'channels': ['websocket', 'push', 'email'],
        'variables': ['maintenance_date', 'downtime_duration']
    }
}

@notification_templates_bp.route('/api/notification-templates', methods=['GET'])
@require_auth
def get_notification_templates():
    """Get all notification templates for the authenticated user"""
    try:
        user_id = request.user_id

        # Get user's custom templates
        custom_templates = NotificationTemplate.objects(user_id=user_id)

        # Combine with default templates
        templates = []

        # Add default templates
        for template_key, template_data in DEFAULT_TEMPLATES.items():
            template = {
                'id': template_key,
                'is_default': True,
                'is_active': True,  # Default templates are always active
                **template_data
            }
            templates.append(template)

        # Add custom templates
        for custom_template in custom_templates:
            template = {
                'id': str(custom_template.id),
                'is_default': False,
                'is_active': custom_template.is_active,
                'name': custom_template.name,
                'type': custom_template.type,
                'title_template': custom_template.title_template,
                'message_template': custom_template.message_template,
                'channels': custom_template.channels,
                'variables': custom_template.variables,
                'created_at': custom_template.created_at.isoformat(),
                'updated_at': custom_template.updated_at.isoformat()
            }
            templates.append(template)

        return ApiResponse.success(templates, "Notification templates retrieved successfully")

    except Exception as e:
        return ApiResponse.error(f"Failed to retrieve notification templates: {str(e)}")

@notification_templates_bp.route('/api/notification-templates', methods=['POST'])
@require_auth
def create_notification_template():
    """Create a new custom notification template"""
    try:
        user_id = request.user_id
        data = request.get_json()

        required_fields = ['name', 'type', 'title_template', 'message_template', 'channels']
        for field in required_fields:
            if field not in data:
                return ApiResponse.error(f"Missing required field: {field}")

        # Validate channels
        valid_channels = ['websocket', 'push', 'email']
        for channel in data['channels']:
            if channel not in valid_channels:
                return ApiResponse.error(f"Invalid channel: {channel}")

        # Create new template
        template = NotificationTemplate(
            user_id=user_id,
            name=data['name'],
            type=data['type'],
            title_template=data['title_template'],
            message_template=data['message_template'],
            channels=data['channels'],
            variables=data.get('variables', []),
            is_active=data.get('is_active', True)
        )
        template.save()

        return ApiResponse.success({
            'id': str(template.id),
            'name': template.name,
            'type': template.type,
            'title_template': template.title_template,
            'message_template': template.message_template,
            'channels': template.channels,
            'variables': template.variables,
            'is_active': template.is_active,
            'created_at': template.created_at.isoformat()
        }, "Notification template created successfully")

    except Exception as e:
        return ApiResponse.error(f"Failed to create notification template: {str(e)}")

@notification_templates_bp.route('/api/notification-templates/<template_id>', methods=['PUT'])
@require_auth
def update_notification_template(template_id):
    """Update an existing notification template"""
    try:
        user_id = request.user_id
        data = request.get_json()

        # Find template
        template = NotificationTemplate.objects(id=template_id, user_id=user_id).first()
        if not template:
            return ApiResponse.error("Notification template not found")

        # Update fields
        if 'name' in data:
            template.name = data['name']
        if 'title_template' in data:
            template.title_template = data['title_template']
        if 'message_template' in data:
            template.message_template = data['message_template']
        if 'channels' in data:
            # Validate channels
            valid_channels = ['websocket', 'push', 'email']
            for channel in data['channels']:
                if channel not in valid_channels:
                    return ApiResponse.error(f"Invalid channel: {channel}")
            template.channels = data['channels']
        if 'variables' in data:
            template.variables = data['variables']
        if 'is_active' in data:
            template.is_active = data['is_active']

        template.save()

        return ApiResponse.success({
            'id': str(template.id),
            'name': template.name,
            'type': template.type,
            'title_template': template.title_template,
            'message_template': template.message_template,
            'channels': template.channels,
            'variables': template.variables,
            'is_active': template.is_active,
            'updated_at': template.updated_at.isoformat()
        }, "Notification template updated successfully")

    except Exception as e:
        return ApiResponse.error(f"Failed to update notification template: {str(e)}")

@notification_templates_bp.route('/api/notification-templates/<template_id>', methods=['DELETE'])
@require_auth
def delete_notification_template(template_id):
    """Delete a notification template"""
    try:
        user_id = request.user_id

        # Find and delete template
        template = NotificationTemplate.objects(id=template_id, user_id=user_id).first()
        if not template:
            return ApiResponse.error("Notification template not found")

        template.delete()

        return ApiResponse.success(None, "Notification template deleted successfully")

    except Exception as e:
        return ApiResponse.error(f"Failed to delete notification template: {str(e)}")

@notification_templates_bp.route('/api/notification-templates/<template_type>/render', methods=['POST'])
@require_auth
def render_notification_template(template_type):
    """Render a notification template with provided variables"""
    try:
        user_id = request.user_id
        data = request.get_json()

        variables = data.get('variables', {})

        # Find template
        template = None

        # Check custom templates first
        custom_template = NotificationTemplate.objects(
            user_id=user_id,
            type=template_type,
            is_active=True
        ).first()

        if custom_template:
            template = custom_template
        elif template_type in DEFAULT_TEMPLATES:
            # Use default template
            template_data = DEFAULT_TEMPLATES[template_type]
            template = type('Template', (), template_data)()

        if not template:
            return ApiResponse.error("Notification template not found")

        # Render templates
        title = template.title_template
        message = template.message_template

        for var_name, var_value in variables.items():
            title = title.replace(f'{{{var_name}}}', str(var_value))
            message = message.replace(f'{{{var_name}}}', str(var_value))

        return ApiResponse.success({
            'title': title,
            'message': message,
            'channels': template.channels,
            'template_type': template_type
        }, "Notification template rendered successfully")

    except Exception as e:
        return ApiResponse.error(f"Failed to render notification template: {str(e)}")

@notification_templates_bp.route('/api/notification-templates/types', methods=['GET'])
def get_template_types():
    """Get available notification template types"""
    try:
        types = []
        for template_key, template_data in DEFAULT_TEMPLATES.items():
            types.append({
                'type': template_key,
                'name': template_data['name'],
                'description': f"Template for {template_data['name'].lower()} notifications",
                'variables': template_data['variables']
            })

        return ApiResponse.success(types, "Template types retrieved successfully")

    except Exception as e:
        return ApiResponse.error(f"Failed to retrieve template types: {str(e)}")