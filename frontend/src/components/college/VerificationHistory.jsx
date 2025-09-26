import React from 'react';
import { motion } from 'framer-motion';
import StatusBadge from '../dashboard/StatusBadge';
import { History, Calendar, Shield, CheckCircle, XCircle } from 'lucide-react';

export default function VerificationHistory({ history }) {
  // Helper function to get blockchain status icon
  const getBlockchainIcon = (item) => {
    // Check if the item has blockchain data
    if (item.blockchain_tx_hash || item.blockchain_data?.tx_hash) {
      return <CheckCircle className="w-4 h-4 text-green-600" title="Blockchain Verified" />;
    } else if (item.status === 'verified' || item.status === 'issued') {
      return <Shield className="w-4 h-4 text-gray-400" title="Not on Blockchain" />;
    } else {
      return <XCircle className="w-4 h-4 text-red-400" title="Not Verified" />;
    }
  };

  return (
    <div className="bg-white rounded-2xl shadow-lg shadow-purple-500/10 p-6">
      <h3 className="text-lg font-bold text-gray-800 mb-4 flex items-center gap-2">
        <History className="w-5 h-5 text-purple-600" />
        Verification History
      </h3>
      <div className="space-y-3 max-h-72 overflow-y-auto pr-2">
        {history.slice().reverse().map((item, index) => (
          <motion.div
            key={item.id}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.3, delay: index * 0.1 }}
            className="border border-gray-100 rounded-lg p-3"
          >
            <div className="flex justify-between items-center">
              <div className="flex-1">
                <p className="font-medium text-sm text-gray-700">{item.credentialTitle}</p>
                <p className="text-xs text-gray-500">Student: {item.studentName}</p>
              </div>
              <div className="text-right flex items-center gap-2">
                {getBlockchainIcon(item)}
                <div>
                  <StatusBadge status={item.status} />
                  <p className="text-xs text-gray-400 mt-1 flex items-center justify-end gap-1">
                      <Calendar className="w-3 h-3"/> {item.actionDate}
                  </p>
                </div>
              </div>
            </div>
            
            {/* Show blockchain transaction hash if available */}
            {(item.blockchain_tx_hash || item.blockchain_data?.tx_hash) && (
              <div className="mt-2 pt-2 border-t border-gray-100">
                <p className="text-xs text-gray-500 flex items-center gap-1">
                  <Shield className="w-3 h-3" />
                  TX: {(item.blockchain_tx_hash || item.blockchain_data?.tx_hash).substring(0, 10)}...
                </p>
              </div>
            )}
          </motion.div>
        ))}
      </div>
    </div>
  );
}