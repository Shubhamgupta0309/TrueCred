import React, { useState } from 'react';

export default function MetaMaskConnect() {
  const [isConnected, setIsConnected] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);

  const handleConnect = async () => {
    setIsConnecting(true);
    
    // Simulate MetaMask connection (replace with actual MetaMask integration later)
    setTimeout(() => {
      setIsConnected(!isConnected);
      setIsConnecting(false);
    }, 1500);
  };

  return (
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
          <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 24 24">
            <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
            <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
            <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
            <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
          </svg>
        </div>
        
        <div className="text-left">
          <div className="font-medium">
            {isConnecting ? 'Connecting...' : isConnected ? 'Wallet Connected' : 'Connect MetaMask'}
          </div>
          <div className="text-xs opacity-75">
            {isConnecting ? 'Please wait...' : isConnected ? 'Ready for Web3' : 'For blockchain features'}
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
  );
}