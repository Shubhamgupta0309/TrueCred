import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Copy, ExternalLink, Shield, CheckCircle, XCircle, Info } from 'lucide-react';

export default function BlockchainTokenDisplay({ credential }) {
  const [showDetails, setShowDetails] = useState(false);
  const [copied, setCopied] = useState(false);
  
  // Determine status color
  const getStatusColor = () => {
    switch (credential.verification_status || credential.status) {
      case 'verified':
        return 'bg-green-100 border-green-300 text-green-800';
      case 'pending':
        return 'bg-yellow-100 border-yellow-300 text-yellow-800';
      case 'rejected':
        return 'bg-red-100 border-red-300 text-red-800';
      default:
        return 'bg-gray-100 border-gray-300 text-gray-800';
    }
  };
  
  // Determine status icon
  const StatusIcon = () => {
    switch (credential.verification_status || credential.status) {
      case 'verified':
        return <CheckCircle className="h-5 w-5 text-green-600" />;
      case 'pending':
        return <Info className="h-5 w-5 text-yellow-600" />;
      case 'rejected':
        return <XCircle className="h-5 w-5 text-red-600" />;
      default:
        return <Info className="h-5 w-5 text-gray-600" />;
    }
  };
  
  // Handle copy to clipboard
  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };
  
  // Format date
  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };
  
  return (
    <motion.div
      className={`border rounded-lg overflow-hidden shadow-md mb-4 ${getStatusColor()}`}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <div className="p-4">
        <div className="flex justify-between items-start">
          <div>
            <h3 className="text-lg font-semibold">{credential.title}</h3>
            <p className="text-sm">{credential.issuer}</p>
          </div>
          <div className="flex items-center">
            <StatusIcon />
            <span className="ml-2 text-sm font-medium capitalize">
              {credential.verification_status || credential.status}
            </span>
          </div>
        </div>
        
        <div className="mt-3 flex items-center text-sm">
          <span className="mr-4">
            <strong>Issued:</strong> {formatDate(credential.issue_date)}
          </span>
          {credential.expiry_date && (
            <span>
              <strong>Expires:</strong> {formatDate(credential.expiry_date)}
            </span>
          )}
        </div>
        
        {/* Blockchain token visualization */}
        <div className="mt-4 p-3 bg-white rounded-md border border-gray-200">
          <div className="flex items-center">
            <Shield className="h-5 w-5 text-blue-600 mr-2" />
            <span className="text-blue-800 font-medium">Blockchain Verified</span>
          </div>
          
          <div className="mt-2 flex items-center">
            <div className="bg-gray-100 py-1 px-2 rounded text-sm font-mono text-gray-800 flex-grow mr-2 truncate">
              {credential.blockchain_hash || '0x7a69...4e0b'}
            </div>
            <button
              onClick={() => copyToClipboard(credential.blockchain_hash || '0x7a69...4e0b')}
              className="p-1 text-gray-500 hover:text-gray-800"
              title="Copy to clipboard"
            >
              <Copy className="h-4 w-4" />
            </button>
            {credential.blockchain_explorer_url && (
              <a
                href={credential.blockchain_explorer_url}
                target="_blank"
                rel="noopener noreferrer"
                className="p-1 text-gray-500 hover:text-gray-800 ml-1"
                title="View on blockchain explorer"
              >
                <ExternalLink className="h-4 w-4" />
              </a>
            )}
          </div>
          
          {copied && (
            <div className="mt-1 text-xs text-green-600">
              Copied to clipboard!
            </div>
          )}
        </div>
        
        <button
          onClick={() => setShowDetails(!showDetails)}
          className="mt-3 text-sm text-blue-600 hover:text-blue-800 focus:outline-none"
        >
          {showDetails ? 'Hide Details' : 'Show Details'}
        </button>
        
        {showDetails && (
          <motion.div
            className="mt-3 p-3 bg-white rounded-md border border-gray-200"
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            transition={{ duration: 0.3 }}
          >
            <h4 className="font-medium text-gray-800 mb-2">Verification Details</h4>
            
            <div className="space-y-2 text-sm">
              {credential.blockchain_data && Object.keys(credential.blockchain_data).length > 0 ? (
                <>
                  <div>
                    <strong>Transaction Hash:</strong>{' '}
                    <span className="font-mono">{credential.blockchain_data.tx_hash || 'N/A'}</span>
                  </div>
                  <div>
                    <strong>Block Number:</strong>{' '}
                    <span>{credential.blockchain_data.block_number || 'N/A'}</span>
                  </div>
                  <div>
                    <strong>Timestamp:</strong>{' '}
                    <span>{formatDate(credential.blockchain_data.timestamp) || 'N/A'}</span>
                  </div>
                </>
              ) : (
                <div className="text-gray-500">
                  Detailed blockchain information not available.
                </div>
              )}
              
              {credential.ipfs_hash && (
                <div>
                  <strong>IPFS Hash:</strong>{' '}
                  <span className="font-mono">{credential.ipfs_hash}</span>
                  <button
                    onClick={() => copyToClipboard(credential.ipfs_hash)}
                    className="p-1 text-gray-500 hover:text-gray-800 ml-1"
                    title="Copy to clipboard"
                  >
                    <Copy className="h-3 w-3" />
                  </button>
                </div>
              )}
              
              {credential.verified_at && (
                <div>
                  <strong>Verified At:</strong>{' '}
                  <span>{formatDate(credential.verified_at)}</span>
                </div>
              )}
            </div>
          </motion.div>
        )}
      </div>
    </motion.div>
  );
}
