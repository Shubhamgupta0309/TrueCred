import { initializeApp } from 'firebase/app';
import { getMessaging, getToken, onMessage, isSupported } from 'firebase/messaging';

// Firebase configuration
const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
  storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID,
  appId: import.meta.env.VITE_FIREBASE_APP_ID,
};

class PushNotificationService {
  constructor() {
    this.app = null;
    this.messaging = null;
    this.isSupported = false;
    this.token = null;
    this.initialized = false;
  }

  async initialize() {
    if (this.initialized) return;

    try {
      // Check if push notifications are supported
      this.isSupported = await isSupported();

      if (!this.isSupported) {
        console.log('Push notifications are not supported in this browser');
        return false;
      }

      // Initialize Firebase
      this.app = initializeApp(firebaseConfig);
      this.messaging = getMessaging(this.app);

      // Set up message handler
      onMessage(this.messaging, (payload) => {
        console.log('Received foreground message:', payload);
        this.handleForegroundMessage(payload);
      });

      this.initialized = true;
      console.log('Push notification service initialized');
      return true;

    } catch (error) {
      console.error('Failed to initialize push notifications:', error);
      return false;
    }
  }

  async requestPermission() {
    if (!this.initialized) {
      const success = await this.initialize();
      if (!success) return null;
    }

    try {
      const permission = await Notification.requestPermission();

      if (permission === 'granted') {
        console.log('Notification permission granted');
        return true;
      } else {
        console.log('Notification permission denied');
        return false;
      }
    } catch (error) {
      console.error('Error requesting notification permission:', error);
      return false;
    }
  }

  async getToken(vapidKey) {
    if (!this.initialized) {
      const success = await this.initialize();
      if (!success) return null;
    }

    try {
      const currentToken = await getToken(this.messaging, {
        vapidKey: vapidKey || import.meta.env.VITE_FIREBASE_VAPID_KEY
      });

      if (currentToken) {
        console.log('Registration token available');
        this.token = currentToken;
        return currentToken;
      } else {
        console.log('No registration token available');
        return null;
      }
    } catch (error) {
      console.error('An error occurred while retrieving token:', error);
      return null;
    }
  }

  async registerTokenWithBackend(token, deviceType = 'web', deviceId = null) {
    try {
      const response = await fetch('/api/push/register-token', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('accessToken')}`
        },
        body: JSON.stringify({
          token,
          device_type: deviceType,
          device_id: deviceId || this.generateDeviceId()
        })
      });

      const result = await response.json();

      if (result.success) {
        console.log('Token registered with backend successfully');
        return true;
      } else {
        console.error('Failed to register token with backend:', result.message);
        return false;
      }
    } catch (error) {
      console.error('Error registering token with backend:', error);
      return false;
    }
  }

  async unregisterToken() {
    if (!this.token) return;

    try {
      const response = await fetch('/api/push/unregister-token', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('accessToken')}`
        },
        body: JSON.stringify({
          token: this.token
        })
      });

      const result = await response.json();

      if (result.success) {
        console.log('Token unregistered successfully');
        this.token = null;
        return true;
      } else {
        console.error('Failed to unregister token:', result.message);
        return false;
      }
    } catch (error) {
      console.error('Error unregistering token:', error);
      return false;
    }
  }

  handleForegroundMessage(payload) {
    // Handle foreground messages (when app is in focus)
    const { notification, data } = payload;

    if (notification) {
      // Show browser notification
      const options = {
        body: notification.body,
        icon: '/vite.svg', // You can customize this
        badge: '/vite.svg',
        data: data,
        requireInteraction: false,
        silent: false
      };

      const browserNotification = new Notification(notification.title, options);

      // Auto-close after 5 seconds
      setTimeout(() => {
        browserNotification.close();
      }, 5000);

      // Handle click
      browserNotification.onclick = () => {
        // Focus the window and navigate to relevant page
        window.focus();

        // You can add navigation logic here based on the notification data
        if (data && data.type === 'notification') {
          // Navigate to notifications page
          window.location.href = '/notifications';
        }

        browserNotification.close();
      };

      // Emit event for React components to handle
      window.dispatchEvent(new CustomEvent('pushNotification', {
        detail: {
          type: 'foreground',
          payload
        }
      }));
    }
  }

  generateDeviceId() {
    // Generate a unique device ID
    const timestamp = Date.now().toString(36);
    const random = Math.random().toString(36).substr(2, 9);
    return `${timestamp}-${random}`;
  }

  async setupPushNotifications() {
    try {
      // Request permission
      const permissionGranted = await this.requestPermission();
      if (!permissionGranted) return false;

      // Get token
      const token = await this.getToken();
      if (!token) return false;

      // Register with backend
      const registered = await this.registerTokenWithBackend(token);
      if (!registered) return false;

      console.log('Push notifications setup completed successfully');
      return true;

    } catch (error) {
      console.error('Error setting up push notifications:', error);
      return false;
    }
  }

  async cleanup() {
    await this.unregisterToken();
    this.initialized = false;
    this.token = null;
  }

  getStatus() {
    return {
      isSupported: this.isSupported,
      initialized: this.initialized,
      hasToken: !!this.token,
      permission: Notification.permission
    };
  }
}

// Create singleton instance
const pushNotificationService = new PushNotificationService();

export default pushNotificationService;