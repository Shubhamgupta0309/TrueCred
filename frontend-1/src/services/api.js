import axios from "axios";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:5000/api";

export const api = axios.create({
  baseURL: API_URL,
  withCredentials: true,
  headers: {
    "Content-Type": "application/json",
    Accept: "application/json",
  }
});

api.interceptors.request.use(
  (config) => {
    // Don't add token for auth endpoints except refresh
    if (!config.url.startsWith('/auth/') || config.url === '/auth/refresh') {
      const token = localStorage.getItem("accessToken");
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    }
    return config;
  },
  (error) => Promise.reject(error)
);

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    // Check for CORS errors (will usually have no response object)
    if (!error.response) {
      // Detect CORS errors by checking for 'Network Error' message which is typically seen with CORS issues
      if (error.message.includes('Network Error') || error.message.includes('CORS')) {
        console.error('Possible CORS error detected:', error.message);
        
        // Try a CORS-friendly approach - make a JSONP request or redirect to mock data
        return Promise.reject({
          message: "Network error. This may be due to a CORS configuration issue.",
          isNetworkError: true,
          isCorsError: true,
          originalError: error
        });
      }
      
      return Promise.reject({
        message: "Network error. Please check your connection.",
        isNetworkError: true,
        originalError: error
      });
    }

    if (error.response.status === 403) {
      return Promise.reject({
        message: "Access denied. You do not have permission.",
        originalError: error
      });
    }

    if (error.response.status === 401 && originalRequest && !originalRequest._retry) {
      originalRequest._retry = true;
      try {
        const refreshToken = localStorage.getItem("refreshToken");
        if (!refreshToken) {
          localStorage.clear();
          window.location.href = "/auth";
          return Promise.reject(error);
        }

        const response = await axios.post(`${API_URL}/auth/refresh`, {
          refresh_token: refreshToken
        });

        const { access_token, refresh_token } = response.data.tokens;
        localStorage.setItem("accessToken", access_token);
        localStorage.setItem("refreshToken", refresh_token);

        originalRequest.headers.Authorization = `Bearer ${access_token}`;
        api.defaults.headers.common.Authorization = `Bearer ${access_token}`;

        return api(originalRequest);
      } catch (refreshError) {
        console.error("Token refresh failed:", refreshError);
        localStorage.clear();
        window.location.href = "/auth";
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject({
      message: error.response?.data?.message || "An error occurred",
      status: error.response?.status,
      originalError: error
    });
  }
);

export const authService = {
  login: async (credentials) => {
    const response = await api.post("/auth/login", credentials);
    return response.data;
  },
  register: async (userData) => {
    const response = await api.post("/auth/register", userData);
    return response.data;
  },
  logout: async () => {
    const response = await api.post("/auth/logout");
    return response.data;
  },
  refreshToken: async (refreshToken) => {
    const response = await api.post("/auth/refresh", { refresh_token: refreshToken });
    return response.data;
  },
  connectWallet: async (walletAddress) => {
    const response = await api.post("/auth/connect-wallet", { wallet_address: walletAddress });
    return response.data;
  },
  verifyEmail: async (token) => {
    const response = await api.get(`/auth/verify-email?token=${token}`);
    return response.data;
  },
  resendVerification: async (email) => {
    const response = await api.post("/auth/resend-verification", { email });
    return response.data;
  }
};

export const credentialService = {
  getCredentials: async () => {
    try {
      const response = await api.get("/students/credentials");
      return response.data;
    } catch (error) {
      console.error("Error fetching credentials:", error);
      if (error.message && error.message.includes("CORS")) {
        // If CORS error, throw with specific message to trigger mock data
        throw new Error("CORS_ERROR");
      }
      throw error;
    }
  },
  requestCredential: async (formData) => {
    try {
      const response = await api.post("/students/credentials/request", formData, {
        headers: { "Content-Type": "multipart/form-data" }
      });
      return response.data;
    } catch (error) {
      console.error("Error requesting credential:", error);
      if (error.message && error.message.includes("CORS")) {
        throw new Error("CORS_ERROR");
      }
      throw error;
    }
  },
  getCredentialById: async (credentialId) => {
    try {
      const response = await api.get(`/students/credentials/${credentialId}`);
      return response.data;
    } catch (error) {
      console.error("Error fetching credential by ID:", error);
      if (error.message && error.message.includes("CORS")) {
        throw new Error("CORS_ERROR");
      }
      throw error;
    }
  },
  getCredentialDocument: async (documentHash) => {
    try {
      const response = await api.get(`/ipfs/gateway/${documentHash}`);
      return response.data;
    } catch (error) {
      console.error("Error fetching credential document:", error);
      if (error.message && error.message.includes("CORS")) {
        throw new Error("CORS_ERROR");
      }
      throw error;
    }
  }
};

export const experienceService = {
  getExperiences: async () => {
    try {
      const response = await api.get("/students/experiences");
      return response.data;
    } catch (error) {
      console.error("Error fetching experiences:", error);
      if (error.message && error.message.includes("CORS")) {
        // If CORS error, throw with specific message to trigger mock data
        throw new Error("CORS_ERROR");
      }
      throw error;
    }
  },
  requestExperience: async (formData) => {
    try {
      const response = await api.post("/students/experiences/request", formData, {
        headers: { "Content-Type": "multipart/form-data" }
      });
      return response.data;
    } catch (error) {
      console.error("Error requesting experience:", error);
      if (error.message && error.message.includes("CORS")) {
        throw new Error("CORS_ERROR");
      }
      throw error;
    }
  },
  getExperienceById: async (experienceId) => {
    try {
      const response = await api.get(`/students/experiences/${experienceId}`);
      return response.data;
    } catch (error) {
      console.error("Error fetching experience by ID:", error);
      if (error.message && error.message.includes("CORS")) {
        throw new Error("CORS_ERROR");
      }
      throw error;
    }
    return response.data;
  }
};

export const instituteService = {
  verifyCredential: async (credentialId) => {
    const response = await api.post(`/institutes/verify-credential/${credentialId}`);
    return response.data;
  },
  getPendingVerifications: async () => {
    const response = await api.get("/institutes/pending-verifications");
    return response.data;
  },
  getVerifiedCredentials: async () => {
    const response = await api.get("/institutes/verified-credentials");
    return response.data;
  },
  getVerificationHistory: async () => {
    const response = await api.get("/institutes/verification-history");
    return response.data;
  },
  rejectCredential: async (credentialId, reason) => {
    const response = await api.post(`/institutes/reject-credential/${credentialId}`, { reason });
    return response.data;
  }
};

// Alias for backward compatibility
export const collegeService = instituteService;

export const companyService = {
  verifyExperience: async (experienceId) => {
    const response = await api.post(`/companies/verify-experience/${experienceId}`);
    return response.data;
  },
  getPendingVerifications: async () => {
    const response = await api.get("/companies/pending-verifications");
    return response.data;
  }
};
