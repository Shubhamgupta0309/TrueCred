import React, { useState, useEffect } from 'react';
import { companyService } from '../services/api';
import { useNavigate } from 'react-router-dom';

const CompanyDashboard = () => {
  const [pendingRequests, setPendingRequests] = useState([]);
  const [verificationHistory, setVerificationHistory] = useState([]);
  const [loading, setLoading] = useState({ requests: true, history: true });
  const [error, setError] = useState({ requests: null, history: null });

  const navigate = useNavigate();

  useEffect(() => {
    const fetchPendingRequests = async () => {
      try {
        const response = await companyService.getPendingExperienceRequests();
        setPendingRequests(response.data || []);
      } catch (err) {
        setError(prev => ({ ...prev, requests: err.message }));
      } finally {
        setLoading(prev => ({ ...prev, requests: false }));
      }
    };

    const fetchVerificationHistory = async () => {
      try {
        const response = await companyService.getExperienceHistory();
        setVerificationHistory(response.data || []);
      } catch (err) {
        setError(prev => ({ ...prev, history: err.message }));
      } finally {
        setLoading(prev => ({ ...prev, history: false }));
      }
    };

    fetchPendingRequests();
    fetchVerificationHistory();
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    localStorage.removeItem('userRole');
    navigate('/auth');
  };

  const handleApproveRequest = async (requestId) => {
    try {
      await companyService.approveExperienceRequest(requestId);
      setPendingRequests(requests => requests.filter(req => req.id !== requestId));
      // Refresh verification history
      const response = await companyService.getExperienceHistory();
      setVerificationHistory(response.data || []);
    } catch (err) {
      console.error('Error approving request:', err);
    }
  };

  const handleRejectRequest = async (requestId, reason) => {
    try {
      await companyService.rejectExperienceRequest(requestId, reason);
      setPendingRequests(requests => requests.filter(req => req.id !== requestId));
      // Refresh verification history
      const response = await companyService.getExperienceHistory();
      setVerificationHistory(response.data || []);
    } catch (err) {
      console.error('Error rejecting request:', err);
    }
  };

  const PendingRequestsList = () => (
    <div className="bg-white shadow-md rounded-lg p-4">
      <h3 className="text-lg font-semibold mb-4">Pending Experience Verification Requests</h3>
      {loading.requests ? (
        <div className="text-center py-4">Loading requests...</div>
      ) : error.requests ? (
        <div className="text-red-500 py-4">{error.requests}</div>
      ) : pendingRequests.length === 0 ? (
        <div className="text-gray-500 py-4">No pending requests</div>
      ) : (
        <div className="space-y-4">
          {pendingRequests.map((request) => (
            <div key={request.id} className="border rounded p-4">
              <h4 className="font-semibold">{request.studentName}</h4>
              <p className="text-gray-600">{request.experienceTitle}</p>
              <p className="text-gray-500">Duration: {request.duration}</p>
              <p className="text-gray-500">Submitted: {request.submissionDate}</p>
              <div className="mt-4 space-x-2">
                <button
                  onClick={() => handleApproveRequest(request.id)}
                  className="bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded"
                >
                  Verify
                </button>
                <button
                  onClick={() => handleRejectRequest(request.id, "Information incorrect or incomplete")}
                  className="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded"
                >
                  Reject
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );

  const VerificationHistoryList = () => (
    <div className="bg-white shadow-md rounded-lg p-4 mt-6">
      <h3 className="text-lg font-semibold mb-4">Verification History</h3>
      {loading.history ? (
        <div className="text-center py-4">Loading history...</div>
      ) : error.history ? (
        <div className="text-red-500 py-4">{error.history}</div>
      ) : verificationHistory.length === 0 ? (
        <div className="text-gray-500 py-4">No verification history</div>
      ) : (
        <div className="space-y-4">
          {verificationHistory.map((record) => (
            <div key={record.id} className="border rounded p-4">
              <h4 className="font-semibold">{record.studentName}</h4>
              <p className="text-gray-600">{record.experienceTitle}</p>
              <p className="text-gray-500">Action Date: {record.actionDate}</p>
              <div className="mt-2">
                <span className={`px-2 py-1 rounded text-sm ${
                  record.status === 'verified' ? 'bg-green-100 text-green-800' :
                  record.status === 'rejected' ? 'bg-red-100 text-red-800' :
                  'bg-gray-100 text-gray-800'
                }`}>
                  {record.status}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-100">
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 py-6 flex justify-between items-center">
          <h2 className="text-2xl font-bold text-gray-900">Company Dashboard</h2>
          <button
            onClick={handleLogout}
            className="text-gray-600 hover:text-gray-800"
          >
            Logout
          </button>
        </div>
      </header>
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 sm:px-0">
          <PendingRequestsList />
          <VerificationHistoryList />
        </div>
      </main>
    </div>
  );
};

export default CompanyDashboard;
