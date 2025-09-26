import React from 'react';
import { useAuth } from '../../context/AuthContext.jsx';

/**
 * A simple component to display the current auth state
 * This is useful for debugging purposes
 */
const AuthStatus = () => {
  const { user, isAuthenticated, loading, error } = useAuth();

  if (loading) {
    return (
      <div className="p-4 bg-blue-50 rounded-lg shadow-sm mb-4">
        <p className="text-blue-700">Loading authentication status...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4 bg-red-50 rounded-lg shadow-sm mb-4">
        <p className="text-red-700">Auth Error: {error}</p>
      </div>
    );
  }

  if (isAuthenticated && user) {
    return (
      <div className="p-4 bg-green-50 rounded-lg shadow-sm mb-4">
        <p className="text-green-700">
          Authenticated as: <strong>{user.username || user.email}</strong> (Role: {user.role})
        </p>
      </div>
    );
  }

  return (
    <div className="p-4 bg-gray-50 rounded-lg shadow-sm mb-4">
      <p className="text-gray-700">Not authenticated. Please log in.</p>
    </div>
  );
};

export default AuthStatus;
