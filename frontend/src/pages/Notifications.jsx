import React, { useState, useEffect } from 'react';

const Notifications = () => {
  const [notifications, setNotifications] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchNotifications = async () => {
      setIsLoading(true);
      try {
        const resp = await fetch('/api/notifications', {
          headers: { 'Authorization': `Bearer ${localStorage.getItem('accessToken')}` }
        });
        const data = await resp.json();
        if (data.success) setNotifications(data.notifications);
      } catch (err) {
        setError('Failed to fetch notifications');
      }
      setIsLoading(false);
    };
    fetchNotifications();
    const interval = setInterval(fetchNotifications, 10000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="max-w-xl mx-auto p-6 bg-white rounded shadow">
      <h2 className="text-2xl font-bold mb-4">Notifications</h2>
      {error && <div className="text-red-500 mb-2">{error}</div>}
      <ul>
        {notifications.length === 0 && <li className="text-gray-500">No notifications</li>}
        {notifications.map(n => (
          <li key={n.id || n._id} className="mb-2 p-2 border rounded">
            <strong>{n.title}</strong> - {n.message}
            <div className="text-xs text-gray-500">{new Date(n.created_at).toLocaleString()}</div>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default Notifications;
