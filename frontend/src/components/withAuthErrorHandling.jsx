import React, { useState, useEffect } from 'react';
import { isAuthenticated } from '../utils/tokenUtils';
import AuthenticationModal from './common/AuthenticationModal';

/**
 * Higher-order component that adds authentication error handling
 * Shows an authentication modal when session expires
 */
const withAuthErrorHandling = (WrappedComponent) => {
  return function WithAuthErrorHandling(props) {
    const [authModalOpen, setAuthModalOpen] = useState(false);
    
    // Listen for session expired events
    useEffect(() => {
      const handleSessionExpired = () => {
        setAuthModalOpen(true);
      };
      
      // Add event listener
      window.addEventListener('auth:sessionExpired', handleSessionExpired);
      
      // Cleanup
      return () => {
        window.removeEventListener('auth:sessionExpired', handleSessionExpired);
      };
    }, []);
    
    // Function to handle error from wrapped component
    const handleAuthError = (error) => {
      if (error?.response?.status === 401) {
        setAuthModalOpen(true);
        return true; // Handled
      }
      return false; // Not handled
    };
    
    return (
      <>
        <WrappedComponent {...props} onAuthError={handleAuthError} />
        <AuthenticationModal 
          isOpen={authModalOpen} 
          onClose={() => setAuthModalOpen(false)}
          onRefresh={() => {
            // Force re-render of the wrapped component
            window.location.reload();
          }}
        />
      </>
    );
  };
};

export default withAuthErrorHandling;
