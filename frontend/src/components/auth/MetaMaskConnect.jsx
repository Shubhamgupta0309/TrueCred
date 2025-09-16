import React, { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import { useNavigate } from 'react-router-dom';

export default function MetaMaskConnect({ isDashboard = false }) {
  const [isConnected, setIsConnected] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  const [account, setAccount] = useState('');
  const [error, setError] = useState('');
  const { walletAuth, connectWallet, isAuthenticated, user } = useAuth();
  const navigate = useNavigate();

  // Check if MetaMask is already connected on component mount
  useEffect(() => {
    // Skip the auto authentication process if already authenticated and not in dashboard
    if (isAuthenticated && !isDashboard) {
      console.log('User is already authenticated and not in dashboard, skipping MetaMask connection check');
      return;
    }

    const checkConnection = async () => {
      if (!window.isMetaMaskAvailable()) {
        console.log('MetaMask is not installed');
        return;
      }

      try {
        // Check if we have access to accounts
        const accounts = await window.safeMetaMaskRequest('eth_accounts');
        if (accounts && accounts.length > 0) {
          setAccount(accounts[0]);
          setIsConnected(true);
          
          // In dashboard mode, we're just checking if connected, not authenticating
          if (isDashboard) {
            console.log('In dashboard mode, detected connected wallet:', accounts[0]);
            return;
          }
          
          // For authentication page: if there's a wallet address in localStorage, the user previously connected
          const storedWalletAddress = localStorage.getItem('walletAddress');
          // Only try to auto-login if we're not already authenticated
          if (storedWalletAddress === accounts[0] && !isAuthenticated) {
            // Auto-login with wallet if address matches - but only once
            handleWalletAuth(accounts[0]);
          }
        }
      } catch (err) {
        console.error('Error checking MetaMask connection:', err);
      setError('Error connecting to MetaMask. Please ensure MetaMask is installed and unlocked. ' + (err?.message || ''));
      }
    };

    checkConnection();
  }, [isAuthenticated, isDashboard]); // Add isDashboard to dependency array

  const handleWalletAuth = async (walletAddress) => {
    // Skip if already authenticated
    if (isAuthenticated) {
      console.log('User is already authenticated, skipping wallet authentication');
      return { success: true };
    }
    
    try {
      // Normalize the wallet address to lowercase to avoid case sensitivity issues
      const normalizedAddress = walletAddress.toLowerCase();
      console.log('Attempting wallet authentication with address:', normalizedAddress);
      const result = await walletAuth(normalizedAddress);
      if (result.success) {
        // Redirect based on role
        if (result.role === 'student') {
          navigate('/student-dashboard');
        } else if (result.role === 'college') {
          navigate('/college-dashboard');
        } else if (result.role === 'company') {
          navigate('/company-dashboard');
        } else {
          navigate('/student-dashboard'); // Default
        }
      } else {
        console.error('Wallet auth failed:', result.error);
        setError(result.error || 'Wallet authentication failed. This wallet may not be registered.');
      }
      return result;
    } catch (err) {
      console.error('Wallet auth error:', err);
      setError('Authentication failed. Please try again.');
      throw err;
    }
  };

  const handleConnect = async () => {
  setError('');
  // Prevent multiple concurrent connect flows from rapid clicks
  if (isConnecting) return;
    
    // If already authenticated but not in dashboard, redirect to the appropriate dashboard
    if (isAuthenticated && !isDashboard) {
      console.log('User is already authenticated and not in dashboard, redirecting to dashboard');
      if (user?.role === 'student') {
        navigate('/student-dashboard');
      } else if (user?.role === 'college') {
        navigate('/college-dashboard');
      } else if (user?.role === 'company') {
        navigate('/company-dashboard');
      } else {
        navigate('/student-dashboard'); // Default
      }
      return;
    }
    
    // If already connected, disconnect
    if (isConnected && !isDashboard) {
      setIsConnected(false);
      setAccount('');
      return;
    }

    // Check if MetaMask is installed
    if (!window.isMetaMaskAvailable()) {
      setError('MetaMask is not installed. Please install MetaMask to connect.');
      return;
    }

    setIsConnecting(true);

    try {
      // If the provider (or another tab) already has an eth_requestAccounts in progress, avoid duplicate request
      if (window && (window.__eth_request_promise || window.__eth_request_in_progress)) {
        setError('A wallet connection is already in progress. Please finish the existing MetaMask dialog or check the MetaMask extension and try again.');
        return;
      }

      // Request account access. The polyfill will retry a few times if the provider reports it's busy.
      const accounts = await window.safeMetaMaskRequest('eth_requestAccounts');
      
      if (accounts && accounts.length > 0) {
        const walletAddress = accounts[0];
        setAccount(walletAddress);
        setIsConnected(true);
        
        // If in dashboard or already authenticated, connect wallet to account
        if (isDashboard || isAuthenticated) {
          try {
            const success = await connectWallet(walletAddress);
            if (success) {
              // Show success message or update UI
              console.log('Wallet connected successfully to account');
            }
          } catch (err) {
            console.error('Error connecting wallet to account:', err);
            setError('Failed to connect wallet to your account. Please try again.');
          }
        } else {
          // Try to authenticate with wallet
          try {
            await handleWalletAuth(walletAddress);
          } catch (err) {
            console.error('Error authenticating with wallet:', err);
            setError('Wallet authentication failed. This wallet may not be registered.');
          }
        }
      } else {
        setError('No accounts found. Please check MetaMask.');
      }
    } catch (err) {
      console.error('Error connecting to MetaMask:', err);
      // User rejected the request
      if (err && (err.code === 4001 || (err.error && err.error.code === 4001))) {
        setError('MetaMask connection was rejected. Please approve the connection request.');
      } else if (err && (err.code === -32001 || (err.message && err.message.includes('timed out')))) {
        // Our polyfill timed out waiting for the provider to become available
        setError('MetaMask did not respond in time. Please check the MetaMask popup/extension and try again.');
      } else if (err && (err.code === -32002 || (err.message && err.message.includes('Already processing')))) {
        // Provider reports it's already processing eth_requestAccounts
        setError('MetaMask is already handling a connection request. Please finish the existing MetaMask dialog (check other tabs) and try again.');
      } else if (err && err.message) {
        setError(`Failed to connect to MetaMask: ${err.message}`);
      } else {
        setError('Failed to connect to MetaMask. Please try again.');
      }
    } finally {
      setIsConnecting(false);
    }
  };

  return (
    <div>
      <button
        onClick={handleConnect}
        disabled={isConnecting}
        className={`w-full flex items-center justify-center px-4 py-3 border-2 border-dashed rounded-lg transition-all duration-200 hover:border-purple-400 hover:bg-purple-50 ${
          isConnected ? 'border-green-400 bg-green-50 text-green-700' : 'border-gray-300 text-gray-600'
        } ${isConnecting ? 'opacity-75 cursor-not-allowed' : 'hover:shadow-md'}`}
      >
        <div className="flex items-center space-x-3">
          {/* MetaMask Fox Icon */}
          <div className="w-6 h-6 bg-gradient-to-br from-orange-400 to-orange-600 rounded-full flex items-center justify-center">
            <svg className="w-4 h-4 text-white" viewBox="0 0 35 33" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M32.9582 1L19.8241 10.7183L22.2667 5.3585L32.9582 1Z" fill="#E17726" stroke="#E17726" strokeWidth="0.25" strokeLinecap="round" strokeLinejoin="round"/>
              <path d="M2.04183 1L15.052 10.809L12.7333 5.35846L2.04183 1Z" fill="#E27625" stroke="#E27625" strokeWidth="0.25" strokeLinecap="round" strokeLinejoin="round"/>
              <path d="M28.2647 23.4894L24.7109 28.5973L32.2512 30.5635L34.3697 23.5999L28.2647 23.4894Z" fill="#E27625" stroke="#E27625" strokeWidth="0.25" strokeLinecap="round" strokeLinejoin="round"/>
              <path d="M0.652222 23.5999L2.7486 30.5635L10.2889 28.5973L6.75722 23.4894L0.652222 23.5999Z" fill="#E27625" stroke="#E27625" strokeWidth="0.25" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </div>
          
          <div className="text-left">
            <div className="font-medium">
              {isConnecting ? 'Connecting...' : isConnected ? 'Wallet Connected' : 'Connect MetaMask'}
            </div>
            <div className="text-xs opacity-75">
              {isConnecting ? 'Please wait...' : isConnected ? `${account.substring(0, 6)}...${account.substring(account.length - 4)}` : 'Login with MetaMask wallet'}
            </div>
          </div>
          
          {isConnecting && (
            <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-purple-600"></div>
          )}
          
          {isConnected && (
            <div className="w-3 h-3 bg-green-500 rounded-full"></div>
          )}
        </div>
      </button>
      
      {error && (
        <div className="mt-2 text-sm text-red-600">
          {error}
        </div>
      )}
    </div>
  );
}