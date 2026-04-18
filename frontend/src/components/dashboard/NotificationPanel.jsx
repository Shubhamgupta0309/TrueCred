import React from 'react';
import { motion } from 'framer-motion';
import { Bell, AlertTriangle, CheckCircle, Clock } from 'lucide-react';

export default function NotificationPanel({ notifications }) {
  // Helper function to format dates
  const formatTime = (dateString) => {
    if (!dateString) return 'Recently';
    try {
      const date = new Date(dateString);
      const now = new Date();
      const diffMs = now - date;
      const diffSecs = Math.floor(diffMs / 1000);
      const diffMins = Math.floor(diffSecs / 60);
      const diffHours = Math.floor(diffMins / 60);
      
      if (diffSecs < 60) return 'Just now';
      if (diffMins < 60) return `${diffMins}m ago`;
      if (diffHours < 24) return `${diffHours}h ago`;
      
      return date.toLocaleDateString('en-US', { 
        month: 'short', 
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch (e) {
      return dateString;
    }
  };

  // Get icon based on notification type
  const getNotificationIcon = (type) => {
    switch (type) {
      case 'credential_issued':
      case 'credential_approved':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'credential_rejected':
        return <AlertTriangle className="w-5 h-5 text-red-500" />;
      case 'credential_review':
        return <Clock className="w-5 h-5 text-yellow-500" />;
      default:
        return <Bell className="w-5 h-5 text-cyan-500" />;
    }
  };

  // Get background color based on notification type
  const getNotificationBg = (type) => {
    switch (type) {
      case 'credential_issued':
      case 'credential_approved':
        return 'bg-green-900/20 border-green-500/30';
      case 'credential_rejected':
        return 'bg-red-900/20 border-red-500/30';
      case 'credential_review':
        return 'bg-yellow-900/20 border-yellow-500/30';
      default:
        return 'bg-cyan-900/20 border-cyan-500/30';
    }
  };

  return (
    <div className="bg-cyan-950/30 border border-cyan-500/30 rounded-2xl shadow-lg shadow-cyan-500/10 p-4">
      <h3 className="text-lg font-bold text-cyan-100 mb-4 flex items-center gap-2">
        <Bell className="w-5 h-5 text-cyan-400" />
        Notifications
      </h3>
      <div className="space-y-3 max-h-96 overflow-y-auto pr-2">
        {notifications && notifications.length > 0 ? (
          notifications.slice().reverse().map((notif, index) => {
            const notificationType = notif.notification_type || notif.type || 'info';
            const notifTitle = notif.title || notif.message || 'New notification';
            const notifMessage = notif.message || '';
            const notifTime = notif.created_at || notif.time;
            
            return (
              <motion.div
                key={notif.id || notif._id || `notification-${index}`}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3, delay: index * 0.05 }}
                className={`flex items-start gap-3 p-3 rounded-lg border ${getNotificationBg(notificationType)}`}
              >
                <div className="flex-shrink-0 mt-0.5">
                  {getNotificationIcon(notificationType)}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="font-medium text-sm text-cyan-100 truncate">{notifTitle}</p>
                  {notifMessage && (
                    <p className="text-xs text-cyan-300 mt-1 line-clamp-2">{notifMessage}</p>
                  )}
                  <p className="text-xs text-cyan-400/70 mt-1">
                    {formatTime(notifTime)}
                  </p>
                </div>
              </motion.div>
            );
          })
        ) : (
          <div className="text-center py-8">
            <Bell className="w-8 h-8 text-cyan-500/40 mx-auto mb-2" />
            <p className="text-cyan-300/70 text-sm">No notifications yet</p>
            <p className="text-cyan-300/50 text-xs mt-1">Notifications will appear when credentials are approved or OCR verified</p>
          </div>
        )}
      </div>
    </div>
  );
}