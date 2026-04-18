import React, { useMemo, useState } from 'react';
import { motion } from 'framer-motion';
import StatusBadge from '../dashboard/StatusBadge';
import { History, Calendar, Shield, CheckCircle, XCircle, Search, Trash2 } from 'lucide-react';

export default function VerificationHistory({ history, onDelete }) {
  const [searchTcId, setSearchTcId] = useState('');
  const [selectedItem, setSelectedItem] = useState(null);
  const [deletingId, setDeletingId] = useState(null);

  const filteredHistory = useMemo(() => {
    const query = searchTcId.trim().toLowerCase();
    if (!query) return history || [];

    return (history || []).filter((item) => {
      const searchableValues = [
        item.studentTruecredId,
        item.student_truecred_id,
        item.id,
        item.studentName,
        item.credentialTitle,
      ]
        .filter(Boolean)
        .map((value) => String(value).toLowerCase());

      return searchableValues.some((value) => value.includes(query));
    });
  }, [history, searchTcId]);

  const getBadgeStatus = (status) => {
    const normalized = String(status || '').toLowerCase();
    if (normalized === 'verified' || normalized === 'issued' || normalized === 'approved') return 'Verified';
    if (normalized === 'rejected') return 'Rejected';
    return 'Pending';
  };

  const handleDelete = async (item) => {
    if (!item?.id || !onDelete) return;
    const confirmed = window.confirm('Delete this history item? This also removes related student record(s).');
    if (!confirmed) return;

    setDeletingId(item.id);
    try {
      await onDelete(item.id);
      if (selectedItem?.id === item.id) {
        setSelectedItem(null);
      }
    } finally {
      setDeletingId(null);
    }
  };

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

  // Check if history is empty
  if (!history || history.length === 0) {
    return (
      <div className="bg-cyan-950/30 border border-cyan-500/30 rounded-2xl shadow-lg shadow-cyan-500/10 p-6">
        <h3 className="text-lg font-bold text-cyan-100 mb-4 flex items-center gap-2">
          <History className="w-5 h-5 text-cyan-400" />
          Verification History
        </h3>
        <div className="text-center py-12">
          <History className="w-12 h-12 text-cyan-500/40 mx-auto mb-4" />
          <p className="text-cyan-300/70">No verification history yet</p>
          <p className="text-cyan-300/50 text-sm">Approved requests will appear here</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-cyan-950/30 border border-cyan-500/30 rounded-2xl shadow-lg shadow-cyan-500/10 p-6">
      <h3 className="text-lg font-bold text-cyan-100 mb-4 flex items-center gap-2">
        <History className="w-5 h-5 text-cyan-400" />
        Verification History
      </h3>

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

      <div className="space-y-3 max-h-72 overflow-y-auto pr-2">
        {filteredHistory.map((item, index) => (
          <motion.div
            key={item.id}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.3, delay: index * 0.1 }}
            className="border border-cyan-500/20 bg-cyan-950/20 rounded-lg p-3"
          >
            <div className="flex justify-between items-center">
              <button type="button" onClick={() => setSelectedItem(item)} className="flex-1 text-left">
                <p className="font-medium text-sm text-cyan-100">{item.credentialTitle}</p>
                <p className="text-xs text-cyan-300">Student: {item.studentName}</p>
                {item.studentTruecredId && (
                  <p className="text-xs text-cyan-300/80">TC ID: {item.studentTruecredId}</p>
                )}
              </button>
              <div className="text-right flex items-center gap-2">
                {getBlockchainIcon(item)}
                <div>
                  <StatusBadge status={getBadgeStatus(item.status)} />
                  <p className="text-xs text-cyan-300/70 mt-1 flex items-center justify-end gap-1">
                      <Calendar className="w-3 h-3"/> {item.actionDate}
                  </p>
                  {onDelete && (
                    <div className="mt-2 flex justify-end">
                      <button
                        type="button"
                        onClick={() => handleDelete(item)}
                        disabled={deletingId === item.id}
                        title="Delete"
                        className="inline-flex items-center justify-center h-7 w-7 rounded-md bg-red-600 text-white hover:bg-red-700 disabled:opacity-60"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  )}
                </div>
              </div>
            </div>
            
            {/* Show blockchain transaction hash if available */}
            {(item.blockchain_tx_hash || item.blockchain_data?.tx_hash) && (
              <div className="mt-2 pt-2 border-t border-cyan-500/20">
                <p className="text-xs text-cyan-300 flex items-center gap-1">
                  <Shield className="w-3 h-3" />
                  TX: {(item.blockchain_tx_hash || item.blockchain_data?.tx_hash).substring(0, 10)}...
                </p>
              </div>
            )}
          </motion.div>
        ))}

        {filteredHistory.length === 0 && (
          <p className="text-sm text-cyan-300/70 text-center py-6">No history found for this TC ID.</p>
        )}
      </div>

      {selectedItem && (
        <div className="fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-4">
          <div className="w-full max-w-xl bg-slate-950 border border-cyan-500/30 rounded-2xl p-6 text-cyan-100">
            <div className="flex items-start justify-between gap-4">
              <h4 className="text-xl font-bold">Verification Details</h4>
              <button onClick={() => setSelectedItem(null)} className="text-cyan-300 hover:text-cyan-100">Close</button>
            </div>
            <div className="mt-4 space-y-2 text-sm">
              <p><span className="text-cyan-300">Title:</span> {selectedItem.credentialTitle || 'N/A'}</p>
              <p><span className="text-cyan-300">Student:</span> {selectedItem.studentName || 'N/A'}</p>
              <p><span className="text-cyan-300">TC ID:</span> {selectedItem.studentTruecredId || 'N/A'}</p>
              <p><span className="text-cyan-300">Student Email:</span> {selectedItem.studentEmail || 'N/A'}</p>
              <p><span className="text-cyan-300">Issuer:</span> {selectedItem.issuer || 'N/A'}</p>
              <p><span className="text-cyan-300">Status:</span> {getBadgeStatus(selectedItem.status)}</p>
              <p><span className="text-cyan-300">Verification Status:</span> {selectedItem.verification_status || 'N/A'}</p>
              <p><span className="text-cyan-300">Date:</span> {selectedItem.actionDate || 'N/A'}</p>
              <p><span className="text-cyan-300">History ID:</span> {selectedItem.id || 'N/A'}</p>
              {onDelete && (
                <div className="pt-3 flex justify-end">
                  <button
                    type="button"
                    onClick={() => handleDelete(selectedItem)}
                    disabled={deletingId === selectedItem.id}
                    title="Delete"
                    className="inline-flex items-center justify-center h-9 w-9 rounded-md bg-red-600 text-white hover:bg-red-700 disabled:opacity-60"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}