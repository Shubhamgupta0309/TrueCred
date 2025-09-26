import React, { useState } from 'react';
import { motion } from 'framer-motion';
import CompanyDashboardHeader from '../components/company/CompanyDashboardHeader';
import SearchFilterPanel from '../components/college/SearchFilterPanel'; // Reusing for now
import PendingExperienceRequests from '../components/company/PendingExperienceRequests';
import ExperienceHistory from '../components/company/ExperienceHistory';
import CompanyProfileForm from '../components/company/CompanyProfileForm';
import NotificationPanel from '../components/dashboard/NotificationPanel';
import { companyService, notificationService } from '../services/api';

// start with empty state; will fetch from API
const mockCompanyUser = { name: '', email: '', role: 'Company' };
const initialPendingRequests = [];
const initialHistory = [];
const mockNotifications = [];

export default function CompanyDashboard() {
  const [activeTab, setActiveTab] = useState('requests');
  const [pendingRequests, setPendingRequests] = useState(initialPendingRequests);
  const [history, setHistory] = useState(initialHistory);
  const [notifications, setNotifications] = useState(mockNotifications);

  // Fetch company/experience data on mount
  React.useEffect(() => {
    const fetchData = async () => {
      try {
        const pendingResp = await companyService.getPendingExperienceRequests();
        if (pendingResp.data && pendingResp.data.success) {
          setPendingRequests(pendingResp.data.data || pendingResp.data.requests || []);
        }
      } catch (e) {
        console.error('Error fetching pending experience requests', e);
      }

      try {
        const historyResp = await companyService.getExperienceHistory();
        if (historyResp.data && historyResp.data.success) {
          setHistory(historyResp.data.data || historyResp.data.history || []);
        }
      } catch (e) {
        console.error('Error fetching experience history', e);
      }

      try {
        const notifResp = await notificationService.getNotifications();
        if (notifResp.data && notifResp.data.success) {
          setNotifications(notifResp.data.data.notifications || notifResp.data.notifications || []);
        }
      } catch (e) {
        console.error('Error fetching notifications', e);
      }
    };

    fetchData();
  }, []);

  const handleAction = async (requestId, newStatus, reason = null) => {
    try {
      let response;
      if (newStatus === 'approved' || newStatus === 'Approved') {
        response = await companyService.approveExperienceRequest(requestId);
      } else if (newStatus === 'rejected' || newStatus === 'Rejected') {
        response = await companyService.rejectExperienceRequest(requestId, reason || 'No reason provided');
      }
      
      if (response && response.data && response.data.success) {
        // Move to history on success
        const requestToMove = pendingRequests.find(req => req.id === requestId);
        if (requestToMove) {
          setHistory(prevHistory => [
            ...prevHistory,
            { ...requestToMove, status: newStatus, actionDate: new Date().toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }) }
          ]);
          setPendingRequests(prevRequests => prevRequests.filter(req => req.id !== requestId));
        }
      } else {
        console.error('Failed to process request:', response?.data?.message);
        // You might want to show an error toast here
      }
    } catch (error) {
      console.error('Error processing request:', error);
      // You might want to show an error toast here
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
          <div className="bg-white shadow-sm rounded-lg mb-8 lg:col-span-3">
            <div className="flex border-b">
              <button className={`py-3 px-6 focus:outline-none ${activeTab === 'requests' ? 'border-b-2 border-teal-600 text-teal-700' : 'text-gray-500 hover:text-teal-500'}`} onClick={() => setActiveTab('requests')}>Pending Requests</button>
              <button className={`py-3 px-6 focus:outline-none ${activeTab === 'history' ? 'border-b-2 border-teal-600 text-teal-700' : 'text-gray-500 hover:text-teal-500'}`} onClick={() => setActiveTab('history')}>History</button>
              <button className={`py-3 px-6 focus:outline-none ${activeTab === 'profile' ? 'border-b-2 border-teal-600 text-teal-700' : 'text-gray-500 hover:text-teal-500'}`} onClick={() => setActiveTab('profile')}>Company Profile</button>
            </div>
          </div>

          {activeTab === 'requests' ? (
            <>
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
                  <NotificationPanel notifications={notifications} />
                </motion.div>
              </div>
            </>
          ) : activeTab === 'history' ? (
            <>
              <div className="lg:col-span-2">
                <PendingExperienceRequests requests={[]} onAction={handleAction} />
              </div>
              <div className="space-y-8">
                <motion.div variants={itemVariants}>
                  <ExperienceHistory history={history} />
                </motion.div>
                <motion.div variants={itemVariants}>
                  <NotificationPanel notifications={notifications} />
                </motion.div>
              </div>
            </>
          ) : (
            <>
              <div className="lg:col-span-2">
                <CompanyProfileForm user={mockCompanyUser} onUpdate={() => {}} />
              </div>
              <div className="space-y-8">
                <motion.div variants={itemVariants}>
                  <NotificationPanel notifications={notifications} />
                </motion.div>
              </div>
            </>
          )}
        </motion.div>
      </div>
    </div>
  );
}