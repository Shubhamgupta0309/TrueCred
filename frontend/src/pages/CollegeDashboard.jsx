import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from '../context/AuthContext.jsx';
import { useToast } from '../context/ToastContext.jsx';
import DashboardHeader from '../components/dashboard/DashboardHeader';
import SearchFilterPanel from '../components/college/SearchFilterPanel';
import PendingRequests from '../components/college/PendingRequests';
import VerificationHistory from '../components/college/VerificationHistory';
import NotificationPanel from '../components/dashboard/NotificationPanel';
import CredentialIssuanceContainer from '../components/CredentialIssuanceContainer';
import StudentSearch from '../components/organization/StudentSearch';
import StudentCredentialUpload from '../components/organization/StudentCredentialUpload';
import ProfileCard from '../components/profile/ProfileCard';
import CollegeProfileForm from '../components/college/CollegeProfileForm';
import { api, notificationService } from '../services/api';

export default function CollegeDashboard() {
  const { user } = useAuth();
  const { success, error: toastError } = useToast();
  const [pendingRequests, setPendingRequests] = useState([]);
  const [history, setHistory] = useState([]);
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('requests');
  const [error, setError] = useState(null);
  const [selectedStudent, setSelectedStudent] = useState(null);
  const [collegeProfile, setCollegeProfile] = useState(null);
  
  // Format the user data for the header
  const userForHeader = {
    name: user?.first_name && user?.last_name 
      ? `${user.first_name} ${user.last_name}` 
      : user?.username || 'College Admin',
    email: user?.email || '',
    role: 'College'
  };
  
  // Fetch dashboard data from API
  useEffect(() => {
    const fetchDashboardData = async () => {
      setLoading(true);
      setError(null);

      try {
        // Fetch pending requests from API
        const pendingResponse = await api.get('/api/college/pending-requests');

        // Check if we got valid data
        const requestsData = pendingResponse.data.requests || [];

        if (requestsData.length === 0) {
          setPendingRequests([]);
        } else {
          // Transform the data to match expected format for backward compatibility
          const transformedRequests = requestsData.map(req => ({
            id: req.id,
            user_id: req.user_id,
            title: req.title,
            studentName: req.student_name || 'Unknown Student',
            studentEmail: req.student_email || '',
            institutionName: req.institution_name || req.issuer || 'Not specified',
            credentialTitle: req.title || 'Untitled Credential',
            submissionDate: req.created_at ? new Date(req.created_at).toLocaleDateString() : 'Unknown',
            status: req.status,
            type: req.type,
            issuer: req.issuer,
            attachments: req.attachments || [],  // Include attachments for document viewing
            education_info: req.education_info || []
          }));

          setPendingRequests(transformedRequests);
        }

        // Remove college verification history API call
        setHistory([]);

        // Fetch notifications
        const notificationsResponse = await notificationService.getNotifications();
        setNotifications(notificationsResponse.data.data.notifications || []);

      } catch (err) {
        console.error('Error fetching dashboard data:', err);
        setError('Failed to load dashboard data. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  const handleAction = async (requestId, newStatus) => {
    // Update the local state immediately for better UX
    setPendingRequests(prevRequests =>
      prevRequests.filter(req => req.id !== requestId)
    );

    // Add to history if it's an approval
    if (newStatus === 'Issued') {
      // Find the request that was just approved to add to history
      const approvedRequest = pendingRequests.find(req => req.id === requestId);
      if (approvedRequest) {
        const historyItem = {
          id: requestId,
          studentName: approvedRequest.studentName || approvedRequest.student_name || 'Unknown Student',
          credentialTitle: approvedRequest.title || approvedRequest.credentialTitle || 'Unknown Credential',
          status: newStatus,
          actionDate: new Date().toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
            year: 'numeric'
          }),
          institutionName: approvedRequest.institutionName || approvedRequest.institution_name || approvedRequest.issuer || 'Unknown Institution'
        };

        setHistory(prevHistory => [historyItem, ...prevHistory]);
      }
    }

    // Show success message
    const message = newStatus === 'Issued' ? 'Request approved successfully!' : 'Request rejected successfully!';
    success(message);

    // Optional: Refresh data from server to ensure consistency
    try {
      const response = await api.get('/college/pending-requests');
      if (response.data && response.data.requests) {
        setPendingRequests(response.data.requests);
      }
    } catch (err) {
      console.error('Failed to refresh pending requests:', err);
      // Don't show error to user since local update already happened
    }
  };

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: { opacity: 1, transition: { staggerChildren: 0.1 } },
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 },
  };

  const handleCredentialIssued = (credential) => {
    // Refresh the history data to include the newly issued credential
    api.get('/college/verification-history')
      .then(response => {
        if (response.data && response.data.history) {
          setHistory(response.data.history);
        }
      })
      .catch(err => {
        console.error('Failed to refresh history after credential issuance:', err);
        
        // Fallback: Add to history manually if API call fails
        setHistory(prevHistory => [
          {
            id: credential.id || Math.random().toString(36).substr(2, 9),
            studentName: credential.recipientEmail.split('@')[0],
            credentialTitle: credential.title,
            status: 'Issued',
            actionDate: new Date().toLocaleDateString('en-US', { 
              month: 'short', 
              day: 'numeric', 
              year: 'numeric' 
            })
          },
          ...prevHistory
        ]);
      });
  };

  const handleProfileUpdate = (profile) => {
    setCollegeProfile(profile);
    // Update user for header if needed
    if (profile.name) {
      userForHeader.organization = profile.name;
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-indigo-100 p-4 md:p-8 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-purple-600 mx-auto"></div>
          <p className="mt-4 text-gray-700">Loading your dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-indigo-100 p-4 md:p-8 flex items-center justify-center">
        <div className="bg-white shadow-md rounded-lg p-8 max-w-md w-full">
          <div className="text-center">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-12 w-12 mx-auto text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <h2 className="mt-4 text-xl font-bold text-gray-800">Error Loading Dashboard</h2>
            <p className="mt-2 text-gray-600">{error}</p>
            <button 
              onClick={() => window.location.reload()}
              className="mt-6 px-4 py-2 bg-purple-600 text-white rounded hover:bg-purple-700 transition-colors"
            >
              Retry
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-indigo-100 p-4 md:p-8">
      <div className="max-w-7xl mx-auto">
        <DashboardHeader user={userForHeader} />

        {/* Tab Navigation */}
        <div className="bg-white shadow-sm rounded-lg mb-8">
          <div className="flex border-b">
            <button
              className={`py-3 px-6 focus:outline-none ${
                activeTab === 'requests'
                  ? 'border-b-2 border-purple-600 text-purple-700'
                  : 'text-gray-500 hover:text-purple-500'
              }`}
              onClick={() => setActiveTab('requests')}
            >
              Pending Requests
            </button>
            <button
              className={`py-3 px-6 focus:outline-none ${
                activeTab === 'issue'
                  ? 'border-b-2 border-purple-600 text-purple-700'
                  : 'text-gray-500 hover:text-purple-500'
              }`}
              onClick={() => setActiveTab('issue')}
            >
              Issue Credentials
            </button>
            <button
              className={`py-3 px-6 focus:outline-none ${
                activeTab === 'profile'
                  ? 'border-b-2 border-purple-600 text-purple-700'
                  : 'text-gray-500 hover:text-purple-500'
              }`}
              onClick={() => setActiveTab('profile')}
            >
              College Profile
            </button>
          </div>
        </div>

        <AnimatePresence mode="wait">
          {activeTab === 'requests' ? (
            <motion.div
              key="requests"
              variants={containerVariants}
              initial="hidden"
              animate="visible"
              exit={{ opacity: 0 }}
              className="grid grid-cols-1 lg:grid-cols-3 gap-8"
            >
              {/* Main Column */}
              <div className="lg:col-span-2 space-y-8">
                <motion.div variants={itemVariants}>
                  <SearchFilterPanel />
                </motion.div>
                <motion.div variants={itemVariants}>
                  <PendingRequests requests={pendingRequests} onAction={handleAction} />
                </motion.div>
              </div>

              {/* Right Column */}
              <div className="space-y-8">
                <motion.div variants={itemVariants}>
                  <VerificationHistory history={history} />
                </motion.div>
                <motion.div variants={itemVariants}>
                  <ProfileCard student={selectedStudent} currentUser={user} onEditRequest={(s) => console.log('edit request', s)} />
                </motion.div>
                <motion.div variants={itemVariants}>
                  <NotificationPanel notifications={notifications} />
                </motion.div>
              </div>
            </motion.div>
          ) : activeTab === 'issue' ? (
            <motion.div
              key="issue"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="grid grid-cols-1 lg:grid-cols-3 gap-8"
            >
              {/* Main Column */}
              <div className="lg:col-span-2">
                <CredentialIssuanceContainer onCredentialIssued={handleCredentialIssued} />
              </div>

              {/* Right Column */}
              <div className="space-y-8">
                <motion.div variants={itemVariants}>
                  <VerificationHistory history={history} />
                </motion.div>
                <motion.div variants={itemVariants}>
                  <NotificationPanel notifications={notifications} />
                </motion.div>
              </div>
            </motion.div>
          ) : (
            <motion.div
              key="profile"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="grid grid-cols-1 lg:grid-cols-3 gap-8"
            >
              {/* Main Column */}
              <div className="lg:col-span-2">
                <CollegeProfileForm user={user} onUpdate={handleProfileUpdate} />
              </div>

              {/* Right Column */}
              <div className="space-y-8">
                <motion.div variants={itemVariants}>
                  <div className="bg-white rounded-2xl shadow-lg shadow-purple-500/10 p-6">
                    <h3 className="text-lg font-bold text-gray-800 mb-4">Why Complete Your Profile?</h3>
                    <ul className="space-y-3">
                      <li className="flex items-start">
                        <span className="bg-green-100 rounded-full p-1 mr-2 mt-0.5">
                          <svg className="h-4 w-4 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                          </svg>
                        </span>
                        <span className="text-gray-700">Enables students to easily find your institution</span>
                      </li>
                      <li className="flex items-start">
                        <span className="bg-green-100 rounded-full p-1 mr-2 mt-0.5">
                          <svg className="h-4 w-4 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                          </svg>
                        </span>
                        <span className="text-gray-700">Adds credibility to issued certificates</span>
                      </li>
                      <li className="flex items-start">
                        <span className="bg-green-100 rounded-full p-1 mr-2 mt-0.5">
                          <svg className="h-4 w-4 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                          </svg>
                        </span>
                        <span className="text-gray-700">Improves verification process efficiency</span>
                      </li>
                      <li className="flex items-start">
                        <span className="bg-green-100 rounded-full p-1 mr-2 mt-0.5">
                          <svg className="h-4 w-4 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                          </svg>
                        </span>
                        <span className="text-gray-700">Ensures correct institution details on certificates</span>
                      </li>
                    </ul>
                  </div>
                </motion.div>
                <motion.div variants={itemVariants}>
                  <NotificationPanel notifications={notifications} />
                </motion.div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}