"""
Push Notification Service for TrueCred

This service handles push notifications for mobile devices using Firebase Cloud Messaging (FCM).
"""
import firebase_admin
from firebase_admin import credentials, messaging
import logging
from datetime import datetime
import os

logger = logging.getLogger(__name__)

class PushNotificationService:
    def __init__(self):
        self.initialized = False
        self._initialize_firebase()

    def _initialize_firebase(self):
        """Initialize Firebase Admin SDK"""
        try:
            # Check if Firebase is already initialized
            if not firebase_admin._apps:
                # Try to get credentials from environment or file
                cred_path = os.getenv('FIREBASE_CREDENTIALS_PATH')
                cred_json = os.getenv('FIREBASE_CREDENTIALS_JSON')

                if cred_json:
                    # Use JSON string from environment
                    import json
                    cred_dict = json.loads(cred_json)
                    cred = credentials.Certificate(cred_dict)
                elif cred_path and os.path.exists(cred_path):
                    # Use credentials file
                    cred = credentials.Certificate(cred_path)
                else:
                    logger.warning("Firebase credentials not found. Push notifications will be disabled.")
                    return

                # Initialize Firebase app
                firebase_admin.initialize_app(cred)
                self.initialized = True
                logger.info("Firebase Admin SDK initialized successfully")
            else:
                self.initialized = True
                logger.info("Firebase Admin SDK already initialized")

        except Exception as e:
            logger.error(f"Failed to initialize Firebase: {e}")
            self.initialized = False

    def send_push_notification(self, token, title, body, data=None, image_url=None):
        """
        Send a push notification to a single device

        Args:
            token: FCM registration token
            title: Notification title
            body: Notification body
            data: Additional data payload
            image_url: URL of image to display

        Returns:
            Dictionary with status and message ID
        """
        if not self.initialized:
            logger.warning("Firebase not initialized. Cannot send push notification.")
            return {
                'status': 'error',
                'error': 'Firebase not initialized',
                'timestamp': datetime.utcnow().isoformat()
            }

        try:
            # Create the message
            message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=body,
                    image=image_url
                ),
                data=data or {},
                token=token,
            )

            # Send the message
            response = messaging.send(message)

            logger.info(f"Push notification sent successfully: {response}")

            return {
                'status': 'sent',
                'message_id': response,
                'timestamp': datetime.utcnow().isoformat()
            }

        except messaging.UnregisteredError:
            logger.warning(f"Token is unregistered: {token}")
            return {
                'status': 'unregistered',
                'error': 'Device token is no longer registered',
                'timestamp': datetime.utcnow().isoformat()
            }

        except messaging.InvalidArgumentError as e:
            logger.error(f"Invalid argument in push notification: {e}")
            return {
                'status': 'error',
                'error': f'Invalid argument: {str(e)}',
                'timestamp': datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Error sending push notification: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }

    def send_multicast_notification(self, tokens, title, body, data=None, image_url=None):
        """
        Send a push notification to multiple devices

        Args:
            tokens: List of FCM registration tokens
            title: Notification title
            body: Notification body
            data: Additional data payload
            image_url: URL of image to display

        Returns:
            Dictionary with status and results
        """
        if not self.initialized:
            logger.warning("Firebase not initialized. Cannot send multicast push notification.")
            return {
                'status': 'error',
                'error': 'Firebase not initialized',
                'timestamp': datetime.utcnow().isoformat()
            }

        try:
            # Create the multicast message
            message = messaging.MulticastMessage(
                notification=messaging.Notification(
                    title=title,
                    body=body,
                    image=image_url
                ),
                data=data or {},
                tokens=tokens,
            )

            # Send the message
            response = messaging.send_multicast(message)

            logger.info(f"Multicast push notification sent. Success: {response.success_count}, Failure: {response.failure_count}")

            # Process responses
            results = []
            for i, resp in enumerate(response.responses):
                if resp.success:
                    results.append({
                        'token': tokens[i],
                        'status': 'sent',
                        'message_id': resp.message_id
                    })
                else:
                    results.append({
                        'token': tokens[i],
                        'status': 'failed',
                        'error': resp.exception.code if resp.exception else 'Unknown error'
                    })

            return {
                'status': 'completed',
                'success_count': response.success_count,
                'failure_count': response.failure_count,
                'results': results,
                'timestamp': datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Error sending multicast push notification: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }

    def send_topic_notification(self, topic, title, body, data=None, image_url=None):
        """
        Send a push notification to a topic

        Args:
            topic: FCM topic name
            title: Notification title
            body: Notification body
            data: Additional data payload
            image_url: URL of image to display

        Returns:
            Dictionary with status and message ID
        """
        if not self.initialized:
            logger.warning("Firebase not initialized. Cannot send topic push notification.")
            return {
                'status': 'error',
                'error': 'Firebase not initialized',
                'timestamp': datetime.utcnow().isoformat()
            }

        try:
            # Create the message
            message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=body,
                    image=image_url
                ),
                data=data or {},
                topic=topic,
            )

            # Send the message
            response = messaging.send(message)

            logger.info(f"Topic push notification sent successfully: {response}")

            return {
                'status': 'sent',
                'message_id': response,
                'topic': topic,
                'timestamp': datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Error sending topic push notification: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }

    def subscribe_to_topic(self, tokens, topic):
        """
        Subscribe devices to a topic

        Args:
            tokens: List of FCM registration tokens
            topic: Topic name

        Returns:
            Dictionary with subscription results
        """
        if not self.initialized:
            return {
                'status': 'error',
                'error': 'Firebase not initialized',
                'timestamp': datetime.utcnow().isoformat()
            }

        try:
            response = messaging.subscribe_to_topic(tokens, topic)

            return {
                'status': 'completed',
                'success_count': response.success_count,
                'failure_count': response.failure_count,
                'errors': response.errors,
                'timestamp': datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Error subscribing to topic: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }

    def unsubscribe_from_topic(self, tokens, topic):
        """
        Unsubscribe devices from a topic

        Args:
            tokens: List of FCM registration tokens
            topic: Topic name

        Returns:
            Dictionary with unsubscription results
        """
        if not self.initialized:
            return {
                'status': 'error',
                'error': 'Firebase not initialized',
                'timestamp': datetime.utcnow().isoformat()
            }

        try:
            response = messaging.unsubscribe_from_topic(tokens, topic)

            return {
                'status': 'completed',
                'success_count': response.success_count,
                'failure_count': response.failure_count,
                'errors': response.errors,
                'timestamp': datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Error unsubscribing from topic: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }

# Global instance
push_notification_service = PushNotificationService()