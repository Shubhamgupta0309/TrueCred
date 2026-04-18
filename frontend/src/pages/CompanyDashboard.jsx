import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { useAuth } from '../context/AuthContext.jsx';
import { useNavigate } from 'react-router-dom';
import CompanyDashboardHeader from '../components/company/CompanyDashboardHeader';
import PendingExperienceRequests from '../components/company/PendingExperienceRequests';
import ExperienceHistory from '../components/company/ExperienceHistory';
import CompanyProfileForm from '../components/company/CompanyProfileForm';
import CredentialIssuanceContainer from '../components/CredentialIssuanceContainer';
import NotificationPanel from '../components/dashboard/NotificationPanel';
import TemplateManager from '../components/TemplateManager';
import { companyService, notificationService } from '../services/api';

const initialPendingRequests = [];
const initialHistory = [];

export default function CompanyDashboard() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('intro');
  const [pendingRequests, setPendingRequests] = useState(initialPendingRequests);
  const [history, setHistory] = useState(initialHistory);
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const userForHeader = {
    name: user?.first_name && user?.last_name
      ? `${user.first_name} ${user.last_name}`
      : user?.organization || user?.username || 'Company Admin',
    email: user?.email || '',
    role: 'Company'
  };

  // Fetch company/experience data on mount
  React.useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError(null);

      try {
        const [pendingResp, historyResp, notifResp] = await Promise.all([
          companyService.getPendingExperienceRequests(),
          companyService.getExperienceHistory(),
          notificationService.getNotifications()
        ]);

        if (pendingResp.data && pendingResp.data.success) {
          const rawPending = pendingResp.data.data || pendingResp.data.requests || [];
          const mappedPending = rawPending.map((req) => ({
            ...req,
            studentTruecredId:
              req.studentTruecredId ||
              req.student_truecred_id ||
              req.student?.truecred_id ||
              req.student?.truecredId ||
              '',
          }));
          setPendingRequests(mappedPending);
        }

        if (historyResp.data && historyResp.data.success) {
          setHistory(historyResp.data.data || historyResp.data.history || []);
        }

        if (notifResp.data && notifResp.data.success) {
          setNotifications(notifResp.data.data.notifications || notifResp.data.notifications || []);
        }
      } catch (e) {
        console.error('Error fetching company dashboard data', e);
        setError('Failed to load company dashboard data. Please refresh and try again.');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  // Auto-refresh data every 5 seconds to keep notifications and stats updated
  React.useEffect(() => {
    const interval = setInterval(async () => {
      console.log('Auto-refreshing company dashboard data...');
      try {
        const [pendingResp, historyResp, notifResp] = await Promise.all([
          companyService.getPendingExperienceRequests(),
          companyService.getExperienceHistory(),
          notificationService.getNotifications()
        ]);

        if (pendingResp.data && pendingResp.data.success) {
          const rawPending = pendingResp.data.data || pendingResp.data.requests || [];
          const mappedPending = rawPending.map((req) => ({
            ...req,
            studentTruecredId:
              req.studentTruecredId ||
              req.student_truecred_id ||
              req.student?.truecred_id ||
              req.student?.truecredId ||
              '',
          }));
          setPendingRequests(mappedPending);
        }

        if (historyResp.data && historyResp.data.success) {
          setHistory(historyResp.data.data || historyResp.data.history || []);
        }

        if (notifResp.data && notifResp.data.success) {
          setNotifications(notifResp.data.data.notifications || notifResp.data.notifications || []);
        }
      } catch (e) {
        console.error('Error during company dashboard auto-refresh', e);
      }
    }, 5000); // Refresh every 5 seconds

    return () => clearInterval(interval);
  }, []);

  const handleAction = async (requestId, newStatus) => {
    try {
      let response;
      if (newStatus === 'approved' || newStatus === 'Approved') {
        response = await companyService.approveExperienceRequest(requestId);
      } else if (newStatus === 'rejected' || newStatus === 'Rejected') {
        response = await companyService.rejectExperienceRequest(requestId);
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

  const stats = [
    { label: 'Pending Verifications', value: pendingRequests.length, tone: 'text-cyan-100 bg-cyan-900/30 border-cyan-500/30' },
    { label: 'Completed Reviews', value: history.length, tone: 'text-cyan-100 bg-cyan-900/30 border-cyan-500/30' },
    { label: 'Notifications', value: notifications.length, tone: 'text-cyan-100 bg-cyan-900/30 border-cyan-500/30' }
  ];

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: { opacity: 1, transition: { staggerChildren: 0.1 } },
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 },
  };

  const handleLogout = async () => {
    await logout();
    navigate('/auth');
  };

  const handleDeleteHistoryItem = async (historyId) => {
    try {
      const response = await companyService.deleteExperienceHistoryItem(historyId);
      if (response?.data?.success) {
        setHistory((prev) => prev.filter((item) => item.id !== historyId));
      }
    } catch (error) {
      console.error('Failed to delete experience history item:', error);
    }
  };

  const handleFocusProfileForm = () => {
    const profileForm = document.querySelector('[data-profile-form]');
    if (profileForm instanceof HTMLElement) {
      profileForm.scrollIntoView({ behavior: 'smooth', block: 'start' });
      const editButton = profileForm.querySelector('[data-profile-edit]');
      if (editButton instanceof HTMLElement) {
        editButton.click();
        return;
      }
      const firstField = profileForm.querySelector('input, textarea, select');
      if (firstField instanceof HTMLElement) {
        firstField.focus();
      }
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 p-4 md:p-8 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-cyan-600 mx-auto"></div>
          <p className="mt-4 text-cyan-200">Loading company dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 p-4 md:p-8 flex items-center justify-center">
        <div className="bg-cyan-950/30 border border-cyan-500/30 shadow-md rounded-lg p-8 max-w-md w-full text-center backdrop-blur-md">
          <h2 className="text-xl font-bold text-cyan-100">Error Loading Dashboard</h2>
          <p className="mt-2 text-cyan-200">{error}</p>
          <button
            onClick={() => window.location.reload()}
            className="mt-6 px-4 py-2 bg-cyan-600 text-slate-950 rounded hover:bg-cyan-500 transition-colors"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 p-4 md:p-8">
      <div className="max-w-7xl mx-auto">
        <CompanyDashboardHeader user={userForHeader} />

        <motion.div
          variants={containerVariants}
          initial="hidden"
          animate="visible"
          className="grid grid-cols-1 lg:grid-cols-3 gap-8"
        >
          <div className="bg-cyan-950/30 border border-cyan-500/30 shadow-sm rounded-lg mb-8 lg:col-span-3 backdrop-blur-md">
            <div className="flex border-b border-cyan-500/20">
              <button className={`py-3 px-6 focus:outline-none ${activeTab === 'intro' ? 'border-b-2 border-cyan-400 text-cyan-300' : 'text-cyan-200/70 hover:text-cyan-300'}`} onClick={() => setActiveTab('intro')}>Intro</button>
              <button className={`py-3 px-6 focus:outline-none ${activeTab === 'requests' ? 'border-b-2 border-cyan-400 text-cyan-300' : 'text-cyan-200/70 hover:text-cyan-300'}`} onClick={() => setActiveTab('requests')}>Pending Requests</button>
              <button className={`py-3 px-6 focus:outline-none ${activeTab === 'issue' ? 'border-b-2 border-cyan-400 text-cyan-300' : 'text-cyan-200/70 hover:text-cyan-300'}`} onClick={() => setActiveTab('issue')}>Issue Credentials</button>
              <button className={`py-3 px-6 focus:outline-none ${activeTab === 'history' ? 'border-b-2 border-cyan-400 text-cyan-300' : 'text-cyan-200/70 hover:text-cyan-300'}`} onClick={() => setActiveTab('history')}>History</button>
              <button className={`py-3 px-6 focus:outline-none ${activeTab === 'templates' ? 'border-b-2 border-cyan-400 text-cyan-300' : 'text-cyan-200/70 hover:text-cyan-300'}`} onClick={() => setActiveTab('templates')}>Certificate Templates</button>
              <button className={`py-3 px-6 focus:outline-none ${activeTab === 'profile' ? 'border-b-2 border-cyan-400 text-cyan-300' : 'text-cyan-200/70 hover:text-cyan-300'}`} onClick={() => setActiveTab('profile')}>Profile</button>
            </div>
          </div>

          {activeTab === 'intro' ? (
            <>
              <div className="lg:col-span-2 space-y-6">
                <motion.div variants={itemVariants} className="bg-cyan-950/30 rounded-2xl shadow-sm border border-cyan-500/30 p-6">
                  <p className="text-xs uppercase tracking-[0.18em] text-cyan-300 font-semibold">TrueCred Startup Workspace</p>
                  <h2 className="mt-2 text-2xl md:text-3xl font-bold text-cyan-100">Institution Verification Command Center</h2>
                  <p className="mt-3 text-cyan-200 leading-relaxed">
                    Manage credential approvals, keep audit-ready verification history, and publish trusted templates so
                    student submissions can be evaluated with confidence and speed.
                  </p>
                </motion.div>
                <motion.div variants={itemVariants} className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {stats.map((item) => (
                    <div key={item.label} className={`rounded-xl border p-4 ${item.tone}`}>
                      <p className="text-xs uppercase tracking-wide font-semibold">{item.label}</p>
                      <p className="text-3xl font-bold mt-2">{item.value}</p>
                    </div>
                  ))}
                </motion.div>
              </div>
              <div className="space-y-8">
                <motion.div variants={itemVariants}>
                  <NotificationPanel notifications={notifications} />
                </motion.div>
              </div>
            </>
          ) : activeTab === 'requests' ? (
            <>
              {/* Main Column */}
              <div className="lg:col-span-2 space-y-8">
                <motion.div variants={itemVariants}>
                  <PendingExperienceRequests requests={pendingRequests} onAction={handleAction} />
                </motion.div>
              </div>

              {/* Right Column */}
              <div className="space-y-8">
                <motion.div variants={itemVariants}>
                  <NotificationPanel notifications={notifications} />
                </motion.div>
              </div>
            </>
          ) : activeTab === 'issue' ? (
            <>
              <div className="lg:col-span-2">
                <CredentialIssuanceContainer />
              </div>
              <div className="space-y-8">
                <motion.div variants={itemVariants}>
                  <NotificationPanel notifications={notifications} />
                </motion.div>
              </div>
            </>
          ) : activeTab === 'history' ? (
            <>
              <div className="lg:col-span-2 space-y-8">
                <motion.div variants={itemVariants}>
                  <ExperienceHistory history={history} onDelete={handleDeleteHistoryItem} />
                </motion.div>
              </div>
              <div className="space-y-8">
                <motion.div variants={itemVariants}>
                  <NotificationPanel notifications={notifications} />
                </motion.div>
              </div>
            </>
          ) : activeTab === 'templates' ? (
            <div className="lg:col-span-3 space-y-8">
              <motion.div variants={itemVariants}>
                <TemplateManager
                  organizationId={user?.company_id || user?.organization_id || user?.id}
                  organizationName={user?.organization || user?.company_name || 'Company'}
                  organizationType="company"
                />
              </motion.div>
            </div>
          ) : (
            <div className="lg:col-span-3">
              <CompanyProfileForm user={userForHeader} onUpdate={() => {}} />
              <div className="mt-6 flex justify-end gap-3">
                <button
                  onClick={handleLogout}
                  className="px-4 py-2 rounded-lg bg-red-500 text-white hover:bg-red-600 transition-colors"
                >
                  Logout
                </button>
              </div>
            </div>
          )}
        </motion.div>
      </div>
    </div>
  );
}