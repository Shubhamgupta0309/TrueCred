import React, { useEffect, useState } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext.jsx';

// Protected route component that checks if user is authenticated and has the correct role
const ProtectedRoute = ({ element, allowedRoles = [] }) => {
  const { isAuthenticated, user, loading } = useAuth();
  const location = useLocation();
  const [isAuthorized, setIsAuthorized] = useState(false);
  const [isChecking, setIsChecking] = useState(true);

  useEffect(() => {
    // Wait for authentication to complete
    if (!loading) {
      // Check if user is authenticated
      if (!isAuthenticated) {
        setIsAuthorized(false);
        setIsChecking(false);
        return;
      }

      // If no specific roles are required, or user's role is in the allowed roles
      if (allowedRoles.length === 0 || allowedRoles.includes(user?.role)) {
        setIsAuthorized(true);
      } else {
        setIsAuthorized(false);
      }
      
      setIsChecking(false);
    }
  }, [isAuthenticated, user, loading, allowedRoles]);  if (isChecking || loading) {
    // Show loading state while checking authorization
    return (
      <div className="min-h-screen flex items-center justify-center bg-purple-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-purple-600 mx-auto"></div>
          <p className="mt-4 text-gray-700">Verifying access...</p>
        </div>
      </div>
    );
  }

  // If not authorized, redirect to login
  if (!isAuthorized) {
    return <Navigate to="/auth" state={{ from: location }} replace />;
  }

  // If authorized, render the protected component
  return element;
};

export default ProtectedRoute;
