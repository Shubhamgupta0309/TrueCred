import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Copy, ExternalLink, Shield, CheckCircle, XCircle, Info, RefreshCw } from 'lucide-react';
import { credentialService } from '../../services/api';

export default function BlockchainTokenDisplay({ credential, onVerificationUpdate }) {
  const [showDetails, setShowDetails] = useState(false);
  const [copied, setCopied] = useState(false);
  const [verifying, setVerifying] = useState(false);
  const [verificationResult, setVerificationResult] = useState(null);
  
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

  // Compute canonical tx hash to display/copy (prefer top-level, then nested)
  const displayTxFull = credential.blockchain_tx_hash || credential.blockchain_data?.tx_hash || null;
  const displayTxShort = displayTxFull ? `${displayTxFull.substring(0, 12)}...` : 'N/A';

  // Handle blockchain verification
  const handleVerifyOnBlockchain = async () => {
    setVerifying(true);
    setVerificationResult(null);
    
    try {
      const response = await credentialService.verifyCredentialBlockchain(credential.id);
      
      if (response.data && response.data.success) {
        setVerificationResult({
          success: true,
          message: 'Credential verified on blockchain!',
          data: response.data.data
        });
        
        // Update the credential status if callback provided
        if (onVerificationUpdate) {
          onVerificationUpdate(credential.id, 'verified', response.data.data);
        }
      } else {
        setVerificationResult({
          success: false,
          message: response.data?.message || 'Verification failed'
        });
      }
    } catch (error) {
      console.error('Blockchain verification error:', error);
      setVerificationResult({
        success: false,
        message: error.response?.data?.message || 'Failed to verify credential on blockchain'
      });
    } finally {
      setVerifying(false);
    }
  };
  
  // Format date (defensive): accepts ISO strings, numeric strings, or unix timestamps
  // If a numeric timestamp appears to be in seconds (< 1e12) convert to ms.
  const formatDate = (value) => {
    if (value === undefined || value === null || value === '') return 'N/A';

    // Normalize numeric strings
    let ts = value;
    if (typeof ts === 'string') {
      // If it's an all-digits string, treat as timestamp
      if (/^\d+$/.test(ts)) {
        ts = parseInt(ts, 10);
      }
    }

    let dateObj;
    if (typeof ts === 'number') {
      // If timestamp looks like seconds (typical for blockchain), convert to ms
      if (ts < 1e12) {
        ts = ts * 1000;
      }
      dateObj = new Date(ts);
    } else {
      // Fallback: let Date parse ISO strings or other formats
      dateObj = new Date(ts);
    }

    if (Number.isNaN(dateObj.getTime())) return 'N/A';

    return dateObj.toLocaleDateString('en-US', {
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
              {displayTxShort}
            </div>
            <button
              onClick={() => copyToClipboard(displayTxFull || '')}
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
            <button
              onClick={handleVerifyOnBlockchain}
              disabled={verifying}
              className="p-1 text-gray-500 hover:text-blue-600 ml-1 disabled:opacity-50 disabled:cursor-not-allowed"
              title="Verify on blockchain"
            >
              <RefreshCw className={`h-4 w-4 ${verifying ? 'animate-spin' : ''}`} />
            </button>
          </div>
          
          {copied && (
            <div className="mt-1 text-xs text-green-600">
              Copied to clipboard!
            </div>
          )}
          
          {verificationResult && (
            <div className={`mt-1 text-xs ${verificationResult.success ? 'text-green-600' : 'text-red-600'}`}>
              {verificationResult.message}
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
                  <button
                    onClick={() => {
                      try {
                        const h = credential.ipfs_hash;
                        if (!h) return window.alert('No IPFS hash available');
                        const url = String(h).startsWith('http')
                          ? String(h)
                          : (String(h).startsWith('ipfs://') ? `http://localhost:8080/ipfs/${String(h).replace('ipfs://','')}` : `http://localhost:8080/ipfs/${h}`);
                        window.open(url, '_blank', 'noopener');
                      } catch (e) {
                        console.error('Failed to open IPFS document', e);
                        window.alert('Failed to open document. See console for details.');
                      }
                    }}
                    className="p-1 text-gray-500 hover:text-blue-600 ml-2"
                    title="View document"
                  >
                    View Document
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
