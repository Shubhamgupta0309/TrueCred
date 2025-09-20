import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Bell, Mail, Smartphone, Globe, Clock, TestTube, Save, RotateCcw } from 'lucide-react';
import { useAuth } from '../context/AuthContext.jsx';
import { api } from '../services/api';

const NotificationPreferences = () => {
  const { user } = useAuth();
  const [preferences, setPreferences] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [channels, setChannels] = useState(null);

  // Fetch notification preferences
  const fetchPreferences = async () => {
    setIsLoading(true);
    try {
      const resp = await api.get('/api/notification-preferences/');
      setPreferences(resp.data.data);
    } catch (err) {
      setError('Failed to fetch notification preferences');
      console.error('Fetch error:', err);
    }
    setIsLoading(false);
  };

  // Fetch available channels
  const fetchChannels = async () => {
    try {
      const resp = await api.get('/api/notification-preferences/channels');
      setChannels(resp.data.data.channels);
    } catch (err) {
      console.error('Channels fetch error:', err);
    }
  };

  // Save preferences
  const savePreferences = async () => {
    setIsSaving(true);
    setError('');
    setSuccess('');

    try {
      const resp = await api.put('/api/notification-preferences/', preferences);
      setPreferences(resp.data.data);
      setSuccess('Notification preferences saved successfully!');
    } catch (err) {
      setError('Failed to save notification preferences');
      console.error('Save error:', err);
    }
    setIsSaving(false);
  };

  // Reset to defaults
  const resetPreferences = async () => {
    if (!confirm('Are you sure you want to reset all preferences to defaults?')) return;

    setIsSaving(true);
    try {
      const resp = await api.post('/api/notification-preferences/reset');
      setPreferences(resp.data.data);
      setSuccess('Notification preferences reset to defaults!');
    } catch (err) {
      setError('Failed to reset notification preferences');
      console.error('Reset error:', err);
    }
    setIsSaving(false);
  };

  // Test notification channel
  const testChannel = async (channel) => {
    try {
      await api.post(`/api/notification-preferences/test/${channel}`);
      setSuccess(`Test ${channel} notification sent!`);
    } catch (err) {
      setError(`Failed to send test ${channel} notification`);
      console.error('Test error:', err);
    }
  };

  // Update preference
  const updatePreference = (key, value) => {
    setPreferences(prev => ({
      ...prev,
      [key]: value
    }));
  };

  // Effect to fetch data on mount
  useEffect(() => {
    fetchPreferences();
    fetchChannels();
  }, []);

  // Channel icons
  const getChannelIcon = (channel) => {
    switch (channel) {
      case 'email':
        return <Mail className="w-5 h-5" />;
      case 'push':
        return <Smartphone className="w-5 h-5" />;
      case 'websocket':
        return <Globe className="w-5 h-5" />;
      case 'browser':
        return <Bell className="w-5 h-5" />;
      default:
        return <Bell className="w-5 h-5" />;
    }
  };

  if (isLoading) {
    return (
      <div className="max-w-4xl mx-auto p-6 bg-white min-h-screen">
        <div className="text-center py-12">
          <div className="w-8 h-8 border-4 border-purple-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600">Loading notification preferences...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto p-6 bg-white min-h-screen">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-8"
      >
        <div className="flex items-center gap-3 mb-2">
          <Bell className="w-8 h-8 text-purple-600" />
          <div>
            <h1 className="text-2xl font-bold text-gray-800">Notification Preferences</h1>
            <p className="text-gray-600 text-sm">Customize how and when you receive notifications</p>
          </div>
        </div>
      </motion.div>

      {/* Success/Error Messages */}
      {error && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg"
        >
          <p className="text-red-700">{error}</p>
        </motion.div>
      )}

      {success && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg"
        >
          <p className="text-green-700">{success}</p>
        </motion.div>
      )}

      {preferences && channels && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.1 }}
          className="space-y-8"
        >
          {/* Channel Preferences */}
          {Object.entries(channels).map(([channelKey, channelInfo], index) => (
            <motion.div
              key={channelKey}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="bg-gray-50 rounded-lg p-6"
            >
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                  {getChannelIcon(channelKey)}
                  <div>
                    <h3 className="text-lg font-semibold text-gray-800">{channelInfo.name}</h3>
                    <p className="text-gray-600 text-sm">{channelInfo.description}</p>
                  </div>
                </div>

                <div className="flex items-center gap-4">
                  <label className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      checked={preferences[`${channelKey}_enabled`] || false}
                      onChange={(e) => updatePreference(`${channelKey}_enabled`, e.target.checked)}
                      className="w-4 h-4 text-purple-600 rounded focus:ring-purple-500"
                    />
                    <span className="text-sm font-medium text-gray-700">Enabled</span>
                  </label>

                  <button
                    onClick={() => testChannel(channelKey)}
                    className="flex items-center gap-2 px-3 py-1 text-sm bg-purple-100 text-purple-700 rounded hover:bg-purple-200 transition-colors"
                  >
                    <TestTube className="w-4 h-4" />
                    Test
                  </button>
                </div>
              </div>

              {/* Notification Types */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {Object.entries(channelInfo.types).map(([typeKey, typeDescription]) => (
                  <label key={typeKey} className="flex items-center gap-3 p-3 bg-white rounded border">
                    <input
                      type="checkbox"
                      checked={preferences[`${channelKey}_${typeKey}`] !== false}
                      onChange={(e) => updatePreference(`${channelKey}_${typeKey}`, e.target.checked)}
                      disabled={!preferences[`${channelKey}_enabled`]}
                      className="w-4 h-4 text-purple-600 rounded focus:ring-purple-500 disabled:opacity-50"
                    />
                    <div className="flex-1">
                      <span className="text-sm font-medium text-gray-700 capitalize">
                        {typeKey.replace('_', ' ')}
                      </span>
                      <p className="text-xs text-gray-500">{typeDescription}</p>
                    </div>
                  </label>
                ))}
              </div>
            </motion.div>
          ))}

          {/* Quiet Hours */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-gray-50 rounded-lg p-6"
          >
            <div className="flex items-center gap-3 mb-4">
              <Clock className="w-5 h-5 text-purple-600" />
              <div>
                <h3 className="text-lg font-semibold text-gray-800">Quiet Hours</h3>
                <p className="text-gray-600 text-sm">Disable push and browser notifications during specified hours</p>
              </div>
            </div>

            <div className="space-y-4">
              <label className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={preferences.quiet_hours_enabled || false}
                  onChange={(e) => updatePreference('quiet_hours_enabled', e.target.checked)}
                  className="w-4 h-4 text-purple-600 rounded focus:ring-purple-500"
                />
                <span className="text-sm font-medium text-gray-700">Enable quiet hours</span>
              </label>

              {preferences.quiet_hours_enabled && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 ml-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Start Time
                    </label>
                    <input
                      type="time"
                      value={preferences.quiet_hours_start || '22:00'}
                      onChange={(e) => updatePreference('quiet_hours_start', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-purple-500 focus:border-purple-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      End Time
                    </label>
                    <input
                      type="time"
                      value={preferences.quiet_hours_end || '08:00'}
                      onChange={(e) => updatePreference('quiet_hours_end', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-purple-500 focus:border-purple-500"
                    />
                  </div>
                </div>
              )}
            </div>
          </motion.div>

          {/* Action Buttons */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex items-center justify-end gap-4 pt-6 border-t"
          >
            <button
              onClick={resetPreferences}
              disabled={isSaving}
              className="flex items-center gap-2 px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors disabled:opacity-50"
            >
              <RotateCcw className="w-4 h-4" />
              Reset to Defaults
            </button>

            <button
              onClick={savePreferences}
              disabled={isSaving}
              className="flex items-center gap-2 px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors disabled:opacity-50"
            >
              {isSaving ? (
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
              ) : (
                <Save className="w-4 h-4" />
              )}
              {isSaving ? 'Saving...' : 'Save Preferences'}
            </button>
          </motion.div>
        </motion.div>
      )}
    </div>
  );
};

export default NotificationPreferences;