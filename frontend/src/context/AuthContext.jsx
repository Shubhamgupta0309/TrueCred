import { createContext, useState, useEffect, useContext, useCallback, useRef, useMemo } from 'react';
import { api } from '../services/api';
import { decodeToken, isTokenExpired, getTimeUntilExpiration, throttle } from '../utils/tokenUtils';
import { Navigate, useNavigate } from 'react-router-dom';
import websocketService from '../services/websocket';
import pushNotificationService from '../services/pushNotifications';

// Create the auth context
const AuthContext = createContext();

// Custom hook to use auth context
export const useAuth = () => {
  return useContext(AuthContext);
};

// Auth provider component
export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [tokenRefreshInterval, setTokenRefreshInterval] = useState(null);
  const [lastProfileCheck, setLastProfileCheck] = useState(0);
  
  // Use a ref to track if a profile request is in progress
  const profileRequestInProgress = useRef(false);
  
  // Function to redirect to login page
  const redirectToLogin = useCallback(() => {
    // Clear user data
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    localStorage.removeItem('userRole');
    localStorage.removeItem('user');
    
    // Reset state
    setUser(null);
    
    // Redirect to login page
    window.location.href = '/auth';
  }, []);

  // Function to refresh the access token
  const refreshAccessToken = useCallback(async () => {
    try {
      const currentRefreshToken = localStorage.getItem('refreshToken');
      
      if (!currentRefreshToken) {
        throw new Error('No refresh token available');
      }

      const response = await api.post('/api/auth/refresh', {
        refresh_token: currentRefreshToken
      });

      const { access_token, refresh_token } = response.data.tokens;

      // Update tokens in localStorage
      localStorage.setItem('accessToken', access_token);
      localStorage.setItem('refreshToken', refresh_token);

      // Update API header
      api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;

      return true;
    } catch (err) {
      console.error('Error refreshing token:', err);
      // If refresh fails, log the user out
      localStorage.removeItem('accessToken');
      localStorage.removeItem('refreshToken');
      localStorage.removeItem('userRole');
      setUser(null);
      return false;
    }
  }, []);

  // Set up automatic token refresh based on expiration
  const setupTokenRefresh = useCallback((accessToken) => {
    // Clear any existing interval
    if (tokenRefreshInterval) {
      clearTimeout(tokenRefreshInterval);
    }
    
    try {
      // Calculate when to refresh (5 minutes before expiration)
      const timeUntilExpiration = getTimeUntilExpiration(accessToken);
      const refreshTime = Math.max(timeUntilExpiration - 5 * 60 * 1000, 0);
      
      console.log(`Token will refresh in ${Math.floor(refreshTime / 1000 / 60)} minutes`);
      
      // Set up the refresh as a single timeout, not an interval
      const timeoutId = setTimeout(() => {
        refreshAccessToken().then(success => {
          if (success) {
            // Set up the next refresh only after the current one completes
            setupTokenRefresh(localStorage.getItem('accessToken'));
          }
        });
      }, refreshTime);
      
      setTokenRefreshInterval(timeoutId);
    } catch (err) {
      console.error('Error setting up token refresh:', err);
    }
  }, [refreshAccessToken, tokenRefreshInterval]);

  // Listen for session expired events from API interceptors
  useEffect(() => {
    const handleSessionExpired = () => {
      console.log('Session expired event received');
      redirectToLogin();
    };
    
    // Add event listener
    window.addEventListener('auth:sessionExpired', handleSessionExpired);
    
    // Cleanup
    return () => {
      window.removeEventListener('auth:sessionExpired', handleSessionExpired);
    };
  }, [redirectToLogin]);

  // Memoized function to check user profile
  const checkUserProfile = useCallback(async () => {
    // If a request is already in progress, don't start another one
    if (profileRequestInProgress.current) return;
    
    // Skip if we've checked recently (within last 10 seconds)
    const now = Date.now();
    if (now - lastProfileCheck < 10000) return;
    
    profileRequestInProgress.current = true;
    setLastProfileCheck(now);
    
    try {
      const response = await api.get('/api/auth/profile');
      setUser(response.data.user);
    } catch (err) {
      console.error('Error checking user profile:', err);
      // Only clear on 401 Unauthorized or similar auth errors
      if (err.response && (err.response.status === 401 || err.response.status === 403)) {
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
        localStorage.removeItem('userRole');
        setUser(null);
      }
    } finally {
      profileRequestInProgress.current = false;
    }
  }, [setLastProfileCheck]); // Minimal dependencies to avoid re-creation
  
  // Throttled version for UI events
  const throttledCheckUserProfile = useMemo(() => 
    throttle(checkUserProfile, 1000), 
  [checkUserProfile]);

  // Check if user is already logged in on mount
  useEffect(() => {
    
    // One-time check on mount only
    const checkLoggedInOnMount = async () => {
      setLoading(true);
      try {
        // Check if tokens exist in localStorage
        const accessToken = localStorage.getItem('accessToken');
        const refreshToken = localStorage.getItem('refreshToken');
        
        if (!accessToken || !refreshToken) {
          // No tokens found, user is not logged in
          setLoading(false);
          return;
        }
        
        // Check if token is expired
        if (isTokenExpired(accessToken)) {
          console.log('Access token expired, attempting to refresh...');
          const refreshSuccess = await refreshAccessToken();
          
          if (!refreshSuccess) {
            setLoading(false);
            return;
          }
        }
        
        // Set token in API header (using the potentially refreshed token)
        const currentToken = localStorage.getItem('accessToken');
        api.defaults.headers.common['Authorization'] = `Bearer ${currentToken}`;
        
        // Get user profile once
        await checkUserProfile();
        
        // Set up token refresh
        setupTokenRefresh(currentToken);
      } catch (err) {
        console.error('Error checking authentication:', err);
        // Clear tokens if invalid
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
        localStorage.removeItem('userRole');
        setError('Session expired. Please login again.');
      } finally {
        setLoading(false);
      }
    };

    checkLoggedInOnMount();
    
    // Clean up refresh interval on unmount
    return () => {
      if (tokenRefreshInterval) {
        clearTimeout(tokenRefreshInterval);
      }
    };
  }, []); // Empty dependency array - only run once on mount

  // Login function
  const login = async (usernameOrEmail, password) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await api.post('/api/auth/login', {
        username_or_email: usernameOrEmail,
        password
      });

      const { user, tokens } = response.data;
      
      // Store tokens in localStorage
      localStorage.setItem('accessToken', tokens.access_token);
      localStorage.setItem('refreshToken', tokens.refresh_token);
      localStorage.setItem('userRole', user.role); // Store user role for redirection
      
      // Set token for future API requests
      api.defaults.headers.common['Authorization'] = `Bearer ${tokens.access_token}`;
      
      // Set up token refresh
      setupTokenRefresh(tokens.access_token);
      
      // Connect to WebSocket for real-time notifications
      try {
        websocketService.connect(tokens.access_token);
        console.log('WebSocket connection initiated');
      } catch (wsError) {
        console.error('Failed to connect to WebSocket:', wsError);
      }

      // Set up push notifications
      try {
        const pushSetup = await pushNotificationService.setupPushNotifications();
        if (pushSetup) {
          console.log('Push notifications setup completed');
        } else {
          console.log('Push notifications setup skipped or failed');
        }
      } catch (pushError) {
        console.error('Failed to setup push notifications:', pushError);
      }

      setUser(user);
      setError(null); // Clear any previous errors on successful login
      return true;
    } catch (err) {
      console.error('Login error:', err);
      
      // Check if the error is due to unverified email
      if (err.response?.data?.message && err.response.data.message.includes('Email not verified')) {
        const email = usernameOrEmail.includes('@') ? usernameOrEmail : null;
        setError('Email not verified. Please check your inbox for a verification link.');
        return { needsVerification: true, email };
      }
      
      // Extract detailed error message if available
      let errorMessage = 'Login failed. Please check your credentials.';
      
      // Handle specific 401 Unauthorized errors
      if (err.response?.status === 401) {
        // Check if the error is due to invalid credentials
        if (err.response?.data?.message === "Invalid username/email or password") {
          errorMessage = 'User does not exist or password is incorrect. Please check your credentials.';
        } else {
          errorMessage = 'Invalid email or password. Please try again.';
        }
      } else if (err.response?.data?.message) {
        errorMessage = err.response.data.message;
      } else if (err.response?.data?.error) {
        errorMessage = err.response.data.error;
      } else if (!err.response) {
        // Network errors or server unavailable
        errorMessage = 'Unable to connect to the server. Please check your internet connection.';
      }
      
      setError(errorMessage);
      return false;
    } finally {
      setLoading(false);
    }
  };

  // Register function
  const register = async (userData) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await api.post('/api/auth/register', userData);
      
      const { user, tokens, needsEmailVerification } = response.data;
      
      // If email verification is required, don't store tokens or set user
      if (needsEmailVerification) {
        setError(null); // Clear any previous errors
        return { success: true, needsEmailVerification: true, email: userData.email };
      }
      
      // Store tokens in localStorage
      localStorage.setItem('accessToken', tokens.access_token);
      localStorage.setItem('refreshToken', tokens.refresh_token);
      localStorage.setItem('userRole', user.role); // Store user role for redirection
      
      // Set token for future API requests
      api.defaults.headers.common['Authorization'] = `Bearer ${tokens.access_token}`;
      
      // Set up token refresh
      setupTokenRefresh(tokens.access_token);
      
      setUser(user);
      setError(null); // Clear any previous errors
      return { success: true };
    } catch (err) {
      console.error('Registration error:', err);
      
      // Extract detailed error message if available
      let errorMessage = 'Registration failed. Please try again.';
      
      if (err.response?.status === 400 && err.response?.data?.message?.includes('already exists')) {
        errorMessage = 'This email is already registered. Please try logging in instead.';
      } else if (err.response?.status === 400 && err.response?.data?.message?.includes('password')) {
        errorMessage = 'Password does not meet requirements. Please use a stronger password.';
      } else if (err.response?.data?.message) {
        errorMessage = err.response.data.message;
      } else if (err.response?.data?.error) {
        errorMessage = err.response.data.error;
      }
      
      setError(errorMessage);
      return { success: false, error: errorMessage };
    } finally {
      setLoading(false);
    }
  };

  // Logout function
  const logout = async () => {
    try {
      // Call logout API if needed
      await api.post('/api/auth/logout');
    } catch (err) {
      console.error('Logout error:', err);
    } finally {
      // Clear token refresh interval
      if (tokenRefreshInterval) {
        clearTimeout(tokenRefreshInterval);
        setTokenRefreshInterval(null);
      }
      
      // Disconnect from WebSocket
      try {
        websocketService.disconnect();
        console.log('WebSocket disconnected');
      } catch (wsError) {
        console.error('Error disconnecting WebSocket:', wsError);
      }

      // Clean up push notifications
      try {
        await pushNotificationService.cleanup();
        console.log('Push notifications cleaned up');
      } catch (pushError) {
        console.error('Error cleaning up push notifications:', pushError);
      }

      // Remove tokens from localStorage
      localStorage.removeItem('accessToken');
      localStorage.removeItem('refreshToken');
      localStorage.removeItem('userRole'); // Also remove user role
      localStorage.removeItem('walletAddress'); // Remove wallet address
      
      // Remove Authorization header
      delete api.defaults.headers.common['Authorization'];
      
      setUser(null);
    }
  };

  // Update user profile
  const updateProfile = async (profileData) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await api.put('/api/auth/profile', profileData);
      setUser(response.data.user);
      return true;
    } catch (err) {
      console.error('Profile update error:', err);
      setError(err.response?.data?.message || 'Failed to update profile.');
      return false;
    } finally {
      setLoading(false);
    }
  };

  // Wallet authentication function
  const walletAuth = async (walletAddress) => {
    // If user is already authenticated, don't make another request
    if (user) {
      console.log('User already authenticated, skipping wallet auth request');
      return { success: true, role: user.role };
    }
    
    setLoading(true);
    setError(null);
    
    try {
      // Ensure wallet address is lowercase for consistency
      const normalizedAddress = walletAddress.toLowerCase();
      console.log('AuthContext: Sending wallet auth request with address:', normalizedAddress);
      
      const response = await api.post('/api/auth/wallet-auth', {
        wallet_address: normalizedAddress
      });

      console.log('Wallet auth response:', response.data);
      
      const { user, tokens } = response.data;
      
      // Store tokens in localStorage
      localStorage.setItem('accessToken', tokens.access_token);
      localStorage.setItem('refreshToken', tokens.refresh_token);
      localStorage.setItem('userRole', user.role); // Store user role for redirection
      localStorage.setItem('walletAddress', normalizedAddress);
      
      // Set token for future API requests
      api.defaults.headers.common['Authorization'] = `Bearer ${tokens.access_token}`;
      
      setUser(user);
      return { success: true, role: user.role };
    } catch (err) {
      console.error('Wallet authentication error:', err);
      console.error('Error response:', err.response?.data);
      
      // Extract detailed error message if available
      const errorMessage = err.response?.data?.message || 
                          err.response?.data?.error || 
                          'Wallet authentication failed. This wallet may not be registered.';
      setError(errorMessage);
      return { success: false, error: errorMessage };
    } finally {
      setLoading(false);
    }
  };

  // Connect wallet to existing account
  const connectWallet = async (walletAddress) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await api.post('/api/auth/connect-wallet', {
        wallet_address: walletAddress
      });
      
      // Update user with wallet address
      const updatedUser = { ...user, wallet_address: walletAddress };
      localStorage.setItem('walletAddress', walletAddress);
      setUser(updatedUser);
      return true;
    } catch (err) {
      console.error('Wallet connection error:', err);
      const errorMessage = err.response?.data?.message || 
                          err.response?.data?.error || 
                          'Failed to connect wallet. Please try again.';
      setError(errorMessage);
      return false;
    } finally {
      setLoading(false);
    }
  };

  // Create value object for context
  const value = {
    user,
    loading,
    error,
    isAuthenticated: !!user,
    login,
    register,
    logout,
    updateProfile,
    walletAuth,
    connectWallet,
    setError,
    refreshToken: refreshAccessToken,
    // Provide alias for components expecting refreshAccessToken
    refreshAccessToken: refreshAccessToken,
    checkProfile: throttledCheckUserProfile,
    updateUser: (userData) => {
      // Update user state directly
      setUser(prevUser => ({
        ...prevUser,
        ...userData
      }));
    },
    resendVerificationEmail: async (email) => {
      try {
        const response = await api.post('/api/auth/resend-verification', { email });
        return response.data;
      } catch (err) {
        console.error('Error resending verification email:', err);
        throw err;
      }
    },
    verifyEmail: async (token) => {
      try {
        const response = await api.get(`/api/auth/verify-email?token=${token}`);
        if (response.data.success) {
          const { user, tokens } = response.data;
          
          // Store tokens in localStorage
          localStorage.setItem('accessToken', tokens.access_token);
          localStorage.setItem('refreshToken', tokens.refresh_token);
          localStorage.setItem('userRole', user.role);
          
          // Set token for future API requests
          api.defaults.headers.common['Authorization'] = `Bearer ${tokens.access_token}`;
          
          // Update user state
          setUser(user);
        }
        return response.data;
      } catch (err) {
        console.error('Error verifying email:', err);
        // Return a formatted error response instead of throwing
        return {
          success: false, 
          message: err.response?.data?.message || 'Failed to verify email. The token may be invalid or expired.'
        };
      }
    }
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export default AuthContext;
