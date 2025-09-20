import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Check, X, FileText, Loader2, Calendar, Shield, CheckCircle } from 'lucide-react';
import { collegeService, api } from '../../services/api';
import { useToast } from '../../context/ToastContext.jsx';

export default function PendingRequests({ requests = [], onAction }) {
  const { error: toastError, success } = useToast();
  const [processingId, setProcessingId] = useState(null);
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [selectedRequest, setSelectedRequest] = useState(null);
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedInstitution, setSelectedInstitution] = useState('');
  
  // Get unique institutions for filter dropdown
  const institutions = [...new Set(requests.map(req => req.institutionName || req.institution_name || req.issuer).filter(Boolean))];
  
  // Filter requests based on search and institution
  const filteredRequests = requests.filter(req => {
    const matchesSearch = !searchTerm || 
      (req.title || req.credentialTitle || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
      (req.studentName || req.student_name || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
      (req.studentEmail || req.student_email || '').toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesInstitution = !selectedInstitution || 
      (req.institutionName || req.institution_name || req.issuer) === selectedInstitution;
    
    return matchesSearch && matchesInstitution;
  });

  const handleViewDoc = async (req) => {
    if (!req || !req.attachments || req.attachments.length === 0) {
      toastError('No documents attached to this request');
      return;
    }

    try {
      // Get the first attachment
      const attachment = req.attachments[0];
      const documentUrl = attachment.uri;

      if (!documentUrl) {
        alert('Document URL not found');
        return;
      }

      console.log('Opening document URL:', documentUrl);
      window.open(documentUrl, '_blank');
    } catch (error) {
      console.error('Error opening document:', error);
      alert('Error opening document: ' + (error.message || 'Unknown error'));
    }
  };

  const handleApprove = async (req) => {
    if (!req || !req.id) return;
    setProcessingId(req.id);
    try {
      const resp = await collegeService.approveRequest(req.id);
      if (resp && resp.data) {
        success('Request approved successfully!');
        onAction && onAction(req.id, 'Issued');
      }
    } catch (err) {
      console.error('Approve error', err);
      toastError('Failed to approve request. Please try again.');
    } finally {
      setProcessingId(null);
    }
  };

  const handleReject = async (req) => {
    if (!req || !req.id) return;
    setProcessingId(req.id);
    try {
      const resp = await collegeService.rejectRequest(req.id);
      if (resp && resp.data) {
        success('Request rejected successfully!');
        onAction && onAction(req.id, 'Rejected');
      }
    } catch (err) {
      console.error('Reject error', err);
      toastError('Failed to reject request. Please try again.');
    } finally {
      setProcessingId(null);
    }
  };

  const handleIssue = (req) => {
    setSelectedRequest(req);
    setShowUploadModal(true);
  };

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleUploadAndIssue = async () => {
    if (!selectedRequest || !file) return;
    setUploading(true);
    try {
      // Read file as base64
      const reader = new FileReader();
      reader.onload = async (ev) => {
        const base64Data = ev.target.result.split(',')[1];
        const payload = {
          title: selectedRequest.title || 'Issued Credential',
          type: selectedRequest.type || 'credential',
          issue_date: new Date().toISOString().slice(0,10),
          request_id: selectedRequest.id,
          document: base64Data,
          filename: file.name
        };
        const resp = await api.post(`/api/organization/upload-credential/${selectedRequest.user_id}`, payload);
        if (resp.data && resp.data.success) {
          onAction && onAction(selectedRequest.id, 'Issued');
          setShowUploadModal(false);
          setFile(null);
          setSelectedRequest(null);
        } else {
          alert('Failed to issue credential');
        }
        setUploading(false);
      };
      reader.readAsDataURL(file);
    } catch (err) {
      setUploading(false);
      alert('Failed to issue credential');
      console.error('Issue error', err);
    }
  };

  if (!requests || requests.length === 0) {
    return (
      <div className="bg-white rounded-xl shadow-md p-6">
        <h3 className="text-lg font-bold mb-2">Pending Requests</h3>
        <p className="text-gray-500">No pending requests at the moment.</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl shadow-md p-6">
      <h3 className="text-lg font-bold mb-4">Pending Requests</h3>
      
      {/* Search and Filter Section */}
      <div className="mb-4 space-y-3">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Search Requests
          </label>
          <input
            type="text"
            placeholder="Search by title, student name, or email..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            College/University Name (filter)
          </label>
          <select
            value={selectedInstitution}
            onChange={(e) => setSelectedInstitution(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="">All Institutions</option>
            {institutions.map((institution, index) => (
              <option key={index} value={institution}>
                {institution}
              </option>
            ))}
          </select>
        </div>
        
        {(searchTerm || selectedInstitution) && (
          <div className="flex items-center gap-2 text-sm text-gray-600">
            <span>Filtered: {filteredRequests.length} of {requests.length} requests</span>
            <button
              onClick={() => {
                setSearchTerm('');
                setSelectedInstitution('');
              }}
              className="text-blue-600 hover:text-blue-800 underline"
            >
              Clear filters
            </button>
          </div>
        )}
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
            className="border border-purple-100 rounded-lg p-4 hover:bg-purple-50 transition-colors duration-200"
          >
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
              {/* Request Info */}
              <div className="flex-1">
                <div className="mb-2">
                  <h4 className="font-semibold text-gray-800 text-sm">Title</h4>
                  <p className="text-blue-600 font-medium">{req.title || req.credentialTitle || 'No title provided'}</p>
                </div>
                
                <div className="mb-2">
                  <h4 className="font-semibold text-gray-800 text-sm">Student</h4>
                  <p className="text-gray-700">{req.studentName || req.student_name || 'Unknown Student'}</p>
                  <p className="text-xs text-gray-500">{req.studentEmail || req.student_email || ''}</p>
                </div>
                
                <div className="mb-2">
                  <h4 className="font-semibold text-gray-800 text-sm">Institution</h4>
                  <p className="text-gray-700">{req.institutionName || req.institution_name || req.issuer || 'Not specified'}</p>
                </div>
                
                <p className="text-xs text-gray-400 mt-2 flex items-center gap-1">
                    <Calendar className="w-3 h-3"/> Submitted: {req.submissionDate || (req.created_at ? new Date(req.created_at).toLocaleDateString() : 'Unknown')}
                </p>
                
                {/* Blockchain Status Indicator */}
                <div className="mt-2 flex items-center gap-2">
                  {req.blockchain_tx_hash || req.blockchain_data?.tx_hash ? (
                    <div className="flex items-center gap-1 text-xs text-green-600">
                      <CheckCircle className="w-3 h-3" />
                      <span>Blockchain Verified</span>
                    </div>
                  ) : (
                    <div className="flex items-center gap-1 text-xs text-gray-400">
                      <Shield className="w-3 h-3" />
                      <span>Not on Blockchain</span>
                    </div>
                  )}
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex items-center gap-2 w-full sm:w-auto">
                <motion.button
                  whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}
                  onClick={() => handleViewDoc(req)}
                  className="flex-1 sm:flex-none text-sm flex items-center justify-center gap-2 px-3 py-2 border border-gray-300 rounded-md hover:bg-gray-100"
                >
                  <FileText className="w-4 h-4" /> View Doc
                </motion.button>
                <motion.button
                  whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}
                  onClick={() => handleIssue(req)}
                  disabled={processingId === req.id}
                  className="flex-1 sm:flex-none text-sm flex items-center justify-center gap-2 px-3 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 disabled:opacity-50"
                >
                  {processingId === req.id ? <Loader2 className="w-4 h-4 animate-spin"/> : <FileText className="w-4 h-4" />} Issue
                </motion.button>
                <motion.button
                  whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}
                  onClick={() => handleApprove(req)}
                  disabled={processingId === req.id}
                  className="flex-1 sm:flex-none text-sm flex items-center justify-center gap-2 px-3 py-2 bg-green-500 text-white rounded-md hover:bg-green-600 disabled:opacity-50"
                >
                  {processingId === req.id ? <Loader2 className="w-4 h-4 animate-spin"/> : <Check className="w-4 h-4" />} Approve
                </motion.button>
                <motion.button
                  whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}
                  onClick={() => handleReject(req)}
                  disabled={processingId === req.id}
                  className="flex-1 sm:flex-none text-sm flex items-center justify-center gap-2 px-3 py-2 bg-red-500 text-white rounded-md hover:bg-red-600 disabled:opacity-50"
                >
                  {processingId === req.id ? <Loader2 className="w-4 h-4 animate-spin"/> : <X className="w-4 h-4" />} Reject
                </motion.button>
              </div>
            </div>
          </motion.div>
        ))}
        {filteredRequests.length === 0 && requests.length > 0 && (
            <div className="text-center py-8 text-gray-500">
                <FileText className="w-10 h-10 mx-auto mb-2 text-gray-400"/>
                <p>No requests match your search criteria.</p>
                <button
                  onClick={() => {
                    setSearchTerm('');
                    setSelectedInstitution('');
                  }}
                  className="text-blue-600 hover:text-blue-800 underline mt-2"
                >
                  Clear filters
                </button>
            </div>
        )}
        
        {requests.length === 0 && (
            <div className="text-center py-8 text-gray-500">
                <Check className="w-10 h-10 mx-auto mb-2 text-green-500"/>
                <p>All requests have been processed!</p>
            </div>
        )}
      </div>

      {/* Upload Modal */}
      {showUploadModal && (
        <div className="fixed inset-0 bg-black bg-opacity-30 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-lg p-8 w-full max-w-md">
            <h2 className="text-xl font-bold mb-4">Upload Authoritative Credential</h2>
            <input type="file" accept=".pdf,.jpg,.jpeg,.png,.doc,.docx" onChange={handleFileChange} className="mb-4" />
            <div className="flex gap-4 mt-4">
              <button
                onClick={handleUploadAndIssue}
                disabled={!file || uploading}
                className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
              >
                {uploading ? 'Uploading...' : 'Upload & Issue'}
              </button>
              <button
                onClick={() => { setShowUploadModal(false); setFile(null); setSelectedRequest(null); }}
                className="px-4 py-2 bg-gray-300 text-gray-700 rounded hover:bg-gray-400"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}