import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Bell, Check, CheckCheck, Trash2, Filter } from 'lucide-react';
import { useAuth } from '../context/AuthContext.jsx';
import { api } from '../services/api';
import websocketService from '../services/websocket';

const Notifications = () => {
  const { user } = useAuth();
  const [notifications, setNotifications] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [unreadCount, setUnreadCount] = useState(0);
  const [filter, setFilter] = useState('all'); // all, unread, read
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  // Fetch notifications
  const fetchNotifications = async (page = 1) => {
    setIsLoading(true);
    try {
      const params = { page, per_page: 20 };
      if (filter === 'unread') params.unread_only = 'true';

      const resp = await api.get('/api/notifications/', { params });
      const data = resp.data.data;

      setNotifications(data.notifications || []);
      setTotalPages(data.pagination?.total_pages || 1);
      setCurrentPage(page);
    } catch (err) {
      setError('Failed to fetch notifications');
      console.error('Fetch error:', err);
    }
    setIsLoading(false);
  };

  // Fetch unread count
  const fetchUnreadCount = async () => {
    try {
      const resp = await api.get('/api/notifications/unread-count');
      setUnreadCount(resp.data.data.unread_count || 0);
    } catch (err) {
      console.error('Unread count error:', err);
    }
  };

  // Mark notification as read
  const markAsRead = async (notificationId) => {
    try {
      await api.post(`/api/notifications/${notificationId}/read`);
      // Update local state
      setNotifications(prev =>
        prev.map(n =>
          n.id === notificationId
            ? { ...n, read_at: new Date().toISOString() }
            : n
        )
      );
      fetchUnreadCount(); // Refresh unread count
    } catch (err) {
      console.error('Mark as read error:', err);
    }
  };

  // Mark all as read
  const markAllAsRead = async () => {
    try {
      await api.post('/api/notifications/read-all');
      // Update local state
      setNotifications(prev =>
        prev.map(n => ({ ...n, read_at: new Date().toISOString() }))
      );
      setUnreadCount(0);
    } catch (err) {
      console.error('Mark all as read error:', err);
    }
  };

  // Format date
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInHours = (now - date) / (1000 * 60 * 60);

    if (diffInHours < 1) {
      return 'Just now';
    } else if (diffInHours < 24) {
      return `${Math.floor(diffInHours)}h ago`;
    } else {
      return date.toLocaleDateString();
    }
  };

  // Get notification icon based on type
  const getNotificationIcon = (type) => {
    switch (type) {
      case 'credential_issued':
        return '🎓';
      case 'credential_request':
        return '📝';
      case 'experience_verified':
        return '✅';
      case 'experience_rejected':
        return '❌';
      default:
        return '🔔';
    }
  };

  // Effect to fetch notifications on mount and filter change
  useEffect(() => {
    fetchNotifications(1);
  }, [filter]);

  // Effect to fetch unread count
  useEffect(() => {
    fetchUnreadCount();
    // Set up polling for real-time updates
    const interval = setInterval(fetchUnreadCount, 30000); // Every 30 seconds
    return () => clearInterval(interval);
  }, []);

  // WebSocket event listeners for real-time notifications
  useEffect(() => {
    const handleRealTimeNotification = (notificationData) => {
      console.log('Real-time notification received:', notificationData);

      // Add new notification to the top of the list
      setNotifications(prev => [notificationData, ...prev]);

      // Update unread count
      setUnreadCount(prev => prev + 1);

      // Show a toast or notification banner (you can implement this)
      showNotificationToast(notificationData);
    };

    const handleWebSocketConnected = () => {
      console.log('WebSocket connected for notifications');
    };

    const handleWebSocketDisconnected = () => {
      console.log('WebSocket disconnected');
    };

    // Register WebSocket event listeners
    websocketService.on('notification', handleRealTimeNotification);
    websocketService.on('connected', handleWebSocketConnected);
    websocketService.on('disconnected', handleWebSocketDisconnected);

    // Cleanup function
    return () => {
      websocketService.off('notification', handleRealTimeNotification);
      websocketService.off('connected', handleWebSocketConnected);
      websocketService.off('disconnected', handleWebSocketDisconnected);
    };
  }, []);

  // Function to show notification toast
  const showNotificationToast = (notificationData) => {
    // Create a simple toast notification
    const toast = document.createElement('div');
    toast.className = 'fixed top-4 right-4 bg-blue-600 text-white px-4 py-2 rounded-lg shadow-lg z-50 max-w-sm';
    toast.innerHTML = `
      <div class="flex items-start gap-2">
        <div class="text-lg">🔔</div>
        <div class="flex-1">
          <div class="font-semibold text-sm">${notificationData.title}</div>
          <div class="text-xs opacity-90">${notificationData.message}</div>
        </div>
      </div>
    `;

    document.body.appendChild(toast);

    // Auto remove after 5 seconds
    setTimeout(() => {
      if (toast.parentNode) {
        toast.remove();
      }
    }, 5000);

    // Add click to dismiss
    toast.addEventListener('click', () => {
      if (toast.parentNode) {
        toast.remove();
      }
    });
  };

  return (
    <div className="max-w-4xl mx-auto p-6 bg-white min-h-screen">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-6"
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="relative">
              <Bell className="w-8 h-8 text-purple-600" />
              {unreadCount > 0 && (
                <span className="absolute -top-2 -right-2 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
                  {unreadCount > 99 ? '99+' : unreadCount}
                </span>
              )}
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-800">Notifications</h1>
              <p className="text-gray-600 text-sm">
                {unreadCount > 0 ? `${unreadCount} unread` : 'All caught up!'}
              </p>
            </div>
          </div>

          {unreadCount > 0 && (
            <button
              onClick={markAllAsRead}
              className="flex items-center gap-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
            >
              <CheckCheck className="w-4 h-4" />
              Mark All Read
            </button>
          )}
        </div>
      </motion.div>

      {/* Filters */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="mb-6"
      >
        <div className="flex items-center gap-4">
          <Filter className="w-5 h-5 text-gray-500" />
          <div className="flex gap-2">
            {[
              { id: 'all', label: 'All' },
              { id: 'unread', label: 'Unread' },
              { id: 'read', label: 'Read' }
            ].map((option) => (
              <button
                key={option.id}
                onClick={() => setFilter(option.id)}
                className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                  filter === option.id
                    ? 'bg-purple-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {option.label}
              </button>
            ))}
          </div>
        </div>
      </motion.div>

      {/* Error Message */}
      {error && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg"
        >
          <p className="text-red-700">{error}</p>
        </motion.div>
      )}

      {/* Notifications List */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.2 }}
        className="space-y-3"
      >
        {isLoading ? (
          <div className="text-center py-12">
            <div className="w-8 h-8 border-4 border-purple-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
            <p className="text-gray-600">Loading notifications...</p>
          </div>
        ) : notifications.length === 0 ? (
          <div className="text-center py-12">
            <Bell className="w-12 h-12 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-600 mb-2">
              {filter === 'unread' ? 'No unread notifications' : 'No notifications yet'}
            </h3>
            <p className="text-gray-500">
              {filter === 'unread'
                ? 'You\'ve read all your notifications!'
                : 'Notifications about your credentials and experiences will appear here.'
              }
            </p>
          </div>
        ) : (
          <>
            {notifications.map((notification, index) => (
              <motion.div
                key={notification.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.05 }}
                className={`p-4 rounded-lg border transition-all hover:shadow-md ${
                  !notification.read_at
                    ? 'bg-blue-50 border-blue-200'
                    : 'bg-white border-gray-200'
                }`}
              >
                <div className="flex items-start gap-4">
                  <div className="text-2xl">
                    {getNotificationIcon(notification.type)}
                  </div>

                  <div className="flex-1">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <h3 className="font-semibold text-gray-800 mb-1">
                          {notification.title}
                        </h3>
                        <p className="text-gray-700 text-sm mb-2">
                          {notification.message}
                        </p>
                        <p className="text-xs text-gray-500">
                          {formatDate(notification.created_at)}
                        </p>
                      </div>

                      {!notification.read_at && (
                        <button
                          onClick={() => markAsRead(notification.id)}
                          className="ml-4 p-2 text-blue-600 hover:bg-blue-100 rounded-full transition-colors"
                          title="Mark as read"
                        >
                          <Check className="w-4 h-4" />
                        </button>
                      )}
                    </div>

                    {/* Additional data if available */}
                    {notification.data && Object.keys(notification.data).length > 0 && (
                      <div className="mt-3 pt-3 border-t border-gray-100">
                        <div className="text-xs text-gray-500 space-y-1">
                          {Object.entries(notification.data).map(([key, value]) => (
                            <div key={key} className="flex justify-between">
                              <span className="capitalize">{key.replace('_', ' ')}:</span>
                              <span className="font-mono">{String(value).substring(0, 20)}{String(value).length > 20 ? '...' : ''}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </motion.div>
            ))}

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="flex items-center justify-center gap-2 mt-8">
                <button
                  onClick={() => fetchNotifications(currentPage - 1)}
                  disabled={currentPage === 1}
                  className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Previous
                </button>

                <span className="text-sm text-gray-600">
                  Page {currentPage} of {totalPages}
                </span>

                <button
                  onClick={() => fetchNotifications(currentPage + 1)}
                  disabled={currentPage === totalPages}
                  className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Next
                </button>
              </div>
            )}
          </>
        )}
      </motion.div>
    </div>
  );
};

export default Notifications;
