import React, { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import { credentialService, experienceService } from '../../services/api';
import { Button, Card, Alert } from '../ui';
import { PlusIcon, DocumentIcon, BriefcaseIcon, CheckCircleIcon, WalletIcon } from '@heroicons/react/24/outline';
import { RequestCredentialModal } from './RequestCredentialModal';
import { RequestExperienceModal } from './RequestExperienceModal';

// Mock data for demo purposes
const MOCK_CREDENTIALS = [
  {
    _id: '1',
    title: 'Bachelor of Computer Science',
    institution: 'MIT University',
    status: 'verified',
    verified: true,
    createdAt: new Date('2023-01-15'),
    document_hash: 'QmHashExample1',
    notes: 'Graduated with honors'
  },
  {
    _id: '2',
    title: 'Data Science Certificate',
    institution: 'Stanford Online',
    status: 'pending',
    verified: false,
    createdAt: new Date('2023-03-10'),
    document_hash: 'QmHashExample2'
  }
];

const MOCK_EXPERIENCES = [
  {
    _id: '1',
    position: 'Software Engineer',
    company: 'Google',
    start_date: new Date('2022-01-01'),
    end_date: new Date('2023-01-01'),
    status: 'verified',
    verified: true,
    document_hash: 'QmHashExample3',
    description: 'Worked on cloud infrastructure projects'
  },
  {
    _id: '2',
    position: 'Frontend Developer',
    company: 'Meta',
    start_date: new Date('2023-02-01'),
    end_date: null,
    status: 'pending',
    verified: false,
    document_hash: 'QmHashExample4'
  }
];

export default function StudentDashboard() {
  const { user, connectWallet } = useAuth();
  const [credentials, setCredentials] = useState([]);
  const [experiences, setExperiences] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showRequestModal, setShowRequestModal] = useState(false);
  const [showExperienceModal, setShowExperienceModal] = useState(false);
  const [uploadingDoc, setUploadingDoc] = useState(false);
  const [useMockData, setUseMockData] = useState(false);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      try {
        // Try to fetch real data first
        const [credRes, expRes] = await Promise.all([
          credentialService.getCredentials(),
          experienceService.getExperiences()
        ]);
        
        console.log('Credentials loaded:', credRes.data);
        console.log('Experiences loaded:', expRes.data);
        
        setCredentials(credRes.data || []);
        setExperiences(expRes.data || []);
        setUseMockData(false);
      } catch (err) {
        // If API calls fail (like CORS error), use mock data for demo
        console.error('API error, using mock data instead:', err);
        setCredentials(MOCK_CREDENTIALS);
        setExperiences(MOCK_EXPERIENCES);
        setUseMockData(true);
      }
    } catch (err) {
      console.error('Dashboard load error:', err);
      setError(err.response?.data?.message || err.message || 'Failed to load dashboard data');
      setCredentials([]);
      setExperiences([]);
    } finally {
      setLoading(false);
    }
  };

  const handleRequestCredential = async (formData) => {
    try {
      setUploadingDoc(true);
      setError(null);
      
      // Validate form data
      if (!formData.get('institution') || !formData.get('credential_type') || !formData.get('title')) {
        throw new Error('Please fill in all required fields');
      }

      const documentFile = formData.get('document');
      if (!documentFile) {
        throw new Error('Please upload a document');
      }

      if (useMockData) {
        // Mock successful response for demo
        console.log('Using mock data - would submit:', {
          title: formData.get('title'),
          institution: formData.get('institution'),
          credential_type: formData.get('credential_type')
        });
        
        // Add new mock credential
        const newCredential = {
          _id: Date.now().toString(),
          title: formData.get('title'),
          institution: formData.get('institution'),
          status: 'pending',
          verified: false,
          createdAt: new Date(),
          document_hash: 'QmNewMockHash' + Math.floor(Math.random() * 1000)
        };
        
        setCredentials(prev => [newCredential, ...prev]);
        setShowRequestModal(false);
        alert('Credential request submitted successfully! (Demo Mode)');
        return;
      }

      // Create credential request with proper headers for multipart/form-data
      const response = await credentialService.requestCredential(formData);
      console.log('Credential request response:', response);
      
      // Refresh dashboard data
      await loadDashboardData();
      setShowRequestModal(false);
      
      // Show success message
      alert('Credential request submitted successfully!');
    } catch (err) {
      console.error('Credential request error:', err);
      setError(err.response?.data?.message || err.message || 'Failed to request credential');
    } finally {
      setUploadingDoc(false);
    }
  };

  const handleRequestExperience = async (formData) => {
    try {
      setUploadingDoc(true);
      setError(null);
      
      // Validate form data
      if (!formData.get('company') || !formData.get('position') || !formData.get('start_date')) {
        throw new Error('Please fill in all required fields');
      }

      const documentFile = formData.get('document');
      if (!documentFile) {
        throw new Error('Please upload a document');
      }

      if (useMockData) {
        // Mock successful response for demo
        console.log('Using mock data - would submit:', {
          position: formData.get('position'),
          company: formData.get('company'),
          start_date: formData.get('start_date')
        });
        
        // Add new mock experience
        const newExperience = {
          _id: Date.now().toString(),
          position: formData.get('position'),
          company: formData.get('company'),
          start_date: new Date(formData.get('start_date')),
          end_date: formData.get('end_date') ? new Date(formData.get('end_date')) : null,
          status: 'pending',
          verified: false,
          document_hash: 'QmNewMockHash' + Math.floor(Math.random() * 1000),
          description: formData.get('description') || ''
        };
        
        setExperiences(prev => [newExperience, ...prev]);
        setShowExperienceModal(false);
        alert('Experience verification request submitted successfully! (Demo Mode)');
        return;
      }

      // Create experience request with proper headers for multipart/form-data
      const response = await experienceService.requestExperience(formData);
      console.log('Experience request response:', response);

      // Refresh dashboard data
      await loadDashboardData();
      setShowExperienceModal(false);
      
      // Show success message
      alert('Experience verification request submitted successfully!');
    } catch (err) {
      console.error('Experience request error:', err);
      setError(err.response?.data?.message || err.message || 'Failed to request experience verification');
    } finally {
      setUploadingDoc(false);
    }
  };

  const downloadDocument = async (documentHash) => {
    try {
      if (useMockData) {
        // In demo mode, simulate download
        alert('Downloading document (Demo Mode)');
        return;
      }
      
      const response = await fetch(`${process.env.VITE_API_URL}/ipfs/gateway/${documentHash}`);
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'document';
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      setError('Failed to download document');
    }
  };

  if (loading) return <div>Loading...</div>;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {error && (
        <Alert type="error" message={error} onClose={() => setError(null)} />
      )}
      
      {useMockData && (
        <div className="mb-4 p-4 bg-yellow-50 border-l-4 border-yellow-400 text-yellow-800">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <p className="text-sm">
                Demo Mode: Using mock data because API is unavailable. All actions are simulated.
              </p>
            </div>
          </div>
        </div>
      )}

      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-8">
        <div>
          <h1 className="text-2xl font-bold">Welcome, {user?.first_name || user?.username}</h1>
          {user?.email && <p className="text-gray-600">{user.email}</p>}
        </div>
        <div className="flex flex-col w-full md:w-auto gap-2">
          <Button
            onClick={() => setShowRequestModal(true)}
            icon={<PlusIcon className="h-5 w-5" />}
            className="w-full md:w-auto bg-purple-600 hover:bg-purple-700 text-white"
            disabled={uploadingDoc}
          >
            Upload New Credential
          </Button>
          <Button
            onClick={() => setShowExperienceModal(true)}
            className="w-full bg-blue-600 hover:bg-blue-700 text-white"
            icon={<BriefcaseIcon className="h-5 w-5" />}
          >
            Add New Experience
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* Credentials Section */}
        <section>
          <h2 className="text-xl font-semibold mb-4">My Credentials</h2>
          <div className="space-y-4">
            {loading ? (
              <div className="animate-pulse space-y-4">
                {[...Array(3)].map((_, i) => (
                  <div key={i} className="bg-gray-100 rounded-lg p-4">
                    <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
                    <div className="h-3 bg-gray-200 rounded w-1/2"></div>
                  </div>
                ))}
              </div>
            ) : error ? (
              <div className="text-center py-8">
                <div className="text-red-500 mb-2">Error loading credentials</div>
                <button 
                  onClick={loadDashboardData}
                  className="text-purple-600 hover:text-purple-800"
                >
                  Try Again
                </button>
              </div>
            ) : credentials.length === 0 ? (
              <div className="text-center py-8 bg-gray-50 rounded-lg">
                <DocumentIcon className="h-12 w-12 mx-auto text-gray-400 mb-4" />
                <p className="text-gray-600 mb-4">No credentials yet</p>
                <Button
                  onClick={() => setShowRequestModal(true)}
                  className="bg-purple-600 hover:bg-purple-700 text-white"
                >
                  Upload Your First Credential
                </Button>
              </div>
            ) : (
              credentials.map((credential) => (
                <Card key={credential._id} className="p-4 hover:shadow-md transition-shadow duration-200">
                  <div className="flex justify-between items-start">
                    <div className="space-y-2">
                      <h3 className="font-medium text-gray-900">{credential.title}</h3>
                      <p className="text-sm text-gray-500">{credential.institution}</p>
                      <p className="text-sm text-gray-500">
                        Submitted on {new Date(credential.createdAt).toLocaleDateString()}
                      </p>
                      <div className="flex items-center gap-2">
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium
                          ${credential.status === 'verified' ? 'bg-green-100 text-green-800' : 
                            credential.status === 'rejected' ? 'bg-red-100 text-red-800' :
                            'bg-yellow-100 text-yellow-800'}`
                        }>
                          {credential.status === 'verified' ? 'Verified' : 
                           credential.status === 'rejected' ? 'Rejected' : 
                           'Pending'}
                        </span>
                        {credential.verified && (
                          <CheckCircleIcon className="h-5 w-5 text-green-500" />
                        )}
                      </div>
                    </div>
                    {credential.document_hash && (
                      <button
                        onClick={() => downloadDocument(credential.document_hash)}
                        className="text-blue-600 hover:text-blue-800 transition-colors"
                        title="Download Document"
                      >
                        <DocumentIcon className="h-6 w-6" />
                      </button>
                    )}
                  </div>
                  {credential.notes && (
                    <p className="mt-2 text-sm text-gray-600">{credential.notes}</p>
                  )}
                </Card>
              ))
            )}
          </div>
        </section>

        {/* Experiences Section */}
        <section>
          <h2 className="text-xl font-semibold mb-4">My Experiences</h2>
          <div className="space-y-4">
            {loading ? (
              <div className="animate-pulse space-y-4">
                {[...Array(2)].map((_, i) => (
                  <div key={i} className="bg-gray-100 rounded-lg p-4">
                    <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
                    <div className="h-3 bg-gray-200 rounded w-1/2"></div>
                  </div>
                ))}
              </div>
            ) : error ? (
              <div className="text-center py-8">
                <div className="text-red-500 mb-2">Error loading experiences</div>
                <button 
                  onClick={loadDashboardData}
                  className="text-blue-600 hover:text-blue-800"
                >
                  Try Again
                </button>
              </div>
            ) : experiences.length === 0 ? (
              <div className="text-center py-8 bg-gray-50 rounded-lg">
                <BriefcaseIcon className="h-12 w-12 mx-auto text-gray-400 mb-4" />
                <p className="text-gray-600 mb-4">No experiences yet</p>
                <Button
                  onClick={() => setShowExperienceModal(true)}
                  className="bg-blue-600 hover:bg-blue-700 text-white"
                >
                  Add Your First Experience
                </Button>
              </div>
            ) : (
              experiences.map((experience) => (
                <Card key={experience._id} className="p-4 hover:shadow-md transition-shadow duration-200">
                  <div className="flex justify-between items-start">
                    <div className="space-y-2">
                      <h3 className="font-medium text-gray-900">{experience.position}</h3>
                      <p className="text-sm text-gray-500">{experience.company}</p>
                      <p className="text-sm text-gray-500">
                        {new Date(experience.start_date).toLocaleDateString()} - 
                        {experience.end_date ? new Date(experience.end_date).toLocaleDateString() : 'Present'}
                      </p>
                      <div className="flex items-center gap-2">
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium
                          ${experience.status === 'verified' ? 'bg-green-100 text-green-800' : 
                            experience.status === 'rejected' ? 'bg-red-100 text-red-800' :
                            'bg-yellow-100 text-yellow-800'}`
                        }>
                          {experience.status === 'verified' ? 'Verified' : 
                           experience.status === 'rejected' ? 'Rejected' : 
                           'Pending'}
                        </span>
                        {experience.verified && (
                          <CheckCircleIcon className="h-5 w-5 text-green-500" />
                        )}
                      </div>
                    </div>
                    {experience.document_hash && (
                      <button
                        onClick={() => downloadDocument(experience.document_hash)}
                        className="text-blue-600 hover:text-blue-800 transition-colors"
                        title="Download Document"
                      >
                        <DocumentIcon className="h-6 w-6" />
                      </button>
                    )}
                  </div>
                  {experience.description && (
                    <p className="mt-2 text-sm text-gray-600">{experience.description}</p>
                  )}
                </Card>
              ))
            )}
          </div>
        </section>
      </div>

      {/* Modals */}
      {showRequestModal && (
        <RequestCredentialModal
          onSubmit={handleRequestCredential}
          onClose={() => setShowRequestModal(false)}
          loading={uploadingDoc}
          error={error}
        />
      )}

      {showExperienceModal && (
        <RequestExperienceModal
          onSubmit={handleRequestExperience}
          onClose={() => setShowExperienceModal(false)}
          loading={uploadingDoc}
          error={error}
        />
      )}
    </div>
  );
}
