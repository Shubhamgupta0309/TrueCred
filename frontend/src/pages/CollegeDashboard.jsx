import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from '../context/AuthContext.jsx';
import DashboardHeader from '../components/dashboard/DashboardHeader';
import SearchFilterPanel from '../components/college/SearchFilterPanel';
import PendingRequests from '../components/college/PendingRequests';
import VerificationHistory from '../components/college/VerificationHistory';
import NotificationPanel from '../components/dashboard/NotificationPanel';

// Mock Data - will be replaced with API calls later

const initialPendingRequests = [
  { id: 1, studentName: 'Alex Doe', credentialTitle: 'B.Sc. Computer Science Degree', submissionDate: 'Nov 20, 2023' },
  { id: 2, studentName: 'Jane Smith', credentialTitle: 'Data Science Certification', submissionDate: 'Nov 18, 2023' },
  { id: 3, studentName: 'Mike Johnson', credentialTitle: 'Mechanical Engineering Diploma', submissionDate: 'Nov 15, 2023' },
];

const initialHistory = [
    { id: 101, studentName: 'Emily White', credentialTitle: 'Graphic Design Certificate', status: 'Verified', actionDate: 'Nov 14, 2023'},
    { id: 102, studentName: 'David Green', credentialTitle: 'Business Administration Degree', status: 'Rejected', actionDate: 'Nov 12, 2023'},
];

const mockNotifications = [
    { id: 1, type: 'info', message: '3 new verification requests are pending.', time: 'Just now' },
    { id: 2, type: 'alert', message: 'System maintenance scheduled for this weekend.', time: '1 day ago' },
];

export default function CollegeDashboard() {
  const { user } = useAuth();
  const [pendingRequests, setPendingRequests] = useState(initialPendingRequests);
  const [history, setHistory] = useState(initialHistory);
  const [loading, setLoading] = useState(true);
  
  // Format the user data for the header
  const userForHeader = {
    name: user?.first_name && user?.last_name 
      ? `${user.first_name} ${user.last_name}` 
      : user?.username || 'College Admin',
    email: user?.email || '',
    role: 'College'
  };
  
  // Fetch user data from API
  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        // In a real app, you would fetch actual data here
        // For now, we're using the mock data
        // Example: const response = await api.get('/college/pending-requests');
        // setPendingRequests(response.data);
        
        setLoading(false);
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const handleAction = (requestId, newStatus) => {
    const requestToMove = pendingRequests.find(req => req.id === requestId);
    if (requestToMove) {
      // Add to history
      setHistory(prevHistory => [
        ...prevHistory,
        { ...requestToMove, status: newStatus, actionDate: new Date().toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }) }
      ]);
      // Remove from pending requests
      setPendingRequests(prevRequests => prevRequests.filter(req => req.id !== requestId));
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

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-indigo-100 p-4 md:p-8">
      <div className="max-w-7xl mx-auto">
        <DashboardHeader user={userForHeader} />

        <motion.div
          variants={containerVariants}
          initial="hidden"
          animate="visible"
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
              <NotificationPanel notifications={mockNotifications} />
            </motion.div>
          </div>
        </motion.div>
      </div>
    </div>
  );
}