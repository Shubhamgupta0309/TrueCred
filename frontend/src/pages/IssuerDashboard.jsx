import React, { useState, useEffect } from 'react';

const IssuerDashboard = () => {
  const [requests, setRequests] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [file, setFile] = useState(null);
  const [selectedRequest, setSelectedRequest] = useState(null);

  useEffect(() => {
    // Fetch pending requests
    const fetchRequests = async () => {
      setIsLoading(true);
      try {
        const resp = await fetch('/api/organization/pending-requests', {
          headers: { 'Authorization': `Bearer ${localStorage.getItem('accessToken')}` }
        });
        const data = await resp.json();
          if (data.success && data.data && Array.isArray(data.data.requests)) {
            setRequests(data.data.requests);
          } else if (data.requests) {
            setRequests(data.requests);
          } else {
            setRequests([]);
          }
      } catch (err) {
        setError('Failed to fetch requests');
      }
      setIsLoading(false);
    };
    fetchRequests();
  }, []);

  const handleFileChange = e => {
    setFile(e.target.files[0]);
  };

  const handleIssue = async request => {
    setIsLoading(true);
    setError('');
    setSuccess('');
    if (!file) {
      setError('Please select a file to issue');
      setIsLoading(false);
      return;
    }
    try {
      // Simulate IPFS upload
      const documentUrl = 'ipfs://' + file.name;
      const payload = {
        request_id: request.id,
        title: request.title,
        type: request.type,
        description: request.description,
        document_url: documentUrl
      };
      const resp = await fetch(`/api/organization/upload-credential/${request.user_id}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('accessToken')}`
        },
        body: JSON.stringify(payload)
      });
      const data = await resp.json();
      if (data.success) {
        setSuccess('Credential issued successfully!');
        setFile(null);
        setSelectedRequest(null);
        // Refresh requests
        const reqResp = await fetch('/api/organization/pending-requests', {
          headers: { 'Authorization': `Bearer ${localStorage.getItem('accessToken')}` }
        });
        const reqData = await reqResp.json();
          if (reqData.success && reqData.data && Array.isArray(reqData.data.requests)) {
            setRequests(reqData.data.requests);
          } else if (reqData.requests) {
            setRequests(reqData.requests);
          } else {
            setRequests([]);
          }
      } else {
        setError(data.message || 'Failed to issue credential');
      }
    } catch (err) {
      setError('Failed to issue credential');
    }
    setIsLoading(false);
  };

  return (
    <div className="max-w-3xl mx-auto p-6 bg-white rounded shadow">
      <h2 className="text-2xl font-bold mb-4">Issuer Dashboard</h2>
      {error && <div className="text-red-500 mb-2">{error}</div>}
      {success && <div className="text-green-600 mb-2">{success}</div>}
      <h3 className="text-xl font-semibold mb-2">Pending Requests</h3>
      <ul>
        {requests.length === 0 && <li className="text-gray-500">No pending requests</li>}
        {requests.map(r => (
            <li key={r.id} className="mb-4 p-2 border rounded">
              <strong>{r.title}</strong> ({r.type}) - {r.status}
              <div>{r.description || (r.metadata && r.metadata.description) || ''}</div>
              <div className="mt-2">
                <input type="file" onChange={handleFileChange} />
                <button className="bg-green-600 text-white px-3 py-1 rounded ml-2" onClick={() => handleIssue(r)} disabled={isLoading}>Issue</button>
              </div>
            </li>
        ))}
      </ul>
    </div>
  );
};

export default IssuerDashboard;
