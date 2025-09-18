import React, { useState } from 'react';
import { motion } from 'framer-motion';
import StatusBadge from './StatusBadge';
import { FileText, Calendar, Eye, RefreshCw } from 'lucide-react';
import { credentialService } from '../../services/api';

export default function CredentialsList({ credentials, onVerificationUpdate }) {
  const [verifyingId, setVerifyingId] = useState(null);
  const [verificationResults, setVerificationResults] = useState({});

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
        My Credentials
      </h3>
      <div className="space-y-4 max-h-80 overflow-y-auto pr-2">
        {credentials.map((cred, index) => (
          <motion.div
            key={cred.id}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.3, delay: index * 0.1 }}
            className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 hover:shadow-md transition-all duration-200"
          >
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2">
              <div>
                <p className="font-semibold text-gray-800">{cred.title}</p>
                <p className="text-sm text-gray-500 flex items-center gap-2 mt-1">
                  <Calendar className="w-4 h-4" />
                  Submitted on {cred.date ? (new Date(cred.date).toLocaleDateString()) : 'Unknown'}
                </p>
              </div>
              <div className="flex items-center gap-4 mt-2 sm:mt-0">
                <StatusBadge status={cred.status} />
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
        ))}
      </div>
    </div>
  );
}