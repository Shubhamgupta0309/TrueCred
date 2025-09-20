from models.notification_template import NotificationTemplate
from models.user import User
from services.websocket_service import WebSocketService
from services.push_notification_service import PushNotificationService
from services.notification_service import NotificationService
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class NotificationTemplateService:
    """Service for managing notification templates and sending templated notifications"""

    # Default notification templates
    DEFAULT_TEMPLATES = {
        'credential_issued': {
            'name': 'Credential Issued',
            'title_template': 'New Credential Issued: {credential_title}',
            'message_template': 'Congratulations! Your credential "{credential_title}" has been successfully issued by {issuer_name}.',
            'channels': ['websocket', 'push', 'email'],
            'variables': ['credential_title', 'issuer_name', 'recipient_name']
        },
        'credential_verified': {
            'name': 'Credential Verified',
            'title_template': 'Credential Verified: {credential_title}',
            'message_template': 'Your credential "{credential_title}" has been verified and is now active.',
            'channels': ['websocket', 'push', 'email'],
            'variables': ['credential_title', 'recipient_name']
        },
        'verification_request': {
            'name': 'Verification Request',
            'title_template': 'Verification Request from {requester_name}',
            'message_template': '{requester_name} has requested verification of their credential "{credential_title}". Please review and respond.',
            'channels': ['websocket', 'push', 'email'],
            'variables': ['requester_name', 'credential_title', 'recipient_name']
        },
        'experience_added': {
            'name': 'Experience Added',
            'title_template': 'New Experience Added',
            'message_template': '{user_name} has added a new experience: {position_title} at {company_name}.',
            'channels': ['websocket', 'push'],
            'variables': ['user_name', 'position_title', 'company_name']
        },
        'profile_updated': {
            'name': 'Profile Updated',
            'title_template': 'Profile Updated',
            'message_template': '{user_name} has updated their profile information.',
            'channels': ['websocket'],
            'variables': ['user_name']
        },
        'system_maintenance': {
            'name': 'System Maintenance',
            'title_template': 'Scheduled Maintenance',
            'message_template': 'The system will be undergoing maintenance on {maintenance_date}. Expected downtime: {downtime_duration}.',
            'channels': ['websocket', 'push', 'email'],
            'variables': ['maintenance_date', 'downtime_duration']
        }
    }

    @staticmethod
    def get_template(user_id, template_type):
        """Get notification template for user (custom or default)"""
        try:
            # Try to find custom template first
            custom_template = NotificationTemplate.objects(
                user_id=user_id,
                type=template_type,
                is_active=True
            ).first()

            if custom_template:
                return {
                    'id': str(custom_template.id),
                    'name': custom_template.name,
                    'type': custom_template.type,
                    'title_template': custom_template.title_template,
                    'message_template': custom_template.message_template,
                    'channels': custom_template.channels,
                    'variables': custom_template.variables,
                    'is_default': False
                }

            # Fall back to default template
            if template_type in NotificationTemplateService.DEFAULT_TEMPLATES:
                default_template = NotificationTemplateService.DEFAULT_TEMPLATES[template_type]
                return {
                    'id': template_type,
                    'name': default_template['name'],
                    'type': template_type,
                    'title_template': default_template['title_template'],
                    'message_template': default_template['message_template'],
                    'channels': default_template['channels'],
                    'variables': default_template['variables'],
                    'is_default': True
                }

            return None

        except Exception as e:
            logger.error(f"Error getting template {template_type} for user {user_id}: {str(e)}")
            return None

    @staticmethod
    def render_template(template, variables):
        """Render a notification template with provided variables"""
        try:
            title = template['title_template']
            message = template['message_template']

            # Replace variables in templates
            for var_name, var_value in variables.items():
                placeholder = f'{{{var_name}}}'
                title = title.replace(placeholder, str(var_value))
                message = message.replace(placeholder, str(var_value))

            return {
                'title': title,
                'message': message,
                'channels': template['channels']
            }

        except Exception as e:
            logger.error(f"Error rendering template: {str(e)}")
            return None

    @staticmethod
    def send_templated_notification(user_id, template_type, variables, recipient_ids=None):
        """Send a notification using a template"""
        try:
            # Get template
            template = NotificationTemplateService.get_template(user_id, template_type)
            if not template:
                logger.error(f"Template {template_type} not found for user {user_id}")
                return False

            # Render template
            rendered = NotificationTemplateService.render_template(template, variables)
            if not rendered:
                logger.error(f"Failed to render template {template_type}")
                return False

            # Send notification through appropriate channels
            success = True

            # WebSocket notification
            if 'websocket' in template['channels']:
                try:
                    if recipient_ids:
                        for recipient_id in recipient_ids:
                            WebSocketService.send_notification_to_user(
                                recipient_id,
                                rendered['title'],
                                rendered['message'],
                                template_type
                            )
                    else:
                        WebSocketService.send_notification_to_user(
                            user_id,
                            rendered['title'],
                            rendered['message'],
                            template_type
                        )
                except Exception as e:
                    logger.error(f"Failed to send WebSocket notification: {str(e)}")
                    success = False

            # Push notification
            if 'push' in template['channels']:
                try:
                    if recipient_ids:
                        for recipient_id in recipient_ids:
                            PushNotificationService.send_push_notification(
                                recipient_id,
                                rendered['title'],
                                rendered['message'],
                                {'type': template_type}
                            )
                    else:
                        PushNotificationService.send_push_notification(
                            user_id,
                            rendered['title'],
                            rendered['message'],
                            {'type': template_type}
                        )
                except Exception as e:
                    logger.error(f"Failed to send push notification: {str(e)}")
                    success = False

            # Email notification (if implemented)
            if 'email' in template['channels']:
                try:
                    # TODO: Implement email service
                    logger.info(f"Email notification would be sent: {rendered['title']}")
                except Exception as e:
                    logger.error(f"Failed to send email notification: {str(e)}")
                    success = False

            # Store notification in database
            try:
                NotificationService.create_notification(
                    user_id=user_id,
                    title=rendered['title'],
                    message=rendered['message'],
                    type=template_type,
                    channels=template['channels']
                )
            except Exception as e:
                logger.error(f"Failed to store notification in database: {str(e)}")

            return success

        except Exception as e:
            logger.error(f"Error sending templated notification: {str(e)}")
            return False

    @staticmethod
    def create_custom_template(user_id, template_data):
        """Create a custom notification template"""
        try:
            template = NotificationTemplate(
                user_id=user_id,
                name=template_data['name'],
                type=template_data['type'],
                title_template=template_data['title_template'],
                message_template=template_data['message_template'],
                channels=template_data['channels'],
                variables=template_data.get('variables', []),
                is_active=template_data.get('is_active', True)
            )
            template.save()
            return template
        except Exception as e:
            logger.error(f"Error creating custom template: {str(e)}")
            return None

    @staticmethod
    def update_custom_template(user_id, template_id, template_data):
        """Update a custom notification template"""
        try:
            template = NotificationTemplate.objects(id=template_id, user_id=user_id).first()
            if not template:
                return None

            if 'name' in template_data:
                template.name = template_data['name']
            if 'title_template' in template_data:
                template.title_template = template_data['title_template']
            if 'message_template' in template_data:
                template.message_template = template_data['message_template']
            if 'channels' in template_data:
                template.channels = template_data['channels']
            if 'variables' in template_data:
                template.variables = template_data['variables']
            if 'is_active' in template_data:
                template.is_active = template_data['is_active']

            template.save()
            return template
        except Exception as e:
            logger.error(f"Error updating custom template: {str(e)}")
            return None

    @staticmethod
    def delete_custom_template(user_id, template_id):
        """Delete a custom notification template"""
        try:
            template = NotificationTemplate.objects(id=template_id, user_id=user_id).first()
            if template:
                template.delete()
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting custom template: {str(e)}")
            return False

    @staticmethod
    def get_user_templates(user_id):
        """Get all templates for a user (custom + default)"""
        try:
            templates = []

            # Add default templates
            for template_key, template_data in NotificationTemplateService.DEFAULT_TEMPLATES.items():
                template = {
                    'id': template_key,
                    'is_default': True,
                    'is_active': True,
                    **template_data
                }
                templates.append(template)

            # Add custom templates
            custom_templates = NotificationTemplate.objects(user_id=user_id)
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

            return templates

        except Exception as e:
            logger.error(f"Error getting user templates: {str(e)}")
            return []