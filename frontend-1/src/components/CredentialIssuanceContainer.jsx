import React, { useState, useEffect } from 'react';
import IssueCredentialForm from './IssueCredentialForm';
import StudentLookup from './StudentLookup';
import { motion } from 'framer-motion';
import { api } from '../services/api';

const CredentialIssuanceContainer = ({ onCredentialIssued }) => {
  const [selectedStudent, setSelectedStudent] = useState(null);
  const [credentials, setCredentials] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Fetch issued credentials on component mount
  useEffect(() => {
    const fetchCredentials = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const response = await api.get('/credentials/issued');
        if (response.data && response.data.credentials) {
          console.log('Loaded credentials:', response.data.credentials);
          setCredentials(response.data.credentials);
        } else {
          throw new Error('Invalid response format from server');
        }
      } catch (err) {
        console.error('Failed to fetch credentials:', err);
        setError(err.response?.data?.message || err.message || 'Failed to load credentials');
        setCredentials([]);
      } finally {
        setLoading(false);
      }
    };

    fetchCredentials();
  }, []);

  const handleStudentSelect = (student) => {
    setSelectedStudent(student);
  };

  const handleCredentialIssued = (credential) => {
    setCredentials([credential, ...credentials]);
    
    if (onCredentialIssued) {
      onCredentialIssued(credential);
    }
  };

  const clearSelectedStudent = () => {
    setSelectedStudent(null);
  };

  return (
    <div className="space-y-8">
      {!selectedStudent ? (
        <StudentLookup onStudentSelect={handleStudentSelect} />
      ) : (
        <div className="bg-purple-50 p-4 rounded-lg mb-6">
          <div className="flex justify-between items-center">
            <div>
              <h3 className="font-medium text-purple-800">Selected Student</h3>
              <p className="text-gray-700">{selectedStudent.name}</p>
              <p className="text-gray-500 text-sm">{selectedStudent.email}</p>
              {selectedStudent.wallet_address && (
                <p className="text-gray-500 text-xs font-mono mt-1">Wallet: {selectedStudent.wallet_address}</p>
              )}
            </div>
            <button
              onClick={clearSelectedStudent}
              className="text-purple-600 hover:text-purple-800"
            >
              Change Student
            </button>
          </div>
        </div>
      )}

      {selectedStudent && (
        <IssueCredentialForm 
          onCredentialIssued={handleCredentialIssued}
          initialRecipient={{
            email: selectedStudent.email,
            wallet: selectedStudent.wallet_address
          }}
        />
      )}

      {loading ? (
        <div className="mt-8 text-center py-6">
          <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-purple-600 mx-auto"></div>
          <p className="mt-2 text-gray-600">Loading credentials...</p>
        </div>
      ) : error ? (
        <div className="mt-8 bg-red-100 border-l-4 border-red-500 text-red-700 p-4" role="alert">
          <p>{error}</p>
        </div>
      ) : credentials.length > 0 ? (
        <div className="mt-8">
          <h3 className="text-xl font-semibold mb-4 text-purple-700">Recently Issued Credentials</h3>
          <div className="bg-white shadow rounded-md overflow-hidden">
            <ul className="divide-y divide-gray-200">
              {credentials.map((credential, index) => (
                <motion.li
                  key={credential.id || index}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.05 }}
                  className="p-4"
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="font-medium text-gray-900">{credential.title}</h4>
                      <p className="text-sm text-gray-500">
                        Issued to: {credential.recipient || credential.recipientEmail}
                      </p>
                      <p className="text-xs text-gray-400">
                        Type: {credential.credentialType} | Issued: {new Date(credential.issueDate).toLocaleDateString()}
                      </p>
                    </div>
                    <div className="text-right">
                      <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded-full">
                        Issued
                      </span>
                    </div>
                  </div>
                </motion.li>
              ))}
            </ul>
          </div>
        </div>
      ) : (
        <div className="mt-8 bg-gray-50 rounded-lg p-8 text-center">
          <svg xmlns="http://www.w3.org/2000/svg" className="h-12 w-12 mx-auto text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <h3 className="mt-4 text-lg font-medium text-gray-900">No credentials issued yet</h3>
          <p className="mt-1 text-gray-500">When you issue credentials, they will appear here.</p>
        </div>
      )}
    </div>
  );
};

export default CredentialIssuanceContainer;
