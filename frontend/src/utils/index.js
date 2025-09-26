/**
 * Utility functions for the TrueCred frontend
 */

/**
 * Creates a URL for a page based on the role
 * @param {string} role - The user role (student, college, company)
 * @returns {string} The URL for the dashboard page
 */
export const createPageUrl = (role) => {
  switch (role) {
    case 'student':
      return '/student-dashboard';
    case 'college':
      return '/college-dashboard';
    case 'company':
      return '/company-dashboard';
    default:
      return '/student-dashboard'; // Default to student dashboard
  }
};

/**
 * Formats a date string into a more readable format
 * @param {string} dateString - ISO date string
 * @returns {string} Formatted date string
 */
export const formatDate = (dateString) => {
  const options = { year: 'numeric', month: 'long', day: 'numeric' };
  return new Date(dateString).toLocaleDateString(undefined, options);
};

/**
 * Truncates a string to a specified length and adds ellipsis
 * @param {string} text - Text to truncate
 * @param {number} length - Maximum length
 * @returns {string} Truncated text
 */
export const truncateText = (text, length = 100) => {
  if (!text) return '';
  if (text.length <= length) return text;
  return text.slice(0, length) + '...';
};

/**
 * Checks if a JWT token is expired
 * @param {string} token - JWT token
 * @returns {boolean} True if token is expired
 */
export const isTokenExpired = (token) => {
  if (!token) return true;

  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    return payload.exp * 1000 < Date.now();
  } catch (e) {
    return true;
  }
};
