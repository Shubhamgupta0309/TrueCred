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
import { api, notificationService } from '../services/api';
import StudentSearch from '../components/organization/StudentSearch';

// Mock Data - will be replaced with API calls
const mockCredentials = [
  { id: 1, title: 'B.Sc. Computer Science Degree', date: 'Oct 15, 2023', status: 'Verified' },
  { id: 2, title: 'Web Development Bootcamp Certificate', date: 'Nov 01, 2023', status: 'Pending' },
  { id: 3, title: 'High School Diploma', date: 'Sep 20, 2023', status: 'Verified' },
  { id: 4, title: 'First Aid Certification', date: 'Nov 10, 2023', status: 'Rejected' },
];

const mockExperiences = [
  { id: 1, title: 'Software Engineer Intern', company: 'Tech Corp', duration: 'Jun 2023 - Aug 2023' },
  { id: 2, title: 'Freelance Web Developer', company: 'Self-Employed', duration: 'Jan 2023 - Present' },
  { id: 3, title: 'Hackathon Project Lead', company: 'University CodeFest', duration: 'Mar 2023' },
];

const mockNotifications = [
  { id: 1, type: 'alert', message: 'Your "First Aid Certification" was rejected. Please review.', time: '2 hours ago' },
  { id: 2, type: 'info', message: 'Verification for "Web Development Bootcamp" is in progress.', time: '1 day ago' },
  { id: 3, type: 'info', message: 'Welcome to your new dashboard!', time: '3 days ago' },
];

function StudentDashboard({ onAuthError }) {
  const { user } = useAuth();
  const [credentials, setCredentials] = useState(mockCredentials);
  const [experiences, setExperiences] = useState(mockExperiences);
  const [notifications, setNotifications] = useState(mockNotifications);
  const [loading, setLoading] = useState(true);
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [needsProfileCompletion, setNeedsProfileCompletion] = useState(false);
  const [viewMode, setViewMode] = useState('list'); // 'list' or 'blockchain'
  const [selectedStudent, setSelectedStudent] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');
  
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
        // Check if profile needs completion
        if (user && (!user.first_name || !user.last_name)) {
          setNeedsProfileCompletion(true);
        }
        
        // Fetch credentials
        try {
          const credResponse = await api.get('/api/credentials');
          if (credResponse.data.success) {
            setCredentials(credResponse.data.credentials || []);
          }
        } catch (credError) {
          console.error('Error fetching credentials:', credError);
          // Keep mock data for development
        }
        
        // Fetch experiences
        try {
          const expResponse = await api.get('/api/experiences');
          if (expResponse.data.success) {
            setExperiences(expResponse.data.experiences || []);
          }
        } catch (expError) {
          console.error('Error fetching experiences:', expError);
          // Keep mock data for development
        }
        
        // Fetch notifications
        try {
          const notifResponse = await notificationService.getNotifications();
          if (notifResponse.data.success) {
            setNotifications(notifResponse.data.data.notifications || []);
          }
        } catch (notifError) {
          console.error('Error fetching notifications:', notifError);
          // Keep mock data for development
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
                      <CredentialsList credentials={credentials} />
                      <ExperienceList experiences={experiences} />
                    </>
                  ) : (
                    <div className="bg-white rounded-xl shadow-md p-6">
                      <h2 className="text-xl font-bold text-gray-800 mb-4">Blockchain Credentials</h2>
                      <div className="space-y-4">
                        {credentials.length > 0 ? (
                          credentials.map(credential => (
                            <BlockchainTokenDisplay key={credential.id} credential={credential} />
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
                    <ProfileCompletion onComplete={() => setNeedsProfileCompletion(false)} />
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
                <ActionButtons onAuthError={handleActionError} />
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