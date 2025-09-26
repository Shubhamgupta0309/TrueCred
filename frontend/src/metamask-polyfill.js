// MetaMask compatibility polyfill
// This ensures proper handling of window.ethereum checks

// Define a safe check function for MetaMask
window.isMetaMaskAvailable = function() {
  // Accept any injected provider that exposes the request method.
  // Some wallets may not set `isMetaMask` but still provide the Ethereum provider API.
  return typeof window !== 'undefined' && typeof window.ethereum !== 'undefined' && typeof window.ethereum.request === 'function';
};

// Define a safe request function to handle possible CSP issues
window.safeMetaMaskRequest = async function(method, params) {
  if (!window.isMetaMaskAvailable()) {
    throw new Error('MetaMask is not available');
  }

  // Initialize a global lock flag for eth_requestAccounts to avoid concurrent calls
  if (typeof window.__eth_request_in_progress === 'undefined') {
    window.__eth_request_in_progress = false;
  }

  // If another eth_requestAccounts is already in progress, wait briefly for it to finish.
  // This handles double-clicks, React StrictMode double-invocation in dev, or simultaneous UI instances.
  // Instead of failing immediately, attempt a short retry loop when another request is in progress or
  // when the provider responds with the known -32002 "Already processing" error.
  const defaultWaitMs = 5000; // total time to keep retrying/waiting
  const pollInterval = 250;

  const waitForClear = async () => {
    const start = Date.now();
    while (window.__eth_request_in_progress && (Date.now() - start) < defaultWaitMs) {
      // eslint-disable-next-line no-await-in-loop
      await new Promise(resolve => setTimeout(resolve, pollInterval));
    }
    return !window.__eth_request_in_progress;
  };

  // We'll attempt to call the provider and retry if it reports "Already processing eth_requestAccounts"
  // (code -32002). This can happen if the extension UI is open or another tab initiated the request.
  const timeoutMs = defaultWaitMs;

  // For eth_requestAccounts we use a promise-based lock so concurrent callers share the same request
  // and we avoid invoking provider.request multiple times which often triggers -32002.
  if (method === 'eth_requestAccounts') {
    // If another caller already started a request, reuse that promise
    if (window.__eth_request_promise) {
      return await window.__eth_request_promise;
    }

    const p = (async () => {
      const attemptStart = Date.now();
      let lastError;

      while ((Date.now() - attemptStart) < timeoutMs) {
        try {
          const result = await window.ethereum.request({ method, params });
          return result;
        } catch (error) {
          lastError = error;
          const code = (error && (error.code || (error.error && error.error.code)));
          const message = (error && (error.message || (error.error && error.error.message))) || '';
          const numCode = typeof code === 'string' ? Number(code) : code;

          // If provider explicitly says it's already processing, wait and retry
          if (numCode === -32002 || message.includes('Already processing')) {
            // eslint-disable-next-line no-await-in-loop
            await new Promise(resolve => setTimeout(resolve, pollInterval));
            continue;
          }

          // Other errors: rethrow
          console.error('MetaMask request error (non-retry):', error);
          throw error;
        }
      }

      const msg = 'MetaMask request timed out while waiting for user/extension response.';
      const e = new Error(msg + (lastError ? ` Last error: ${lastError.message || lastError}` : ''));
      e.code = -32001;
      throw e;
    })();

    // store the promise and ensure it's cleared when done
    window.__eth_request_promise = p;
    try {
      return await p;
    } finally {
      try { delete window.__eth_request_promise; } catch (_) { window.__eth_request_promise = undefined; }
    }
  }

  // For other methods just call through
  return await window.ethereum.request({ method, params });
};

console.log('MetaMask polyfill loaded');
