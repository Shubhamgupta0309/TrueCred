import React from 'react';
import { motion } from 'framer-motion';
import { Bell, AlertTriangle } from 'lucide-react';

export default function NotificationPanel({ notifications }) {
  return (
    <div className="bg-cyan-950/30 border border-cyan-500/30 rounded-2xl shadow-lg shadow-cyan-500/10 p-4">
      <h3 className="text-lg font-bold text-cyan-100 mb-4 flex items-center gap-2">
        <Bell className="w-5 h-5 text-cyan-400" />
        Notifications
      </h3>
  <div className="space-y-3 max-h-48 overflow-y-auto pr-2">
        {notifications.map((notif, index) => (
          <motion.div
            key={notif.id || notif._id || `notification-${index}`}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: index * 0.15 }}
            className={`flex items-start gap-3 p-3 rounded-lg ${
              notif.type === 'alert' ? 'bg-amber-900/30 text-amber-200' : 'bg-cyan-900/30 text-cyan-200'
            }`}
          >
            {notif.type === 'alert' && <AlertTriangle className="w-5 h-5 mt-0.5 flex-shrink-0" />}
            <div className="text-sm">
              <p className="font-medium">{notif.message}</p>
              <p className="text-xs opacity-75 mt-1">{notif.time}</p>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
}