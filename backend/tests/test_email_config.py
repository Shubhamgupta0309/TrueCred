"""
Email Configuration Test Script

This script tests the email configuration by attempting to send a test email.
It's useful for verifying that your SMTP settings are correct.

Usage:
    python test_email_config.py
"""
import sys
import os
import logging

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create Flask app context
from app import create_app
app = create_app('development')

def test_email_configuration():
    """Test the email configuration by sending a test email"""
    
    with app.app_context():
        from services.notification_service import NotificationService
        
        # Get recipient email from command line or use default
        recipient_email = input("Enter recipient email (or press Enter to use your configured email): ")
        if not recipient_email:
            from flask import current_app
            recipient_email = current_app.config.get('MAIL_USERNAME')
            logger.info(f"Using default email: {recipient_email}")
        
        # Prepare email content
        subject = "TrueCred: Email Configuration Test"
        message = """
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 5px;">
                <h2 style="color: #6047ff;">TrueCred Email Test</h2>
                <p>This is a test email to verify your email configuration for the TrueCred application.</p>
                <p>If you're receiving this email, it means your email configuration is working correctly! 🎉</p>
                <ul>
                    <li>SMTP Server: Working</li>
                    <li>Authentication: Working</li>
                    <li>Email Delivery: Working</li>
                </ul>
                <p>You can now proceed with using the email verification system.</p>
                <p>Best regards,<br>The TrueCred Team</p>
            </div>
        </body>
        </html>
        """
        
        logger.info(f"Sending test email to: {recipient_email}")
        
        # Send the test email
        notification_result = NotificationService.send_notification(
            to=recipient_email,
            subject=subject,
            message=message,
            notification_type='email',
            metadata={'html': True}
        )
        
        # Check the result
        if notification_result.get('status') == 'sent':
            logger.info("✅ Test email sent successfully!")
            logger.info(f"Notification ID: {notification_result.get('notification_id')}")
            logger.info("Your email configuration is working correctly.")
        else:
            logger.error("❌ Failed to send test email!")
            logger.error(f"Error: {notification_result.get('error')}")
            logger.error("Please check your email configuration in the .env file.")
            
            # Print current email configuration (without sensitive info)
            from flask import current_app
            logger.info("Current email configuration:")
            logger.info(f"MAIL_SERVER: {current_app.config.get('MAIL_SERVER')}")
            logger.info(f"MAIL_PORT: {current_app.config.get('MAIL_PORT')}")
            logger.info(f"MAIL_USE_TLS: {current_app.config.get('MAIL_USE_TLS')}")
            logger.info(f"MAIL_USE_SSL: {current_app.config.get('MAIL_USE_SSL')}")
            logger.info(f"MAIL_USERNAME: {current_app.config.get('MAIL_USERNAME')}")
            logger.info(f"MAIL_DEFAULT_SENDER: {current_app.config.get('MAIL_DEFAULT_SENDER')}")

if __name__ == "__main__":
    logger.info("Starting email configuration test")
    test_email_configuration()
    logger.info("Email configuration test completed")
