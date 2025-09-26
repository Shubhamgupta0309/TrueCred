import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';

// This is a development-only tool to help test the email verification flow
export default function TestVerificationLinks() {
  const [email, setEmail] = useState('');
  const [token, setToken] = useState('');
  const [generatedLink, setGeneratedLink] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  const handleGenerateLink = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    
    try {
      // This is a development-only endpoint that would not exist in production
      // It simulates getting a verification token for a specific email without actually sending an email
      const response = await fetch('http://localhost:5000/api/dev/get-verification-token', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email }),
      });
      
      const data = await response.json();
      
      if (response.ok && data.token) {
        setToken(data.token);
        setGeneratedLink(`/verify-email?token=${data.token}`);
      } else {
        setError(data.message || 'Failed to generate verification link');
      }
    } catch (err) {
      console.error('Error:', err);
      setError('An error occurred. Please try again.');
    } finally {
      setLoading(false);
    }
  };
  
  // For manual testing
  const handleManualTokenChange = (e) => {
    const newToken = e.target.value;
    setToken(newToken);
    if (newToken) {
      setGeneratedLink(`/verify-email?token=${newToken}`);
    } else {
      setGeneratedLink('');
    }
  };
  
  return (
    <div className="p-6 max-w-md mx-auto bg-white rounded-xl shadow-md">
      <h2 className="text-xl font-semibold text-gray-700 mb-4">Email Verification Test Tool</h2>
      <p className="text-sm text-gray-500 mb-4">
        This tool is for development purposes only to help test the email verification flow.
      </p>
      
      <div className="mb-6">
        <h3 className="font-medium mb-2">Option 1: Generate Link for Email</h3>
        <form onSubmit={handleGenerateLink} className="space-y-4">
          <div>
            <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
              Email Address
            </label>
            <input
              type="email"
              id="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
              placeholder="user@example.com"
              required
            />
          </div>
          
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-purple-600 text-white py-2 rounded-md hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-offset-2 disabled:opacity-50"
          >
            {loading ? 'Generating...' : 'Generate Verification Link'}
          </button>
        </form>
        
        {error && (
          <div className="mt-2 text-sm text-red-600">
            {error}
          </div>
        )}
      </div>
      
      <div className="mb-6">
        <h3 className="font-medium mb-2">Option 2: Enter Token Manually</h3>
        <div className="space-y-4">
          <div>
            <label htmlFor="token" className="block text-sm font-medium text-gray-700 mb-1">
              Verification Token
            </label>
            <input
              type="text"
              id="token"
              value={token}
              onChange={handleManualTokenChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
              placeholder="Enter token from backend logs"
            />
          </div>
        </div>
      </div>
      
      {generatedLink && (
        <div className="p-4 bg-gray-50 rounded-md">
          <h3 className="font-medium mb-2">Verification Link:</h3>
          <div className="bg-gray-100 p-2 rounded break-all mb-3">
            {generatedLink}
          </div>
          <Link
            to={generatedLink}
            className="inline-block bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2"
          >
            Open Verification Link
          </Link>
        </div>
      )}
      
      <div className="mt-6 text-xs text-gray-500">
        <p>Note: In a production environment, verification links would be sent to the user's email.</p>
      </div>
    </div>
  );
}
