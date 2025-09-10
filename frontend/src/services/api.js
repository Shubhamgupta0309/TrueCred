import axios from 'axios';

// Base URL for the API
const API_URL = 'http://localhost:5000/api';

// Create an axios instance with default config
export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

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
    
    // If the error is 401 and we haven't retried yet
    if (error.response.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      try {
        // Try to refresh the token
        const refreshToken = localStorage.getItem('refreshToken');
        if (!refreshToken) {
          // No refresh token, redirect to login
          window.location.href = '/auth';
          return Promise.reject(error);
        }
        
        const response = await axios.post(`${API_URL}/auth/refresh`, {
          refresh_token: refreshToken
        });
        
        const { access_token } = response.data;
        localStorage.setItem('accessToken', access_token);
        
        // Retry the original request with the new token
        originalRequest.headers['Authorization'] = `Bearer ${access_token}`;
        return axios(originalRequest);
      } catch (err) {
        // Refresh token failed, redirect to login
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
        localStorage.removeItem('userRole');
        window.location.href = '/auth';
        return Promise.reject(error);
      }
    }
    
    return Promise.reject(error);
  }
);

// Auth services
export const authService = {
  login: (credentials) => api.post('/auth/login', credentials),
  register: (userData) => api.post('/auth/register', userData),
  logout: () => api.post('/auth/logout'),
  refreshToken: (refreshToken) => api.post('/auth/refresh', { refresh_token: refreshToken }),
  connectWallet: (walletAddress) => api.post('/auth/connect-wallet', { wallet_address: walletAddress }),
  verifyEmail: (token) => api.get(`/auth/verify-email?token=${token}`),
  resendVerification: (email) => api.post('/auth/resend-verification', { email }),
};

// Credential services
export const credentialService = {
  getCredentials: () => api.get('/credentials'),
  requestCredential: (credentialData) => api.post('/credentials/request', credentialData),
  verifyCredential: (credentialId) => api.post(`/credentials/${credentialId}/verify`),
};

// Experience services
export const experienceService = {
  getExperiences: () => api.get('/experiences'),
  requestExperience: (experienceData) => api.post('/experiences/request', experienceData),
  verifyExperience: (experienceId) => api.post(`/experiences/${experienceId}/verify`),
};

// College services
export const collegeService = {
  getPendingRequests: () => api.get('/credentials/pending'),
  approveRequest: (requestId) => api.post(`/credentials/${requestId}/approve`),
  rejectRequest: (requestId, reason) => api.post(`/credentials/${requestId}/reject`, { reason }),
  getVerificationHistory: () => api.get('/credentials/history'),
};

// Company services
export const companyService = {
  getPendingExperienceRequests: () => api.get('/experiences/pending'),
  approveExperienceRequest: (requestId) => api.post(`/experiences/${requestId}/approve`),
  rejectExperienceRequest: (requestId, reason) => api.post(`/experiences/${requestId}/reject`, { reason }),
  getExperienceHistory: () => api.get('/experiences/history'),
};

// Export the api instance for direct use if needed
export default api;
