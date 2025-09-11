import React, { useState, useEffect } from 'react';
import { credentialService, experienceService } from '../services/api';
import { useNavigate } from 'react-router-dom';

import RequestCredentialModal from '../components/modals/RequestCredentialModal';
import RequestExperienceModal from '../components/modals/RequestExperienceModal';

const StudentDashboard = () => {
  const [credentials, setCredentials] = useState([]);
  const [experiences, setExperiences] = useState([]);
  const [loading, setLoading] = useState({ credentials: true, experiences: true });
  const [error, setError] = useState({ credentials: null, experiences: null });
  const [showCredentialModal, setShowCredentialModal] = useState(false);
  const [showExperienceModal, setShowExperienceModal] = useState(false);

  const navigate = useNavigate();

  useEffect(() => {
    const fetchCredentials = async () => {
      try {
        const response = await credentialService.getCredentials();
        setCredentials(response.data || []);
      } catch (err) {
        setError(prev => ({ ...prev, credentials: err.message }));
      } finally {
        setLoading(prev => ({ ...prev, credentials: false }));
      }
    };

    const fetchExperiences = async () => {
      try {
        const response = await experienceService.getExperiences();
        setExperiences(response.data || []);
      } catch (err) {
        setError(prev => ({ ...prev, experiences: err.message }));
      } finally {
        setLoading(prev => ({ ...prev, experiences: false }));
      }
    };

    fetchCredentials();
    fetchExperiences();
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    localStorage.removeItem('userRole');
    navigate('/auth');
  };

  const handleRequestCredential = () => {
    setShowCredentialModal(true);
  };

  const handleAddExperience = () => {
    setShowExperienceModal(true);
  };

  const handleCredentialSuccess = async () => {
    try {
      const response = await credentialService.getCredentials();
      setCredentials(response.data || []);
    } catch (err) {
      setError(prev => ({ ...prev, credentials: err.message }));
    }
  };

  const handleExperienceSuccess = async () => {
    try {
      const response = await experienceService.getExperiences();
      setExperiences(response.data || []);
    } catch (err) {
      setError(prev => ({ ...prev, experiences: err.message }));
    }
  };

  const CredentialsList = () => (
    <div className="bg-white shadow-md rounded-lg p-4">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold">Credentials</h3>
        <button
          onClick={handleRequestCredential}
          className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded"
        >
          Request New Credential
        </button>
      </div>
      {loading.credentials ? (
        <div className="text-center py-4">Loading credentials...</div>
      ) : error.credentials ? (
        <div className="text-red-500 py-4">{error.credentials}</div>
      ) : credentials.length === 0 ? (
        <div className="text-gray-500 py-4">No credentials found</div>
      ) : (
        <div className="space-y-4">
          {credentials.map((credential) => (
            <div key={credential.id} className="border rounded p-4">
              <h4 className="font-semibold">{credential.title}</h4>
              <p className="text-gray-600">{credential.description}</p>
              <div className="mt-2">
                <span className={`px-2 py-1 rounded text-sm ${
                  credential.status === 'active' ? 'bg-green-100 text-green-800' :
                  credential.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                  'bg-red-100 text-red-800'
                }`}>
                  {credential.status}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );

  const ExperienceList = () => (
    <div className="bg-white shadow-md rounded-lg p-4 mt-6">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold">Experience Verification</h3>
        <button
          onClick={handleAddExperience}
          className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded"
        >
          Add New Experience
        </button>
      </div>
      {loading.experiences ? (
        <div className="text-center py-4">Loading experiences...</div>
      ) : error.experiences ? (
        <div className="text-red-500 py-4">{error.experiences}</div>
      ) : experiences.length === 0 ? (
        <div className="text-gray-500 py-4">No experience records found</div>
      ) : (
        <div className="space-y-4">
          {experiences.map((experience) => (
            <div key={experience.id} className="border rounded p-4">
              <h4 className="font-semibold">{experience.title}</h4>
              <p className="text-gray-600">{experience.company}</p>
              <p className="text-gray-500">{experience.duration}</p>
              <div className="mt-2">
                <span className={`px-2 py-1 rounded text-sm ${
                  experience.status === 'verified' ? 'bg-green-100 text-green-800' :
                  experience.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                  'bg-red-100 text-red-800'
                }`}>
                  {experience.status}
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
          <h2 className="text-2xl font-bold text-gray-900">Student Dashboard</h2>
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
          <CredentialsList />
          <ExperienceList />

          {/* Modals */}
          <RequestCredentialModal
            isOpen={showCredentialModal}
            onClose={() => setShowCredentialModal(false)}
            onSuccess={handleCredentialSuccess}
          />
          <RequestExperienceModal
            isOpen={showExperienceModal}
            onClose={() => setShowExperienceModal(false)}
            onSuccess={handleExperienceSuccess}
          />
        </div>
      </main>
    </div>
  );
};

export default StudentDashboard;
