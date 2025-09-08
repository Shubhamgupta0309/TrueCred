import React, { useState } from 'react';
import { motion } from 'framer-motion';
import CompanyDashboardHeader from '../components/company/CompanyDashboardHeader';
import SearchFilterPanel from '../components/college/SearchFilterPanel'; // Reusing for now
import PendingExperienceRequests from '../components/company/PendingExperienceRequests';
import ExperienceHistory from '../components/company/ExperienceHistory';
import NotificationPanel from '../components/dashboard/NotificationPanel';

// Mock Data
const mockCompanyUser = {
  name: 'Innovate Inc.',
  email: 'company@gmail.com',
  role: 'Company',
};

const initialPendingRequests = [
  { id: 1, studentName: 'Alex Doe', experienceTitle: 'Software Engineer Intern', collegeName: 'Prestige College', submissionDate: 'Nov 22, 2023' },
  { id: 2, studentName: 'Jane Smith', experienceTitle: 'Marketing Intern', collegeName: 'City University', submissionDate: 'Nov 21, 2023' },
];

const initialHistory = [
    { id: 101, studentName: 'Emily White', experienceTitle: 'Data Analyst Coop', status: 'Verified', actionDate: 'Nov 18, 2023'},
    { id: 102, studentName: 'David Green', experienceTitle: 'UX/UI Design Intern', status: 'Rejected', actionDate: 'Nov 15, 2023'},
];

const mockNotifications = [
    { id: 1, type: 'info', message: 'You have 2 new experience verification requests.', time: '1 hour ago' },
    { id: 2, type: 'alert', message: 'Please update your company profile information.', time: '2 days ago' },
];

export default function CompanyDashboard() {
  const [pendingRequests, setPendingRequests] = useState(initialPendingRequests);
  const [history, setHistory] = useState(initialHistory);

  const handleAction = (requestId, newStatus) => {
    const requestToMove = pendingRequests.find(req => req.id === requestId);
    if (requestToMove) {
      setHistory(prevHistory => [
        ...prevHistory,
        { ...requestToMove, status: newStatus, actionDate: new Date().toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }) }
      ]);
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

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-teal-50 p-4 md:p-8">
      <div className="max-w-7xl mx-auto">
        <CompanyDashboardHeader user={mockCompanyUser} />

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
                <PendingExperienceRequests requests={pendingRequests} onAction={handleAction} />
            </motion.div>
          </div>

          {/* Right Column */}
          <div className="space-y-8">
            <motion.div variants={itemVariants}>
              <ExperienceHistory history={history} />
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