import axios from 'axios';

// Base URL for the API - use Vite's environment variables
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

// Create an axios instance with default config
export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Track if token refresh is in progress
let isRefreshing = false;
let refreshSubscribers = [];

// Function to push callbacks to array
const subscribeTokenRefresh = (callback) => {
  refreshSubscribers.push(callback);
};

// Function to execute callbacks with new token
const onRefreshed = (token) => {
  refreshSubscribers.forEach(callback => callback(token));
  refreshSubscribers = [];
};

// Request interceptor for adding auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('accessToken');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for handling token expiration
api.interceptors.response.use(
  (response) => {
    return response;
  },
  async (error) => {
    const originalRequest = error.config;
    
    // If there's no response (network/CORS), propagate a friendly error
    if (!error.response) {
      console.error('Network error or CORS issue:', error);
      return Promise.reject({
        message: 'Network error or CORS blocked the request',
        isNetworkError: true,
        originalError: error,
      });
    }

    // If error is not 401 or request already retried, reject
    if (error.response.status !== 401 || originalRequest._retry) {
      // Add more context to server errors for easier debugging
      try {
        const method = originalRequest.method ? originalRequest.method.toUpperCase() : 'GET';
        const url = originalRequest.url || (originalRequest.baseURL ? originalRequest.baseURL + originalRequest.url : '(unknown)');
        console.error('API Error - Request:', method, url, 'Status:', error.response.status);
        if (error.response.data) {
          console.error('API Error - Response Body:', error.response.data);
        }
        // Also include original request config for deeper debugging
        console.debug('API Error - Original Request config:', originalRequest);
      } catch (logErr) {
        console.error('Error logging API error context', logErr);
      }

      return Promise.reject(error);
    }

    // Mark request as retried
    originalRequest._retry = true;

    // If token refresh is not in progress, start refresh
    if (!isRefreshing) {
      isRefreshing = true;

      try {
        // Get refresh token from storage
        const refreshToken = localStorage.getItem('refreshToken');
        
        if (!refreshToken) {
          throw new Error('No refresh token available');
        }

        // Call refresh endpoint
            const response = await axios.post(`${API_URL}/api/auth/refresh`, {
              refresh_token: refreshToken
            });

            // Backend may return tokens under response.data.tokens or directly
            // Normalize both shapes for compatibility
            let access_token = null;
            let refresh_token = null;
            if (response.data) {
              if (response.data.tokens) {
                access_token = response.data.tokens.access_token;
                refresh_token = response.data.tokens.refresh_token;
              } else {
                access_token = response.data.access_token || response.data.token || null;
                // some backends return refresh_token at top level
                refresh_token = response.data.refresh_token || null;
              }
            }

            if (!access_token) {
              throw new Error('Refresh did not return an access token');
            }

            // Update tokens in storage
            localStorage.setItem('accessToken', access_token);
            if (refresh_token) {
              localStorage.setItem('refreshToken', refresh_token);
            }
        
        // Update auth header for original request
        originalRequest.headers['Authorization'] = `Bearer ${access_token}`;
        
        // Notify all waiting requests
        onRefreshed(access_token);
        
        // Reset refresh state
        isRefreshing = false;
        
        // Retry original request
        return axios(originalRequest);
        } catch (refreshError) {
        // Reset refresh state
        isRefreshing = false;
        
        // Clear tokens and reject all waiting requests
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
        localStorage.removeItem('user');
        localStorage.removeItem('userRole');
        
        // Trigger session expired event
        window.dispatchEvent(new CustomEvent('auth:sessionExpired'));
        
        // Redirect to login
        window.location.href = '/auth';
        
        return Promise.reject(refreshError);
      }
    } else {
      // If refresh already in progress, wait for new token
      return new Promise((resolve) => {
        subscribeTokenRefresh((token) => {
          originalRequest.headers['Authorization'] = `Bearer ${token}`;
          resolve(axios(originalRequest));
        });
      });
    }
  }
);

// Auth services
export const authService = {
  login: (credentials) => api.post('/api/auth/login', credentials),
  register: (userData) => api.post('/api/auth/register', userData),
  logout: () => api.post('/api/auth/logout'),
  refreshToken: (refreshToken) => api.post('/api/auth/refresh', { refresh_token: refreshToken }),
  connectWallet: (walletAddress) => api.post('/api/auth/connect-wallet', { wallet_address: walletAddress }),
  verifyEmail: (token) => api.get(`/api/auth/verify-email?token=${token}`),
  resendVerification: (email) => api.post('/api/auth/resend-verification', { email }),
};

// Credential services
export const credentialService = {
  getCredentials: () => api.get('/api/credentials'),
  requestCredential: (credentialData) => api.post('/api/credentials/request', credentialData),
  verifyCredential: (credentialId) => api.post(`/api/credentials/${credentialId}/verify`),
  verifyCredentialBlockchain: (credentialId) => api.get(`/api/credentials/blockchain/verify/${credentialId}`),
  getUserRequests: () => api.get('/api/user/requests'),
};

// Experience services
export const experienceService = {
  getExperiences: () => api.get('/api/experiences'),
  requestExperience: (experienceData) => api.post('/api/experiences/request', experienceData),
  verifyExperience: (experienceId) => api.post(`/api/experiences/${experienceId}/verify`),
};

// College services
export const collegeService = {
  // Only keep endpoints that are implemented in backend
  // Remove unused or non-existent endpoints
  getPendingRequests: () => api.get('/api/college/pending-requests'),
  approveRequest: (requestId) => api.post(`/api/credentials/${requestId}/approve`),
  rejectRequest: (requestId, reason) => api.post(`/api/credentials/${requestId}/reject`, { reason }),
};

// Company services
export const companyService = {
  getPendingExperienceRequests: () => api.get('/api/experiences/pending'),
  approveExperienceRequest: (requestId) => api.post(`/api/experiences/${requestId}/approve`),
  rejectExperienceRequest: (requestId, reason) => api.post(`/api/experiences/${requestId}/reject`, { reason }),
  getExperienceHistory: () => api.get('/api/experiences/history'),
};

// Notification services
export const notificationService = {
  getNotifications: () => api.get('/api/notifications'),
};

// Organization services
export const organizationService = {
  getInstitutions: (query) => api.get(`/api/organizations/institutions${query ? `?query=${encodeURIComponent(query)}` : ''}`),
  getOrganizationById: (id) => api.get(`/api/organizations/${id}`),
};

// Export the api instance for direct use if needed
export default api;
