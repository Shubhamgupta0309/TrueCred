"""
Notification service for the TrueCred application.

This service provides functionality to send notifications to users,
organizations, and external systems.
"""
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
from flask import current_app

# Set up logging
logger = logging.getLogger(__name__)

class NotificationService:
    """
    Service for sending notifications in the TrueCred system.
    
    This class handles email notifications and other types of notifications.
    """
    
    @staticmethod
    def send_notification(to, subject, message, notification_type='email', metadata=None):
        """
        Send a notification to a recipient.
        
        Args:
            to: Recipient of the notification (email, user ID, etc.)
            subject: Subject of the notification
            message: Content of the notification
            notification_type: Type of notification (email, push, sms, etc.)
            metadata: Additional metadata for the notification
            
        Returns:
            Dictionary with status and notification ID
        """
        if notification_type == 'email':
            return NotificationService.send_email(to, subject, message, metadata)
        else:
            # For non-email notifications, just log for now
            logger.info(f"NOTIFICATION [{notification_type}] To: {to}, Subject: {subject}")
            logger.info(f"Message: {message}")
        
        # Mock a successful notification
        notification_id = f"notif_{datetime.utcnow().timestamp()}"
        
        # Record the notification in the database
        # In a real implementation, we would store this in a notifications collection
        
        return {
            'status': 'sent',
            'notification_id': notification_id,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    @staticmethod
    def send_email(to, subject, message, metadata=None):
        """
        Send an email notification.
        
        Args:
            to: Email recipient
            subject: Email subject
            message: Email body
            metadata: Additional metadata for the email
            
        Returns:
            Dictionary with status and notification ID
        """
        try:
            is_html = metadata and metadata.get('html', False)
            
            # Try to get email configuration from the app config
            mail_server = current_app.config.get('MAIL_SERVER')
            mail_port = current_app.config.get('MAIL_PORT')
            mail_username = current_app.config.get('MAIL_USERNAME')
            mail_password = current_app.config.get('MAIL_PASSWORD')
            mail_use_tls = current_app.config.get('MAIL_USE_TLS')
            default_sender = current_app.config.get('MAIL_DEFAULT_SENDER')
            
            # If mail settings are not configured, log the email instead
            if not all([mail_server, mail_port, mail_username, mail_password]):
                logger.warning("Email settings not configured. Email not sent. Would send:")
                logger.info(f"To: {to}, Subject: {subject}")
                logger.info(f"Message: {message}")
                
                # Generate a notification ID for tracking
                notification_id = f"email_{datetime.utcnow().timestamp()}"
                
                return {
                    'status': 'logged',
                    'notification_id': notification_id,
                    'timestamp': datetime.utcnow().isoformat()
                }
            
            # Create message container
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = default_sender
            msg['To'] = to
            
            # Attach parts
            if is_html:
                # Create both plain text and HTML versions
                text_part = MIMEText(NotificationService._html_to_text(message), 'plain')
                html_part = MIMEText(message, 'html')
                msg.attach(text_part)
                msg.attach(html_part)
            else:
                # Plain text only
                msg.attach(MIMEText(message, 'plain'))
            
            # Send the message
            with smtplib.SMTP(mail_server, mail_port) as server:
                if mail_use_tls:
                    server.starttls()
                server.login(mail_username, mail_password)
                server.send_message(msg)
            
            logger.info(f"Email sent successfully to {to}")
            notification_id = f"email_{datetime.utcnow().timestamp()}"
            
            return {
                'status': 'sent',
                'notification_id': notification_id,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error sending email: {str(e)}")
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    @staticmethod
    def _html_to_text(html):
        """
        Convert HTML to plain text.
        
        Args:
            html: HTML content
            
        Returns:
            Plain text version
        """
        # This is a very simple HTML to text conversion
        # For a real app, you might want to use a library like html2text
        import re
        text = re.sub('<.*?>', ' ', html)
        text = re.sub(' +', ' ', text)
        return text.strip()
    
    @staticmethod
    def send_verification_request_notification(to, user, item_type, item_title):
        """
        Send a notification for a verification request.
        
        Args:
            to: Recipient of the notification (organization or issuer)
            user: User who is requesting verification
            item_type: Type of item being verified (experience or credential)
            item_title: Title of the item being verified
            
        Returns:
            Dictionary with status and notification ID
        """
        subject = f"Verification Request: {item_type.capitalize()}"
        message = f"User {user.name} has requested verification of their {item_type}: {item_title}"
        
        return NotificationService.send_notification(to, subject, message)
    
    @staticmethod
    def send_verification_result_notification(user, item_type, item_title, result, reason=None):
        """
        Send a notification for a verification result.
        
        Args:
            user: User to notify
            item_type: Type of item being verified (experience or credential)
            item_title: Title of the item being verified
            result: Result of the verification (approved or rejected)
            reason: Reason for rejection if applicable
            
        Returns:
            Dictionary with status and notification ID
        """
        if result == 'approved':
            subject = f"{item_type.capitalize()} Verified"
            message = f"Your {item_type} '{item_title}' has been verified."
        else:
            subject = f"{item_type.capitalize()} Verification Rejected"
            message = f"Your {item_type} '{item_title}' verification was rejected."
            if reason:
                message += f" Reason: {reason}"
        
        return NotificationService.send_notification(user.email, subject, message)

# Alias for the static method for convenience
send_notification = NotificationService.send_notification
