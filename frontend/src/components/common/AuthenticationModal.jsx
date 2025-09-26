import React, { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import { isAuthenticated, getTokenStatus } from '../../utils/tokenUtils';
import { motion } from 'framer-motion';

/**
 * Component that displays when authentication issues are detected
 * Provides options to refresh or redirect to login
 */
const AuthenticationModal = ({ isOpen, onClose, onRefresh }) => {
  const { refreshAccessToken } = useAuth();
  const navigate = useNavigate();
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState(null);
  
  // Auto-refresh on open
  useEffect(() => {
    if (isOpen) {
      handleRefresh();
    }
  }, [isOpen]);
  
  const handleRefresh = async () => {
    setRefreshing(true);
    setError(null);
    
    try {
      const success = await refreshAccessToken();
      
      if (success) {
        onRefresh?.();
        onClose();
      } else {
        setError('Unable to refresh your session. Please log in again.');
      }
    } catch (err) {
      console.error('Refresh error:', err);
      setError('An error occurred while refreshing your session.');
    } finally {
      setRefreshing(false);
    }
  };
  
  const handleLogin = () => {
    navigate('/auth');
    onClose();
  };
  
  if (!isOpen) return null;
  
  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: 20 }}
        className="bg-white rounded-lg shadow-xl p-6 max-w-md w-full mx-4"
      >
        <div className="text-center mb-6">
          <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          </div>
          <h3 className="text-xl font-semibold text-gray-900">Session Expired</h3>
          <p className="mt-2 text-gray-600">
            Your session has expired or you need to log in again to continue.
          </p>
          {error && (
            <p className="mt-2 text-sm text-red-600">{error}</p>
          )}
        </div>
        
        <div className="flex flex-col space-y-3">
          <button
            onClick={handleRefresh}
            disabled={refreshing}
            className="w-full py-2 px-4 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-md transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50"
          >
            {refreshing ? 'Refreshing...' : 'Refresh Session'}
          </button>
          
          <button
            onClick={handleLogin}
            className="w-full py-2 px-4 bg-gray-200 hover:bg-gray-300 text-gray-800 font-medium rounded-md transition-colors focus:outline-none focus:ring-2 focus:ring-gray-400 focus:ring-offset-2"
          >
            Log In Again
          </button>
        </div>
      </motion.div>
    </div>
  );
};

export default AuthenticationModal;
