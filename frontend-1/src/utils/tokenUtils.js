/**
 * Simple utility functions for JWT token handling
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
 * @returns {boolean} True if token is expired or invalid, false otherwise
 */
export function isTokenExpired(token) {
  try {
    const decodedToken = decodeToken(token);
    if (!decodedToken || !decodedToken.exp) return true;
    
    // Get current time in seconds
    const currentTime = Math.floor(Date.now() / 1000);
    
    // Check if token is expired
    return decodedToken.exp < currentTime;
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
