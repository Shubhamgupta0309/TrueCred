import React, { useMemo, useState } from 'react';
import { motion } from 'framer-motion';
import { Check, X, FileText, Loader2, Calendar, School, Search } from 'lucide-react';

export default function PendingExperienceRequests({ requests = [], onAction }) {
  const [processingId, setProcessingId] = useState(null);
  const [searchTcId, setSearchTcId] = useState('');

  const filteredRequests = useMemo(() => {
    const query = searchTcId.trim().toLowerCase();
    if (!query) return requests;

    return requests.filter((req) => {
      const searchableValues = [
        req.studentTruecredId,
        req.student_truecred_id,
        req.id,
        req.studentName,
        req.experienceTitle,
      ]
        .filter(Boolean)
        .map((value) => String(value).toLowerCase());

      return searchableValues.some((value) => value.includes(query));
    });
  }, [requests, searchTcId]);

  const handleViewDetails = (req) => {
    if (!req || !req.documentUrls || req.documentUrls.length === 0) {
      alert('No documents available for this experience');
      return;
    }

    const documentUrl = req.documentUrls[0]?.url;
    if (documentUrl) {
      window.open(documentUrl, '_blank');
    } else {
      alert('Document URL not found');
    }
  };

  const handleApprove = async (req) => {
    if (!req || !req.id) return;
    setProcessingId(req.id);
    try {
      await onAction(req.id, 'approved');
    } finally {
      setProcessingId(null);
    }
  };

  const handleReject = async (req) => {
    if (!req || !req.id) return;

    setProcessingId(req.id);
    try {
      await onAction(req.id, 'rejected');
    } finally {
      setProcessingId(null);
    }
  };

  return (
    <div className="bg-cyan-950/30 border border-cyan-500/30 rounded-2xl shadow-lg shadow-cyan-500/10 p-6">
      <h3 className="text-lg font-bold text-cyan-100 mb-4">Pending Experience Requests ({requests.length})</h3>

      <div className="mb-4">
        <label className="block text-sm font-medium text-cyan-200 mb-1">Search by TC ID</label>
        <div className="relative">
          <Search className="w-4 h-4 text-cyan-300 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={searchTcId}
            onChange={(e) => setSearchTcId(e.target.value)}
            placeholder="e.g. TC123456"
            className="w-full pl-10 pr-3 py-2 border border-cyan-500/30 bg-slate-900 text-cyan-100 rounded-md focus:outline-none focus:ring-2 focus:ring-cyan-500"
          />
        </div>
      </div>

      <div className="space-y-4 max-h-[30rem] overflow-y-auto pr-2">
        {filteredRequests.map((req, index) => (
          <motion.div
            key={req.id}
            layout
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, x: -50, transition: { duration: 0.3 } }}
            transition={{ duration: 0.3, delay: index * 0.05 }}
            className="border border-cyan-500/20 bg-cyan-950/20 rounded-lg p-4 hover:bg-cyan-900/30 transition-colors duration-200"
          >
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
              <div className="flex-1">
                <p className="font-semibold text-cyan-100">{req.experienceTitle || 'Untitled Experience'}</p>
                <p className="text-sm text-cyan-200">Student: {req.studentName || 'Unknown Student'}</p>
                {req.studentTruecredId && (
                  <p className="text-xs text-cyan-300/80 mt-1">TC ID: {req.studentTruecredId}</p>
                )}
                <p className="text-xs text-cyan-300/70 mt-1 flex items-center gap-1">
                  <School className="w-3 h-3" /> From: {req.company || req.collegeName || 'Not specified'}
                </p>
                <p className="text-xs text-cyan-300/60 mt-1 flex items-center gap-1">
                  <Calendar className="w-3 h-3" /> Received: {req.submissionDate || 'Unknown'}
                </p>
              </div>

              <div className="flex items-center gap-2 w-full sm:w-auto">
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={() => handleViewDetails(req)}
                  className="flex-1 sm:flex-none text-sm flex items-center justify-center gap-2 px-3 py-2 border border-cyan-500/30 text-cyan-100 rounded-md hover:bg-cyan-900/30"
                >
                  <FileText className="w-4 h-4" /> View Details
                </motion.button>

                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={() => handleApprove(req)}
                  disabled={processingId === req.id}
                  className="flex-1 sm:flex-none text-sm flex items-center justify-center gap-2 px-3 py-2 bg-green-500 text-white rounded-md hover:bg-green-600 disabled:opacity-50"
                >
                  {processingId === req.id ? <Loader2 className="w-4 h-4 animate-spin" /> : <Check className="w-4 h-4" />} Approve
                </motion.button>

                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={() => handleReject(req)}
                  disabled={processingId === req.id}
                  className="flex-1 sm:flex-none text-sm flex items-center justify-center gap-2 px-3 py-2 bg-red-500 text-white rounded-md hover:bg-red-600 disabled:opacity-50"
                >
                  {processingId === req.id ? <Loader2 className="w-4 h-4 animate-spin" /> : <X className="w-4 h-4" />} Reject
                </motion.button>
              </div>
            </div>
          </motion.div>
        ))}

        {filteredRequests.length === 0 && requests.length > 0 && (
          <p className="text-sm text-cyan-300/70 text-center py-6">No pending requests found for this TC ID.</p>
        )}

        {requests.length === 0 && (
          <div className="text-center py-8 text-cyan-300/70">
            <Check className="w-10 h-10 mx-auto mb-2 text-green-500" />
            <p>All requests have been processed!</p>
          </div>
        )}
      </div>

    </div>
  );
}
