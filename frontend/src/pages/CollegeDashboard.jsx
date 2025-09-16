import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from '../context/AuthContext.jsx';
import DashboardHeader from '../components/dashboard/DashboardHeader';
import SearchFilterPanel from '../components/college/SearchFilterPanel';
import PendingRequests from '../components/college/PendingRequests';
import VerificationHistory from '../components/college/VerificationHistory';
import NotificationPanel from '../components/dashboard/NotificationPanel';
import CredentialIssuanceContainer from '../components/CredentialIssuanceContainer';
import StudentSearch from '../components/organization/StudentSearch';
import StudentCredentialUpload from '../components/organization/StudentCredentialUpload';
import CollegeProfileForm from '../components/college/CollegeProfileForm';
import { api, notificationService } from '../services/api';

export default function CollegeDashboard() {
  const { user } = useAuth();
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
        // Use try/catch for each API call to handle individual failures
        try {
          // Fetch pending requests
          const requestsResponse = await api.get('/college/pending-requests');
          setPendingRequests(requestsResponse.data.requests || []);
        } catch (requestsErr) {
          console.error('Error fetching pending requests:', requestsErr);
          
          // Use mock data in development mode
          if (import.meta.env.DEV) {
            console.warn('Development mode: Using mock pending requests');
            setPendingRequests([
              { id: 1, studentName: 'Alex Doe', credentialTitle: 'B.Sc. Computer Science Degree', submissionDate: 'Nov 20, 2023' },
              { id: 2, studentName: 'Jane Smith', credentialTitle: 'Data Science Certification', submissionDate: 'Nov 18, 2023' },
              { id: 3, studentName: 'Mike Johnson', credentialTitle: 'Mechanical Engineering Diploma', submissionDate: 'Nov 15, 2023' },
            ]);
          } else {
            throw requestsErr;
          }
        }
        
        try {
          // Fetch verification history
          const historyResponse = await api.get('/college/verification-history');
          setHistory(historyResponse.data.history || []);
        } catch (historyErr) {
          console.error('Error fetching verification history:', historyErr);
          
          // Use mock data in development mode
          if (import.meta.env.DEV) {
            console.warn('Development mode: Using mock verification history');
            setHistory([
              { id: 101, studentName: 'Emily White', credentialTitle: 'Graphic Design Certificate', status: 'Verified', actionDate: 'Nov 14, 2023' },
              { id: 102, studentName: 'David Green', credentialTitle: 'Business Administration Degree', status: 'Rejected', actionDate: 'Nov 12, 2023' },
            ]);
          } else {
            throw historyErr;
          }
        }
        
        try {
          // Fetch notifications
          const notificationsResponse = await notificationService.getNotifications();
          setNotifications(notificationsResponse.data.data.notifications || []);
        } catch (notificationsErr) {
          console.error('Error fetching notifications:', notificationsErr);
          
          // Use mock data in development mode
          if (import.meta.env.DEV) {
            console.warn('Development mode: Using mock notifications');
            setNotifications([
              { id: 1, type: 'info', message: '3 new verification requests are pending.', time: 'Just now' },
              { id: 2, type: 'alert', message: 'System maintenance scheduled for this weekend.', time: '1 day ago' },
            ]);
          } else {
            throw notificationsErr;
          }
        }
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
    try {
      // Call API to update the request status
      const response = await api.post(`/college/verification-requests/${requestId}`, {
        status: newStatus
      });
      
      if (response.data.success) {
        // Update local state - remove from pending requests
        setPendingRequests(prevRequests => 
          prevRequests.filter(req => req.id !== requestId)
        );
        
        // Add to history with the updated status
        const requestToMove = pendingRequests.find(req => req.id === requestId);
        if (requestToMove) {
          setHistory(prevHistory => [
            {
              ...requestToMove,
              status: newStatus,
              actionDate: new Date().toLocaleDateString('en-US', { 
                month: 'short', 
                day: 'numeric', 
                year: 'numeric' 
              })
            },
            ...prevHistory
          ]);
        }
      }
    } catch (err) {
      console.error('Error updating request status:', err);
      alert(`Failed to ${newStatus.toLowerCase()} the request. Please try again.`);
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