/**
 * Enhanced utility functions for JWT token handling
 */

/**
 * Decode a JWT token without verification
 * @param {string} token - JWT token to decode
 * @returns {object|null} Decoded token payload or null if invalid
 */
export function decodeToken(token) {
  try {
    if (!token) return null;
    
    // Split the token into parts
    const parts = token.split('.');
    if (parts.length !== 3) return null;
    
    // Decode the payload (middle part)
    const payload = parts[1];
    const decodedPayload = JSON.parse(atob(payload.replace(/-/g, '+').replace(/_/g, '/')));
    
    return decodedPayload;
  } catch (error) {
    console.error('Error decoding token:', error);
    return null;
  }
}

/**
 * Check if a JWT token is expired
 * @param {string} token - JWT token to check
 * @param {number} bufferSeconds - Buffer time in seconds to consider token as "soon to expire"
 * @returns {boolean} True if token is expired or invalid, false otherwise
 */
export function isTokenExpired(token, bufferSeconds = 0) {
  try {
    const decodedToken = decodeToken(token);
    if (!decodedToken || !decodedToken.exp) return true;
    
    // Get current time in seconds
    const currentTime = Math.floor(Date.now() / 1000);
    
    // Check if token is expired with buffer
    return decodedToken.exp < (currentTime + bufferSeconds);
  } catch (error) {
    console.error('Error checking token expiration:', error);
    return true;
  }
}

/**
 * Get time until token expiration in milliseconds
 * @param {string} token - JWT token to check
 * @returns {number} Time until expiration in milliseconds, or 0 if expired/invalid
 */
export function getTimeUntilExpiration(token) {
  try {
    const decodedToken = decodeToken(token);
    if (!decodedToken || !decodedToken.exp) return 0;
    
    // Get current time in seconds
    const currentTime = Math.floor(Date.now() / 1000);
    
    // Calculate time until expiration
    const timeUntilExpiration = decodedToken.exp - currentTime;
    
    // Return time in milliseconds, or 0 if already expired
    return Math.max(timeUntilExpiration * 1000, 0);
  } catch (error) {
    console.error('Error calculating token expiration time:', error);
    return 0;
  }
}

/**
 * Throttle a function to prevent excessive calls
 * @param {Function} func - The function to throttle
 * @param {number} limit - The minimum time between function calls in ms
 * @returns {Function} A throttled version of the function
 */
export function throttle(func, limit) {
  let inThrottle = false;
  
  return function(...args) {
    if (!inThrottle) {
      func.apply(this, args);
      inThrottle = true;
      setTimeout(() => inThrottle = false, limit);
    }
  };
}

/**
 * Store auth tokens securely
 * @param {string} accessToken - JWT access token
 * @param {string} refreshToken - JWT refresh token
 * @param {object} user - User object or data
 */
export function storeAuthTokens(accessToken, refreshToken, user = null) {
  if (accessToken) {
    localStorage.setItem('accessToken', accessToken);
  }
  
  if (refreshToken) {
    localStorage.setItem('refreshToken', refreshToken);
  }
  
  if (user) {
    localStorage.setItem('user', JSON.stringify(user));
    if (user.role) {
      localStorage.setItem('userRole', user.role);
    }
  }
}

/**
 * Clear all auth tokens and user data
 */
export function clearAuthTokens() {
  localStorage.removeItem('accessToken');
  localStorage.removeItem('refreshToken');
  localStorage.removeItem('user');
  localStorage.removeItem('userRole');
  localStorage.removeItem('walletAddress');
}

/**
 * Check if a user is authenticated based on tokens
 * @param {number} bufferSeconds - Buffer time in seconds to consider token as valid 
 * @returns {boolean} True if user has valid tokens
 */
export function isAuthenticated(bufferSeconds = 0) {
  const accessToken = localStorage.getItem('accessToken');
  const refreshToken = localStorage.getItem('refreshToken');
  
  if (!accessToken || !refreshToken) {
    return false;
  }
  
  // If access token is not expired yet, user is authenticated
  if (!isTokenExpired(accessToken, bufferSeconds)) {
    return true;
  }
  
  // If access token is expired but refresh token isn't, user can be re-authenticated
  return !isTokenExpired(refreshToken);
}

/**
 * Get token expiration status with more details
 * @param {string} token - JWT token to check
 * @returns {object} Status object with expired, expiresIn, and percentRemaining properties
 */
export function getTokenStatus(token) {
  try {
    const decodedToken = decodeToken(token);
    if (!decodedToken || !decodedToken.exp) {
      return { expired: true, expiresIn: 0, percentRemaining: 0 };
    }
    
    // Get current time in seconds
    const currentTime = Math.floor(Date.now() / 1000);
    
    // Calculate expiration details
    const isExpired = decodedToken.exp < currentTime;
    const expiresIn = Math.max(decodedToken.exp - currentTime, 0);
    
    // Calculate percentage of time remaining if we know issued time
    let percentRemaining = 0;
    if (decodedToken.iat) {
      const totalLifetime = decodedToken.exp - decodedToken.iat;
      const elapsed = currentTime - decodedToken.iat;
      percentRemaining = Math.max(0, Math.min(100, 100 - (elapsed / totalLifetime * 100)));
    }
    
    return {
      expired: isExpired,
      expiresIn, // seconds until expiration
      percentRemaining // percentage of lifetime remaining
    };
  } catch (error) {
    console.error('Error getting token status:', error);
    return { expired: true, expiresIn: 0, percentRemaining: 0 };
  }
}
