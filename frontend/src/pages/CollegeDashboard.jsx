import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useAuth } from '../context/AuthContext.jsx';
import { useNavigate } from 'react-router-dom';
import { useToast } from '../context/ToastContext.jsx';
import DashboardHeader from '../components/dashboard/DashboardHeader';
import PendingRequests from '../components/college/PendingRequests';
import VerificationHistory from '../components/college/VerificationHistory';
import NotificationPanel from '../components/dashboard/NotificationPanel';
import CredentialIssuanceContainer from '../components/CredentialIssuanceContainer';
import CollegeProfileForm from '../components/college/CollegeProfileForm';
import TemplateManager from '../components/TemplateManager';
import { collegeService, notificationService } from '../services/api';

export default function CollegeDashboard() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const { success, error: toastError } = useToast();
  const [pendingRequests, setPendingRequests] = useState([]);
  const [history, setHistory] = useState([]);
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('intro');
  const [error, setError] = useState(null);
  const [collegeProfile, setCollegeProfile] = useState(null);
  
  // Format the user data for the header
  const userForHeader = {
    name: user?.first_name && user?.last_name 
      ? `${user.first_name} ${user.last_name}` 
      : user?.username || 'College Admin',
    email: user?.email || '',
    role: 'College'
  };

  // Fetch dashboard data on mount
  useEffect(() => {
    const fetchDashboardData = async () => {
      setLoading(true);
      setError(null);

      try {
        const [pendingResult, historyResult, notifResult] = await Promise.allSettled([
          collegeService.getPendingRequests(),
          collegeService.getVerificationHistory(),
          notificationService.getNotifications()
        ]);

        if (pendingResult.status === 'fulfilled') {
          const pendingResp = pendingResult.value;
          if (pendingResp.data && pendingResp.data.success) {
            const rawPending = pendingResp.data.data || pendingResp.data.requests || [];
            const mappedPending = rawPending.map(req => ({
              id: req.id,
              user_id: req.user_id,
              title: req.title,
              studentName: req.student_name || req.userName || 'Unknown Student',
              studentEmail: req.student_email || req.userEmail || '',
              institutionName: req.institution_name || req.issuer || 'Not specified',
              credentialTitle: req.title || 'Untitled Credential',
              submissionDate: req.created_at ? new Date(req.created_at).toLocaleDateString() : 'Unknown',
              status: req.status,
              verification_status: req.verification_status,
              ocr_verified: req.ocr_verified,
              confidence_score: req.confidence_score,
              matched_template_name: req.matched_template_name,
              ocr_decision_details: req.ocr_decision_details || {},
              manual_review_required: req.manual_review_required,
              type: req.type,
              issuer: req.issuer,
              attachments: req.attachments || [],
              education_info: req.education_info || []
            }));
            setPendingRequests(mappedPending);
          }
        } else {
          console.error('Pending requests fetch failed:', pendingResult.reason);
        }

        if (historyResult.status === 'fulfilled') {
          const historyResp = historyResult.value;
          if (historyResp.data && historyResp.data.success) {
            setHistory(historyResp.data.data || historyResp.data.history || []);
          }
        } else {
          console.error('History fetch failed:', historyResult.reason);
        }

        if (notifResult.status === 'fulfilled') {
          const notifResp = notifResult.value;
          if (notifResp.data && notifResp.data.success) {
            setNotifications(notifResp.data.data?.notifications || notifResp.data.notifications || notifResp.data.data || []);
          }
        } else {
          console.error('Notifications fetch failed:', notifResult.reason);
        }

        if (
          pendingResult.status === 'rejected' &&
          historyResult.status === 'rejected' &&
          notifResult.status === 'rejected'
        ) {
          setError('Failed to load dashboard data. Please refresh to try again.');
        }
      } catch (err) {
        console.error('Error fetching dashboard data:', err);
        setError('Failed to load dashboard data. Please refresh to try again.');
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  // Auto-refresh data every 5 seconds to keep notifications and stats updated
  useEffect(() => {
    const interval = setInterval(async () => {
      console.log('Auto-refreshing dashboard data...');
      try {
        const [pendingResp, historyResp, notifResp] = await Promise.all([
          collegeService.getPendingRequests(),
          collegeService.getVerificationHistory(),
          notificationService.getNotifications()
        ]);

        if (pendingResp.data && pendingResp.data.success) {
          const rawPending = pendingResp.data.data || pendingResp.data.requests || [];
          const mappedPending = rawPending.map(req => ({
            id: req.id,
            user_id: req.user_id,
            title: req.title,
            studentName: req.student_name || req.userName || 'Unknown Student',
            studentEmail: req.student_email || req.userEmail || '',
            institutionName: req.institution_name || req.issuer || 'Not specified',
            credentialTitle: req.title || 'Untitled Credential',
            submissionDate: req.created_at ? new Date(req.created_at).toLocaleDateString() : 'Unknown',
            status: req.status,
            verification_status: req.verification_status,
            ocr_verified: req.ocr_verified,
            confidence_score: req.confidence_score,
            matched_template_name: req.matched_template_name,
            ocr_decision_details: req.ocr_decision_details || {},
            manual_review_required: req.manual_review_required,
            type: req.type,
            issuer: req.issuer,
            attachments: req.attachments || [],
            education_info: req.education_info || []
          }));
          setPendingRequests(mappedPending);
        }

        if (historyResp.data && historyResp.data.success) {
          setHistory(historyResp.data.data || historyResp.data.history || []);
        }

        if (notifResp.data && notifResp.data.success) {
          setNotifications(notifResp.data.data?.notifications || notifResp.data.notifications || notifResp.data.data || []);
        }
      } catch (err) {
        console.error('Error during auto-refresh:', err);
      }
    }, 5000); // Refresh every 5 seconds

    return () => clearInterval(interval);
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

    // Refresh data from server to ensure consistency
    try {
      const [pendingResp, historyResp] = await Promise.all([
        collegeService.getPendingRequests(),
        collegeService.getVerificationHistory()
      ]);

      if (pendingResp.data && pendingResp.data.success) {
        const rawPending = pendingResp.data.data || pendingResp.data.requests || [];
        const mappedPending = rawPending.map(req => ({
          id: req.id,
          user_id: req.user_id,
          title: req.title,
          studentName: req.student_name || req.userName || 'Unknown Student',
          studentEmail: req.student_email || req.userEmail || '',
          institutionName: req.institution_name || req.issuer || 'Not specified',
          credentialTitle: req.title || 'Untitled Credential',
          submissionDate: req.created_at ? new Date(req.created_at).toLocaleDateString() : 'Unknown',
          status: req.status,
          verification_status: req.verification_status,
          ocr_verified: req.ocr_verified,
          confidence_score: req.confidence_score,
          matched_template_name: req.matched_template_name,
          ocr_decision_details: req.ocr_decision_details || {},
          manual_review_required: req.manual_review_required,
          type: req.type,
          issuer: req.issuer,
          attachments: req.attachments || [],
          education_info: req.education_info || []
        }));
        setPendingRequests(mappedPending);
      }

      if (historyResp.data && historyResp.data.success) {
        setHistory(historyResp.data.data || historyResp.data.history || []);
      }
    } catch (err) {
      console.error('Failed to refresh data after action:', err);
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
    console.log('Credential issued, refreshing dashboard...');
    
    // Fallback: Add to history manually
    setHistory(prevHistory => [
      {
        id: credential.id || Math.random().toString(36).substr(2, 9),
        studentName: credential.recipientEmail ? credential.recipientEmail.split('@')[0] : 'Unknown Student',
        credentialTitle: credential.title || credential.credentialTitle || 'Issued Credential',
        status: 'Issued',
        actionDate: new Date().toLocaleDateString('en-US', { 
          month: 'short', 
          day: 'numeric', 
          year: 'numeric' 
        }),
        institutionName: credential.institutionName || credential.issuer || 'Your Institution'
      },
      ...prevHistory
    ]);

    // Immediately refresh all data from API
    Promise.all([
      collegeService.getPendingRequests(),
      collegeService.getVerificationHistory(),
      notificationService.getNotifications()
    ]).then(([pendingResp, historyResp, notifResp]) => {
      if (pendingResp.data && pendingResp.data.success) {
        const rawPending = pendingResp.data.data || pendingResp.data.requests || [];
        const mappedPending = rawPending.map(req => ({
          id: req.id,
          user_id: req.user_id,
          title: req.title,
          studentName: req.student_name || req.userName || 'Unknown Student',
          studentEmail: req.student_email || req.userEmail || '',
          institutionName: req.institution_name || req.issuer || 'Not specified',
          credentialTitle: req.title || 'Untitled Credential',
          submissionDate: req.created_at ? new Date(req.created_at).toLocaleDateString() : 'Unknown',
          status: req.status,
          verification_status: req.verification_status,
          ocr_verified: req.ocr_verified,
          confidence_score: req.confidence_score,
          matched_template_name: req.matched_template_name,
          ocr_decision_details: req.ocr_decision_details || {},
          manual_review_required: req.manual_review_required,
          type: req.type,
          issuer: req.issuer,
          attachments: req.attachments || [],
          education_info: req.education_info || []
        }));
        setPendingRequests(mappedPending);
      }

      if (historyResp.data && historyResp.data.success) {
        setHistory(historyResp.data.data || historyResp.data.history || []);
      }

      if (notifResp.data && notifResp.data.success) {
        setNotifications(notifResp.data.data?.notifications || notifResp.data.notifications || notifResp.data.data || []);
      }
    }).catch(err => {
      console.error('Failed to refresh after credential issuance:', err);
    });
  };

  const handleProfileUpdate = (profile) => {
    setCollegeProfile(profile);
    // Update user for header if needed
    if (profile.name) {
      userForHeader.organization = profile.name;
    }
  };

  const handleLogout = async () => {
    await logout();
    navigate('/auth');
  };

  const handleDeleteHistoryItem = async (historyId) => {
    try {
      const response = await collegeService.deleteVerificationHistoryItem(historyId);
      if (response?.data?.success) {
        setHistory((prev) => prev.filter((item) => item.id !== historyId));
        success('History item deleted successfully.');
      } else {
        toastError(response?.data?.message || 'Failed to delete history item.');
      }
    } catch (err) {
      console.error('Failed to delete history item:', err);
      toastError('Failed to delete history item.');
    }
  };

  const summaryStats = [
    {
      label: 'Pending Verifications',
      value: pendingRequests.length,
      tone: 'text-cyan-100 bg-cyan-900/30 border-cyan-500/30'
    },
    {
      label: 'Completed Reviews',
      value: history.length,
      tone: 'text-cyan-100 bg-cyan-900/30 border-cyan-500/30'
    },
    {
      label: 'Notifications',
      value: notifications.length,
      tone: 'text-cyan-100 bg-cyan-900/30 border-cyan-500/30'
    }
  ];

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 p-4 md:p-8 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-cyan-500 mx-auto"></div>
          <p className="mt-4 text-cyan-200">Loading your dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 p-4 md:p-8 flex items-center justify-center">
        <div className="bg-cyan-950/30 border border-cyan-500/30 backdrop-blur-md shadow-md rounded-lg p-8 max-w-md w-full">
          <div className="text-center">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-12 w-12 mx-auto text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <h2 className="mt-4 text-xl font-bold text-cyan-100">Error Loading Dashboard</h2>
            <p className="mt-2 text-cyan-200">{error}</p>
            <button 
              onClick={() => window.location.reload()}
              className="mt-6 px-4 py-2 bg-cyan-600 text-slate-950 rounded hover:bg-cyan-500 transition-colors"
            >
              Retry
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 p-4 md:p-8">
      <div className="max-w-7xl mx-auto">
        <DashboardHeader user={userForHeader} />

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
                  {summaryStats.map((item) => (
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
              <div className="lg:col-span-2 space-y-8">
                <motion.div variants={itemVariants}>
                  <PendingRequests requests={pendingRequests} onAction={handleAction} />
                </motion.div>
              </div>

              <div className="space-y-8">
                <motion.div variants={itemVariants}>
                  <NotificationPanel notifications={notifications} />
                </motion.div>
              </div>
            </>
          ) : activeTab === 'issue' ? (
            <>
              <div className="lg:col-span-2">
                <CredentialIssuanceContainer onCredentialIssued={handleCredentialIssued} />
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
                  <VerificationHistory history={history} onDelete={handleDeleteHistoryItem} />
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
                  organizationId={user?.college_id || user?.id}
                  organizationName={collegeProfile?.name || user?.username}
                  organizationType="college"
                />
              </motion.div>
            </div>
          ) : (
            <div className="lg:col-span-3">
              <CollegeProfileForm user={user} onUpdate={handleProfileUpdate} />
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