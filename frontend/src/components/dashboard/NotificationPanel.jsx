import React from 'react';
import { motion } from 'framer-motion';
import { Bell, AlertTriangle } from 'lucide-react';

export default function NotificationPanel({ notifications }) {
  return (
    <div className="bg-white rounded-2xl shadow-lg shadow-purple-500/10 p-6 h-full">
      <h3 className="text-lg font-bold text-gray-800 mb-4 flex items-center gap-2">
        <Bell className="w-5 h-5 text-purple-600" />
        Notifications
      </h3>
      <div className="space-y-3 max-h-60 overflow-y-auto pr-2">
        {notifications.map((notif, index) => (
          <motion.div
            key={notif.id}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: index * 0.15 }}
            className={`flex items-start gap-3 p-3 rounded-lg ${
              notif.type === 'alert' ? 'bg-yellow-50 text-yellow-800' : 'bg-blue-50 text-blue-800'
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