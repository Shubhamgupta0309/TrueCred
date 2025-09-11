import React, { useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import { useNavigate } from 'react-router-dom';

export default function ManualWalletInput() {
  const [walletAddress, setWalletAddress] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const { walletAuth, isAuthenticated, user } = useAuth();
  const navigate = useNavigate();

  // If user is already authenticated, don't show the component
  if (isAuthenticated) {
    return null;
  }

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    
    // Don't proceed if already authenticated
    if (isAuthenticated) {
      console.log('User is already authenticated, skipping wallet auth');
      navigate('/student-dashboard');
      return;
    }
    
    // Basic validation
    if (!walletAddress || walletAddress.trim() === '') {
      setError('Please enter a wallet address');
      return;
    }
    
    // Simple Ethereum address format validation (0x followed by 40 hex characters)
    const addressRegex = /^0x[a-fA-F0-9]{40}$/;
    if (!addressRegex.test(walletAddress)) {
      setError('Please enter a valid Ethereum wallet address (0x followed by 40 hexadecimal characters)');
      return;
    }
    
    setIsSubmitting(true);
    
    try {
      // Normalize the wallet address to lowercase to avoid case sensitivity issues
      const normalizedAddress = walletAddress.toLowerCase();
      const result = await walletAuth(normalizedAddress);
      
      if (result.success) {
        setSuccess('Authentication successful! Redirecting...');
        
        // Store wallet address in localStorage
        localStorage.setItem('walletAddress', normalizedAddress);
        
        // Redirect based on role
        setTimeout(() => {
          if (result.role === 'student') {
            navigate('/student-dashboard');
          } else if (result.role === 'college') {
            navigate('/college-dashboard');
          } else if (result.role === 'company') {
            navigate('/company-dashboard');
          } else {
            navigate('/student-dashboard'); // Default
          }
        }, 1500);
      } else {
        setError(result.error || 'Wallet authentication failed. This wallet may not be registered.');
      }
    } catch (err) {
      console.error('Manual wallet auth error:', err);
      setError('Authentication failed. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="mt-4">
      <div className="text-sm text-gray-600 mb-2">
        Login with your registered wallet address:
      </div>
      
      <form onSubmit={handleSubmit} className="space-y-2">
        <div className="flex flex-col">
          <label htmlFor="walletAddress" className="text-sm text-gray-700 mb-1">
            Wallet Address
          </label>
          <div className="flex">
            <input
              type="text"
              id="walletAddress"
              name="walletAddress"
              value={walletAddress}
              onChange={(e) => setWalletAddress(e.target.value)}
              placeholder="0x..."
              autoComplete="off"
              className="flex-1 px-3 py-2 border border-gray-300 rounded-l-md focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            />
            <button
              type="submit"
              id="connectWalletBtn"
              name="connectWalletBtn"
              disabled={isSubmitting}
              className="bg-purple-600 text-white px-4 py-2 rounded-r-md hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {isSubmitting ? 'Connecting...' : 'Connect'}
            </button>
          </div>
        </div>
        
        {error && (
          <div className="text-sm text-red-600">
            {error}
          </div>
        )}
        
        {success && (
          <div className="text-sm text-green-600">
            {success}
          </div>
        )}
      </form>
    </div>
  );
}
