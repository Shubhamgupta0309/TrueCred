// MetaMask compatibility polyfill
// This ensures proper handling of window.ethereum checks

// Define a safe check function for MetaMask
window.isMetaMaskAvailable = function() {
  return typeof window.ethereum !== 'undefined' && window.ethereum.isMetaMask;
};

// Define a safe request function to handle possible CSP issues
window.safeMetaMaskRequest = async function(method, params) {
  if (!window.isMetaMaskAvailable()) {
    throw new Error('MetaMask is not available');
  }
  
  try {
    return await window.ethereum.request({ method, params });
  } catch (error) {
    console.error('MetaMask request error:', error);
    throw error;
  }
};

console.log('MetaMask polyfill loaded');
