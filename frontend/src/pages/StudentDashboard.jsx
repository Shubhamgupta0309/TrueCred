import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useAuth } from '../context/AuthContext.jsx';
import DashboardHeader from '../components/dashboard/DashboardHeader';
import CredentialsList from '../components/dashboard/CredentialsList';
import ExperienceList from '../components/dashboard/ExperienceList';
import ActionButtons from '../components/dashboard/ActionButtons';
import NotificationPanel from '../components/dashboard/NotificationPanel';
import BlockchainTokenDisplay from '../components/blockchain/BlockchainTokenDisplay';
import ProfileCompletion from '../components/profile/ProfileCompletion';
import ProfileCard from '../components/profile/ProfileCard';
import withAuthErrorHandling from '../components/withAuthErrorHandling';
import AuthenticationModal from '../components/common/AuthenticationModal';
import { credentialService, experienceService, notificationService } from '../services/api';
import StudentSearch from '../components/organization/StudentSearch';

// Mock Data - will be replaced with API calls
// start with empty data; will fetch from API
const mockCredentials = [];
const mockExperiences = [];
const mockNotifications = [];

// Normalize credential array into UI-friendly shape and deduplicate by a stable id.
// If backend doesn't provide an id, fall back to base64 of title|date so repeated fetches produce same id.
const normalizeCredentials = (arr) => {
  const map = new Map();
  (arr || []).forEach((c) => {
    let id = c.id || c._id || c.id_str || c._id_str || (c._id && String(c._id)) || null;
    const title = c.title || c.name || 'Untitled Credential';
    const date = c.issue_date || c.created_at || c.updated_at || c.timestamp || null;
    const status = c.status || c.verification_status || (c.verified ? 'verified' : (c.pending_verification ? 'pending' : 'unverified')) || 'unknown';

    if (!id) {
      // Create a stable fallback id from title+date
      try {
        const key = `${title}::${date || ''}`;
        // base64-encode for compact id
        id = btoa(unescape(encodeURIComponent(key)));
      } catch (e) {
        id = `${title.replace(/[^a-z0-9]/gi, '_')}_${date || 'na'}`;
      }
    }

    // Avoid overwriting an existing entry with less specific data
    if (!map.has(id)) {
      map.set(id, { id, title, date, status, raw: c });
    }
  });

  return Array.from(map.values()).map((v) => ({ ...v.raw, id: v.id, title: v.title, date: v.date, status: v.status }));
};

function StudentDashboard({ onAuthError }) {
  const { user } = useAuth();
  const [credentials, setCredentials] = useState(mockCredentials);
  const [experiences, setExperiences] = useState(mockExperiences);
  const [notifications, setNotifications] = useState(mockNotifications);
  const [loading, setLoading] = useState(true);
  const [credentialError, setCredentialError] = useState(null);
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [needsProfileCompletion, setNeedsProfileCompletion] = useState(false);
  const [viewMode, setViewMode] = useState('list'); // 'list' or 'blockchain'
  const [selectedStudent, setSelectedStudent] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');
  const [pendingRequests, setPendingRequests] = useState([]);
  
  // Format the user data for the header
  const userForHeader = {
    name: user?.first_name && user?.last_name 
      ? `${user.first_name} ${user.last_name}` 
      : user?.username || 'Student',
    email: user?.email || '',
    role: 'Student',
    truecred_id: user?.truecred_id || 'TC000000'
  };

  // Fetch user data from API
  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      
      try {
        // Check if profile needs completion (either missing names or profile_completed flag false)
        if (user) {
          if (!user.first_name || !user.last_name || user.profile_completed === false) {
            setNeedsProfileCompletion(true);
                      {credentialError ? (
                        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
                          <p className="text-red-700 font-medium">Failed to load credentials</p>
                          <p className="text-sm text-red-600 mt-1">{credentialError}</p>
                        </div>
                      ) : (
                        <div className="bg-white rounded-xl shadow-md p-6 mb-6">
                          <h2 className="text-lg font-bold text-gray-800 mb-2">My Credentials</h2>
                          {pendingRequests && pendingRequests.length > 0 ? (
                            <ul className="space-y-2">
                              {pendingRequests.map(req => (
                                <li key={req.id || req._id} className="p-2 border rounded hover:bg-gray-50">
                                  <div className="flex justify-between">
                                    <div>
                                      <div className="font-medium text-gray-800">{req.title || req.metadata?.institution || 'Credential'}</div>
                                      <div className="text-sm text-gray-500">{req.issuer || req.metadata?.institution || ''}</div>
                                    </div>
                                    <div className={`text-sm ${req.status==='pending'?'text-yellow-600':req.status==='issued'?'text-green-600':'text-red-600'}`}>{req.status || 'pending'}</div>
                                  </div>
                                </li>
                              ))}
                            </ul>
                          ) : (
                            <div className="text-gray-500 text-center py-8">No credentials found.</div>
                          )}
                        </div>
                      )}
            setCredentialError('Unknown error fetching credentials');
          }
        }

        // Fetch pending credential requests for this user
        try {
          const pendingResp = await credentialService.getUserRequests();
          console.debug('GET /api/user/requests response:', pendingResp);
          if (pendingResp.data && pendingResp.data.success) {
            // backend returns list of requests under data.requests or data
            const reqs = pendingResp.data.data?.requests || pendingResp.data.requests || pendingResp.data || [];
            setPendingRequests(reqs || []);
          } else {
            console.warn('Unexpected user requests response shape', pendingResp && pendingResp.data);
          }
        } catch (pendingError) {
          console.error('Error fetching user pending requests:', pendingError);
          if (pendingError.response) {
            console.error('User requests API Error response data:', pendingError.response.status, pendingError.response.data);
          }
        }

        // Fetch issued credentials
        try {
          const credResponse = await credentialService.getCredentials();
          console.debug('GET /api/credentials response:', credResponse);
          if (credResponse.data && credResponse.data.success) {
            // Normalize the credentials data
            const creds = credResponse.data.data?.credentials || credResponse.data.credentials || credResponse.data || [];
            const normalizedCreds = normalizeCredentials(creds);
            setCredentials(normalizedCreds);
          } else {
            console.warn('Unexpected credentials response shape', credResponse && credResponse.data);
          }
        } catch (credError) {
          console.error('Error fetching credentials:', credError);
          setCredentialError(credError.response?.data?.message || 'Failed to load credentials');
          if (credError.response) {
            console.error('Credentials API Error response data:', credError.response.status, credError.response.data);
          }
        }
        
        // Fetch experiences
        try {
          const expResponse = await experienceService.getExperiences();
          if (expResponse.data && expResponse.data.success) {
            setExperiences(expResponse.data.data || expResponse.data.experiences || []);
          }
        } catch (expError) {
          console.error('Error fetching experiences:', expError);
        }
        
        // Fetch notifications
        try {
          const notifResponse = await notificationService.getNotifications();
          if (notifResponse.data && notifResponse.data.success) {
            setNotifications(notifResponse.data.data.notifications || notifResponse.data.notifications || []);
          }
        } catch (notifError) {
          console.error('Error fetching notifications:', notifError);
        }
        
        setLoading(false);
      } catch (error) {
        // Check if it's an auth error and let the HOC handle it
        if (onAuthError && !onAuthError(error)) {
          console.error('Error fetching dashboard data:', error);
        }
        setLoading(false);
      }
    };

    fetchData();
  }, [onAuthError, user]);

  // Handle verification status updates
  const handleVerificationUpdate = (credentialId, newStatus, verificationData) => {
    setCredentials(prevCredentials => 
      prevCredentials.map(cred => 
        cred.id === credentialId 
          ? { ...cred, status: newStatus, blockchain_data: verificationData }
          : cred
      )
    );
  };

  // Handle authentication errors specifically in ActionButtons
  const handleActionError = (error) => {
    if (error?.response?.status === 401) {
      setShowAuthModal(true);
      return true; // Handled
    }
    return false; // Not handled
  };

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
      },
    },
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 },
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-purple-100 p-4 md:p-8 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-purple-600 mx-auto"></div>
          <p className="mt-4 text-gray-700">Loading your dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-purple-100 p-4 md:p-8">
      {/* Background decoration */}
      <div className="absolute inset-0 overflow-hidden -z-10">
        <div className="absolute -top-60 -right-60 w-96 h-96 bg-purple-200 rounded-full opacity-30 blur-3xl"></div>
        <div className="absolute -bottom-60 -left-60 w-96 h-96 bg-purple-300 rounded-full opacity-30 blur-3xl"></div>
      </div>
      
      <div className="max-w-7xl mx-auto">
        {/* Show profile completion if needed */}
        {needsProfileCompletion ? (
          <ProfileCompletion 
            onComplete={() => setNeedsProfileCompletion(false)} 
          />
        ) : (
          <>
            <DashboardHeader user={userForHeader} />
            
            {/* View mode toggle and tabs */}
            <div className="flex justify-center mb-6">
              <div className="bg-white rounded-full p-1 shadow-sm inline-flex">
                <button
                  onClick={() => setViewMode('list')}
                  className={`px-4 py-2 rounded-full ${
                    viewMode === 'list' 
                      ? 'bg-purple-600 text-white' 
                      : 'text-gray-700 hover:bg-gray-100'
                  }`}
                >
                  List View
                </button>
                <button
                  onClick={() => setViewMode('blockchain')}
                  className={`px-4 py-2 rounded-full ${
                    viewMode === 'blockchain' 
                      ? 'bg-purple-600 text-white' 
                      : 'text-gray-700 hover:bg-gray-100'
                  }`}
                >
                  Blockchain View
                </button>
              </div>
            </div>

            <div className="bg-white shadow-sm rounded-lg mb-8">
              <div className="flex border-b">
                <button className={`py-3 px-6 focus:outline-none ${activeTab === 'overview' ? 'border-b-2 border-purple-600 text-purple-700' : 'text-gray-500 hover:text-purple-500'}`} onClick={() => setActiveTab('overview')}>Overview</button>
                <button className={`py-3 px-6 focus:outline-none ${activeTab === 'profile' ? 'border-b-2 border-purple-600 text-purple-700' : 'text-gray-500 hover:text-purple-500'}`} onClick={() => setActiveTab('profile')}>Profile</button>
              </div>
            </div>

            <motion.div
              variants={containerVariants}
              initial="hidden"
              animate="visible"
              className="grid grid-cols-1 lg:grid-cols-3 gap-8"
            >
              {/* Left Column */}
              <motion.div variants={itemVariants} className="lg:col-span-2 space-y-8">
                {activeTab === 'overview' ? (
                  viewMode === 'list' ? (
                    <>
                              {/* Credential Requests panel (grouped by status) */}
                              {pendingRequests && pendingRequests.length > 0 && (
                                <div className="bg-white rounded-xl shadow-md p-6 mb-6">
                                  <h2 className="text-lg font-bold text-gray-800 mb-2">Your Credential Requests</h2>
                                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                    {['pending','issued','rejected'].map((statusKey) => (
                                      <div key={statusKey} className="p-4 border rounded">
                                        <h3 className="text-sm font-semibold text-gray-700 capitalize mb-2">{statusKey}</h3>
                                        <ul className="space-y-2">
                                          {pendingRequests.filter(r => (r.status || '').toLowerCase() === statusKey).map(req => (
                                            <li key={req.id || req._id} className="p-2 border rounded hover:bg-gray-50">
                                              <div className="flex justify-between">
                                                <div>
                                                  <div className="font-medium text-gray-800">{req.title || req.metadata?.institution || 'Requested Credential'}</div>
                                                  <div className="text-sm text-gray-500">{req.issuer || req.metadata?.institution || ''}</div>
                                                </div>
                                                <div className={`text-sm ${statusKey==='pending'?'text-yellow-600':statusKey==='issued'?'text-green-600':'text-red-600'}`}>{statusKey}</div>
                                              </div>
                                            </li>
                                          ))}
                                        </ul>
                                      </div>
                                    ))}
                                  </div>
                                </div>
                              )}

                      {credentialError ? (
                        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
                          <p className="text-red-700 font-medium">Failed to load credentials</p>
                          <p className="text-sm text-red-600 mt-1">{credentialError}</p>
                        </div>
                      ) : (
                        <CredentialsList 
                          credentials={credentials} 
                          onVerificationUpdate={handleVerificationUpdate} 
                        />
                      )}
                      <ExperienceList experiences={experiences} />
                    </>
                  ) : (
                    <div className="bg-white rounded-xl shadow-md p-6">
                      <h2 className="text-xl font-bold text-gray-800 mb-4">Blockchain Credentials</h2>
                      <div className="space-y-4">
                        {credentials.length > 0 ? (
                          credentials.map(credential => (
                            <BlockchainTokenDisplay 
                              key={credential.id} 
                              credential={credential}
                              onVerificationUpdate={handleVerificationUpdate}
                            />
                          ))
                        ) : (
                          <p className="text-gray-500 text-center py-8">
                            No blockchain credentials found. Your verified credentials will appear here.
                          </p>
                        )}
                      </div>
                    </div>
                  )
                ) : activeTab === 'profile' ? (
                  <div>
                    {user?.profile_completed ? (
                      <div className="bg-white rounded-xl shadow-md p-6">
                        <h2 className="text-xl font-bold text-gray-800 mb-4">Your Profile</h2>
                        {user?.profile_completed && (
                          <span className="inline-block bg-green-100 text-green-800 px-3 py-1 rounded mb-4">Profile Complete</span>
                        )}
                        <div className="space-y-4">
                          <div>
                            <h3 className="text-lg font-semibold text-gray-700 mb-2">Personal Information</h3>
                            <p className="text-gray-600"><strong>Name:</strong> {user?.first_name} {user?.last_name}</p>
                            <p className="text-gray-600"><strong>Email:</strong> {user?.email}</p>
                          </div>
                          {user?.education && user.education.length > 0 && (
                            <div>
                              <h3 className="text-lg font-semibold text-gray-700 mb-2">Education</h3>
                              <div className="space-y-3">
                                {user.education.map((edu, idx) => (
                                  <div key={idx} className="bg-gray-50 p-4 rounded-lg">
                                    <div className="font-medium text-gray-800">{edu.degree} in {edu.field_of_study}</div>
                                    <div className="text-sm text-gray-600">{edu.institution}</div>
                                    <div className="text-sm text-gray-500">
                                      {edu.start_date} - {edu.current ? 'Present' : edu.end_date}
                                    </div>
                                  </div>
                                ))}
                              </div>
                            </div>
                          )}
                        </div>
                        <div className="mt-6">
                          <a href="/profile" className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">
                            Edit Profile
                          </a>
                        </div>
                      </div>
                    ) : (
                      <ProfileCompletion onComplete={() => setNeedsProfileCompletion(false)} />
                    )}
                  </div>
                ) : null}
              </motion.div>

              {/* Right Column */}
              <motion.div variants={itemVariants} className="space-y-8">
                <div className="bg-white rounded-xl shadow-md p-6">
                  <h2 className="text-xl font-bold text-gray-800 mb-4">Your TrueCred ID</h2>
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                    <p className="text-2xl font-mono text-blue-700">{userForHeader.truecred_id}</p>
                    <p className="text-sm text-blue-600 mt-2">
                      Share this ID with organizations that need to issue credentials to you.
                    </p>
                  </div>
                </div>
                <StudentSearch onStudentSelect={(s) => setSelectedStudent(s)} />
                <ProfileCard student={selectedStudent} currentUser={user} onEditRequest={(s) => console.log('edit request', s)} />
                <ActionButtons onAuthError={handleActionError} onSuccess={() => {
                  // Re-fetch dashboard data after actions succeed
                  (async () => {
                    setLoading(true);
                    try {
                      const [credResponse, pendingResp, expResponse, notifResponse] = await Promise.all([
                        credentialService.getCredentials().catch(e => e),
                        credentialService.getUserRequests().catch(e => e),
                        experienceService.getExperiences().catch(e => e),
                        notificationService.getNotifications().catch(e => e)
                      ]);

                                if (credResponse && credResponse.data && credResponse.data.success) {
                                  const rawCreds = credResponse.data.data || credResponse.data.credentials || [];
                                  setCredentials(normalizeCredentials(rawCreds));
                                }
                      if (pendingResp && pendingResp.data && pendingResp.data.success) {
                        setPendingRequests(pendingResp.data.data?.requests || pendingResp.data.requests || pendingResp.data || []);
                      }
                      if (expResponse && expResponse.data && expResponse.data.success) {
                        setExperiences(expResponse.data.data || expResponse.data.experiences || []);
                      }
                      if (notifResponse && notifResponse.data && notifResponse.data.success) {
                        setNotifications(notifResponse.data.data.notifications || notifResponse.data.notifications || []);
                      }
                    } catch (e) {
                      console.error('Failed to refresh dashboard after action', e);
                    } finally {
                      setLoading(false);
                    }
                  })();
                }} />
                <NotificationPanel notifications={notifications} />
              </motion.div>
            </motion.div>
          </>
        )}
      </div>
      
      {/* Authentication Modal */}
      <AuthenticationModal 
        isOpen={showAuthModal} 
        onClose={() => setShowAuthModal(false)}
        onRefresh={() => window.location.reload()}
      />
    </div>
  );
}

// Export the component wrapped with auth error handling
export default withAuthErrorHandling(StudentDashboard);