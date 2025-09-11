import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Check, X, FileText, Loader2, Calendar, School } from 'lucide-react';

export default function PendingExperienceRequests({ requests, onAction }) {
  const [processingId, setProcessingId] = useState(null);

  const handleAction = (id, status) => {
    setProcessingId(id);
    // Simulate API call
    setTimeout(() => {
      onAction(id, status);
      setProcessingId(null);
    }, 1500);
  };

  return (
    <div className="bg-white rounded-2xl shadow-lg shadow-purple-500/10 p-6">
      <h3 className="text-lg font-bold text-gray-800 mb-4">Pending Experience Requests ({requests.length})</h3>
      <div className="space-y-4 max-h-[30rem] overflow-y-auto pr-2">
        {requests.map((req, index) => (
          <motion.div
            key={req.id}
            layout
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, x: -50, transition: { duration: 0.3 } }}
            transition={{ duration: 0.3, delay: index * 0.05 }}
            className="border border-purple-100 rounded-lg p-4 hover:bg-purple-50 transition-colors duration-200"
          >
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
              {/* Request Info */}
              <div className="flex-1">
                <p className="font-semibold text-gray-800">{req.experienceTitle}</p>
                <p className="text-sm text-gray-600">Student: {req.studentName}</p>
                 <p className="text-xs text-gray-500 mt-1 flex items-center gap-1">
                    <School className="w-3 h-3"/> From: {req.collegeName}
                </p>
                <p className="text-xs text-gray-400 mt-1 flex items-center gap-1">
                    <Calendar className="w-3 h-3"/> Received: {req.submissionDate}
                </p>
              </div>

              {/* Action Buttons */}
              <div className="flex items-center gap-2 w-full sm:w-auto">
                <motion.button
                  whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}
                  className="flex-1 sm:flex-none text-sm flex items-center justify-center gap-2 px-3 py-2 border border-gray-300 rounded-md hover:bg-gray-100"
                >
                  <FileText className="w-4 h-4" /> View Details
                </motion.button>
                <motion.button
                  whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}
                  onClick={() => handleAction(req.id, 'Verified')}
                  disabled={processingId === req.id}
                  className="flex-1 sm:flex-none text-sm flex items-center justify-center gap-2 px-3 py-2 bg-green-500 text-white rounded-md hover:bg-green-600 disabled:opacity-50"
                >
                  {processingId === req.id ? <Loader2 className="w-4 h-4 animate-spin"/> : <Check className="w-4 h-4" />} Approve
                </motion.button>
                <motion.button
                  whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}
                  onClick={() => handleAction(req.id, 'Rejected')}
                  disabled={processingId === req.id}
                  className="flex-1 sm:flex-none text-sm flex items-center justify-center gap-2 px-3 py-2 bg-red-500 text-white rounded-md hover:bg-red-600 disabled:opacity-50"
                >
                  {processingId === req.id ? <Loader2 className="w-4 h-4 animate-spin"/> : <X className="w-4 h-4" />} Reject
                </motion.button>
              </div>
            </div>
          </motion.div>
        ))}
        {requests.length === 0 && (
            <div className="text-center py-8 text-gray-500">
                <Check className="w-10 h-10 mx-auto mb-2 text-green-500"/>
                <p>No pending experience verifications!</p>
            </div>
        )}
      </div>
    </div>
  );
}