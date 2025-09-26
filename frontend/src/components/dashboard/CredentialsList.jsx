import React, { useState } from 'react';
import { motion } from 'framer-motion';
import StatusBadge from './StatusBadge';
import { FileText, Calendar, Eye, RefreshCw, CheckCircle2 } from 'lucide-react';
import { credentialService } from '../../services/api';

export default function CredentialsList({ credentials, onVerificationUpdate }) {
  const [verifyingId, setVerifyingId] = useState(null);
  const [verificationResults, setVerificationResults] = useState({});
  const [selectedCredential, setSelectedCredential] = useState(null);

  // Filter to show only verified credentials
  const verifiedCredentials = credentials.filter(cred => 
    cred.status === 'Verified' || cred.status === 'verified' || cred.status === 'issued' || cred.verified === true
  );

  // Handle blockchain verification
  const handleVerifyOnBlockchain = async (credentialId) => {
    setVerifyingId(credentialId);
    setVerificationResults(prev => ({ ...prev, [credentialId]: null }));
    
    try {
      const response = await credentialService.verifyCredentialBlockchain(credentialId);
      
      if (response.data && response.data.success) {
        setVerificationResults(prev => ({
          ...prev,
          [credentialId]: {
            success: true,
            message: 'Credential verified on blockchain!',
            data: response.data.data
          }
        }));
        
        // Update the credential status if callback provided
        if (onVerificationUpdate) {
          onVerificationUpdate(credentialId, 'verified', response.data.data);
        }
      } else {
        setVerificationResults(prev => ({
          ...prev,
          [credentialId]: {
            success: false,
            message: response.data?.message || 'Verification failed'
          }
        }));
      }
    } catch (error) {
      console.error('Blockchain verification error:', error);
      setVerificationResults(prev => ({
        ...prev,
        [credentialId]: {
          success: false,
          message: error.response?.data?.message || 'Failed to verify credential on blockchain'
        }
      }));
    } finally {
      setVerifyingId(null);
    }
  };
  return (
    <div className="bg-white rounded-2xl shadow-lg shadow-purple-500/10 p-6">
      <h3 className="text-lg font-bold text-gray-800 mb-4 flex items-center gap-2">
        <FileText className="w-5 h-5 text-purple-600" />
        My Credentials ({verifiedCredentials.length})
      </h3>
      <div className="space-y-4 max-h-80 overflow-y-auto pr-2">
        {verifiedCredentials.length === 0 ? (
          <div className="text-gray-500 text-center py-8">
            <CheckCircle2 className="w-12 h-12 mx-auto mb-4 text-gray-300" />
            <p>No verified credentials yet.</p>
            <p className="text-sm mt-2">Your approved credentials will appear here.</p>
          </div>
        ) : (
          verifiedCredentials.map((cred, index) => (
            <motion.div
              key={cred.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.3, delay: index * 0.1 }}
              className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 hover:shadow-md transition-all duration-200 cursor-pointer"
            >
              <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2">
                <div className="flex items-center gap-3">
                  <CheckCircle2 className="w-5 h-5 text-green-600 flex-shrink-0" />
                  <div>
                    <p className="font-semibold text-gray-800">{cred.title}</p>
                    <p className="text-sm text-gray-500 flex items-center gap-2 mt-1">
                      <Calendar className="w-4 h-4" />
                      Verified on {cred.date ? (new Date(cred.date).toLocaleDateString()) : 'Unknown'}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-4 mt-2 sm:mt-0">
                  <motion.button
                    whileHover={{ scale: 1.1 }}
                    whileTap={{ scale: 0.9 }}
                    onClick={() => handleVerifyOnBlockchain(cred.id)}
                    disabled={verifyingId === cred.id}
                    className="p-2 text-gray-500 hover:text-blue-600 hover:bg-blue-100 rounded-full disabled:opacity-50 disabled:cursor-not-allowed"
                    title="Verify on blockchain"
                  >
                    <RefreshCw className={`w-5 h-5 ${verifyingId === cred.id ? 'animate-spin' : ''}`} />
                  </motion.button>
                  <motion.button
                    whileHover={{ scale: 1.1 }}
                    whileTap={{ scale: 0.9 }}
                    className="p-2 text-gray-500 hover:text-purple-600 hover:bg-purple-100 rounded-full"
                    title="View Details"
                    onClick={(e) => {
                      e.stopPropagation();
                      setSelectedCredential(cred);
                    }}
                  >
                    <Eye className="w-5 h-5" />
                  </motion.button>
                </div>
              </div>
              
              {verificationResults[cred.id] && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  className={`mt-2 p-2 rounded text-sm ${
                    verificationResults[cred.id].success 
                      ? 'bg-green-50 text-green-700 border border-green-200' 
                      : 'bg-red-50 text-red-700 border border-red-200'
                  }`}
                >
                  {verificationResults[cred.id].message}
                </motion.div>
              )}
            </motion.div>
          ))
        )}
      </div>
  
      {/* Credential Details Modal */}
      {selectedCredential && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[80vh] overflow-y-auto"
          >
            <div className="p-6">
              <div className="flex justify-between items-start mb-4">
                <h2 className="text-2xl font-bold text-gray-800">{selectedCredential.title}</h2>
                <button
                  onClick={() => setSelectedCredential(null)}
                  className="text-gray-500 hover:text-gray-700 text-2xl"
                >
                  ×
                </button>
              </div>

              <div className="space-y-4">
                <div className="flex items-center gap-2">
                  <span className={`px-3 py-1 rounded-full text-sm font-medium ${selectedCredential.verified ? 'text-green-600 bg-green-100' : 'text-gray-600 bg-gray-100'}`}>
                    {selectedCredential.verified ? 'Verified' : (selectedCredential.pending_verification ? 'Pending' : 'Not Verified')}
                  </span>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <h3 className="font-semibold text-gray-700 mb-2">Basic Information</h3>
                    <div className="space-y-2 text-sm">
                      <p><span className="font-medium">Issuer:</span> {selectedCredential.issuer}</p>
                      <p><span className="font-medium">Type:</span> {selectedCredential.type || 'Not specified'}</p>
                      <p><span className="font-medium">Document URL:</span> {selectedCredential.document_url || selectedCredential.ipfs_hash || 'Not available'}</p>
                    </div>
                  </div>

                  <div>
                    <h3 className="font-semibold text-gray-700 mb-2">Dates</h3>
                    <div className="space-y-2 text-sm">
                      <p><span className="font-medium">Issued:</span> {selectedCredential.issue_date ? new Date(selectedCredential.issue_date).toLocaleDateString() : 'Unknown'}</p>
                      <p><span className="font-medium">Verified At:</span> {selectedCredential.verified_at ? new Date(selectedCredential.verified_at).toLocaleString() : 'N/A'}</p>
                    </div>
                  </div>
                </div>

                {selectedCredential.description && (
                  <div>
                    <h3 className="font-semibold text-gray-700 mb-2">Description</h3>
                    <p className="text-sm text-gray-600 bg-gray-50 p-3 rounded-lg">{selectedCredential.description}</p>
                  </div>
                )}

                {/* Verification Details */}
                {(selectedCredential.blockchain_data || selectedCredential.blockchain_tx_hash) && (
                  <div>
                    <h3 className="font-semibold text-gray-700 mb-2">Verification Details</h3>
                    <div className="space-y-2 text-sm">
                      <p><span className="font-medium">Transaction Hash:</span> {selectedCredential.blockchain_data?.tx_hash || selectedCredential.blockchain_tx_hash || 'N/A'}</p>
                      <p><span className="font-medium">Block Number:</span> {selectedCredential.blockchain_data?.block_number || selectedCredential.block_number || 'N/A'}</p>
                      <p><span className="font-medium">Timestamp:</span> {selectedCredential.blockchain_data?.timestamp ? new Date(selectedCredential.blockchain_data.timestamp).toLocaleString() : 'N/A'}</p>
                    </div>
                  </div>
                )}

                {/* Documents */}
                <div>
                  <h3 className="font-semibold text-gray-700 mb-2">Documents</h3>
                  <div className="space-y-2">
                    {
                      (() => {
                        // helper to normalize/build URLs
                        const buildDocUrl = (val) => {
                          if (!val) return null;
                          const s = String(val);
                          if (s.startsWith('http://') || s.startsWith('https://')) return s;
                          if (s.startsWith('ipfs://')) return `http://localhost:8080/ipfs/${s.replace('ipfs://','')}`;
                          return `http://localhost:8080/ipfs/${s}`;
                        };

                        // friendly filename extractor
                        const filenameFromUrl = (u) => {
                          try {
                            const parts = new URL(u).pathname.split('/').filter(Boolean);
                            const last = parts[parts.length - 1];
                            return last || u;
                          } catch (e) {
                            return u;
                          }
                        };

                        const docsMap = new Map();

                        // add explicit document_url
                        if (selectedCredential.document_url) {
                          const url = buildDocUrl(selectedCredential.document_url);
                          if (url) docsMap.set(url, { label: 'Document', url, filename: filenameFromUrl(url) });
                        }

                        // add ipfs_hash if present
                        if (selectedCredential.ipfs_hash) {
                          const url = buildDocUrl(selectedCredential.ipfs_hash);
                          if (url) docsMap.set(url, { label: 'IPFS', url, filename: filenameFromUrl(url) });
                        }

                        // add any document_hashes entries
                        if (selectedCredential.document_hashes) {
                          Object.entries(selectedCredential.document_hashes).forEach(([name, hash]) => {
                            const url = buildDocUrl(hash);
                            if (url) docsMap.set(url, { label: name || 'Document', url, filename: name || filenameFromUrl(url) });
                          });
                        }

                        // attachments
                        if (selectedCredential.attachments && selectedCredential.attachments.length > 0) {
                          selectedCredential.attachments.forEach((a, idx) => {
                            const raw = a.uri || a.url || a.document_url || a.hash || a.document_hash;
                            const url = buildDocUrl(raw);
                            const name = a.filename || a.name || `attachment-${idx+1}`;
                            if (url) docsMap.set(url, { label: name, url, filename: name });
                          });
                        }

                        // render unique documents
                        const items = Array.from(docsMap.values());
                        if (items.length === 0) {
                          return (<div className="text-gray-500">No documents available.</div>);
                        }

                        return items.map((d) => (
                          <div key={d.url} className="flex items-center gap-2 p-2 bg-gray-50 rounded-lg">
                            <span className="text-sm font-medium">{d.filename || d.label}</span>
                            <a href={d.url} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:text-blue-800 text-sm underline">View Document</a>
                          </div>
                        ));
                      })()
                    }
                  </div>
                </div>

              </div>
            </div>
          </motion.div>
        </div>
      )}
    </div>
  );
}