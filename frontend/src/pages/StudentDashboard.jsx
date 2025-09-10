import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useAuth } from '../context/AuthContext.jsx';
import DashboardHeader from '../components/dashboard/DashboardHeader';
import CredentialsList from '../components/dashboard/CredentialsList';
import ExperienceList from '../components/dashboard/ExperienceList';
import ActionButtons from '../components/dashboard/ActionButtons';
import NotificationPanel from '../components/dashboard/NotificationPanel';

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


export default function StudentDashboard() {
  const { user } = useAuth();
  const [credentials, setCredentials] = useState(mockCredentials);
  const [experiences, setExperiences] = useState(mockExperiences);
  const [notifications, setNotifications] = useState(mockNotifications);
  const [loading, setLoading] = useState(true);
  
  // Format the user data for the header
  const userForHeader = {
    name: user?.first_name && user?.last_name 
      ? `${user.first_name} ${user.last_name}` 
      : user?.username || 'Student',
    email: user?.email || '',
    role: 'Student'
  };

  // Fetch user data from API
  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        // In a real app, you would fetch actual data here
        // For now, we're using the mock data
        // Example: const response = await api.get('/student/credentials');
        // setCredentials(response.data);
        
        setLoading(false);
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
        setLoading(false);
      }
    };

    fetchData();
  }, []);

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
        <DashboardHeader user={userForHeader} />

        <motion.div
          variants={containerVariants}
          initial="hidden"
          animate="visible"
          className="grid grid-cols-1 lg:grid-cols-3 gap-8"
        >
          {/* Left Column */}
          <motion.div variants={itemVariants} className="lg:col-span-2 space-y-8">
            <CredentialsList credentials={mockCredentials} />
            <ExperienceList experiences={mockExperiences} />
          </motion.div>

          {/* Right Column */}
          <motion.div variants={itemVariants} className="space-y-8">
            <ActionButtons />
            <NotificationPanel notifications={mockNotifications} />
          </motion.div>
        </motion.div>
      </div>
    </div>
  );
}