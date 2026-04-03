import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
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
import { Upload, PlusCircle, Star, TrendingUp, Lock, Users } from 'lucide-react';

// Mock Data - will be replaced with API calls
// start with empty data; will fetch from API
const mockCredentials = [];
const mockExperiences = [];
const mockNotifications = [];

// Normalize credential array into UI-friendly shape and deduplicate by a stable id.
// If backend doesn't provide an id, fall back to base64 of title|date so repeated fetches produce same id.
const normalizeCredentials = (arr) => {
  // Ensure arr is an array
  if (!Array.isArray(arr)) {
    console.warn('normalizeCredentials received non-array input:', arr);
    return [];
  }
  
  const map = new Map();
  arr.forEach((c) => {
    let id = c.id || c._id || c.id_str || c._id_str || (c._id && String(c._id)) || null;
    const title = c.title || c.name || 'Untitled Credential';
    const date = c.issue_date || c.created_at || c.updated_at || c.timestamp || null;
    const status = c.verification_status || c.status || (c.verified ? 'verified' : (c.pending_verification ? 'pending' : 'unverified')) || 'unknown';

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

const getEffectiveRequestStatus = (req) => {
  const verificationStatus = (req?.verification_status || '').toLowerCase();
  if (verificationStatus) {
    if (verificationStatus === 'verified') return 'approved';
    if (verificationStatus === 'pending_review') return 'review';
    if (verificationStatus === 'rejected') return 'rejected';
    if (verificationStatus === 'no_template' || verificationStatus === 'failed' || verificationStatus === 'error') {
      return 'pending';
    }
    return verificationStatus;
  }
  const requestStatus = (req?.status || 'pending').toLowerCase();
  if (requestStatus === 'verified' || requestStatus === 'issued') return 'approved';
  return requestStatus;
};

const getStatusBadgeClass = (statusKey) => {
  const statusMap = {
    'approved': 'bg-emerald-100 text-emerald-700 border-emerald-300',
    'review': 'bg-amber-100 text-amber-700 border-amber-300',
    'pending': 'bg-cyan-900/40 text-cyan-100 border-cyan-500/40',
    'rejected': 'bg-red-100 text-red-700 border-red-300',
    'issued': 'bg-emerald-100 text-emerald-700 border-emerald-300'
  };
  return statusMap[statusKey] || 'bg-gray-100 text-gray-700 border-gray-300';
};

const getStatusLabel = (statusKey) => {
  const labelMap = {
    'approved': '✓ Approved',
    'review': '⊙ Under Review',
    'pending': '◐ Pending',
    'rejected': '✕ Rejected',
    'issued': '✓ Issued'
  };
  return labelMap[statusKey] || statusKey;
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
  const [activeTab, setActiveTab] = useState('intro');
  const [pendingRequests, setPendingRequests] = useState([]);

  const summaryStats = [
    {
      label: 'Issued Credentials',
      value: credentials.length,
      tone: 'text-emerald-700 bg-emerald-50 border-emerald-100'
    },
    {
      label: 'Pending Requests',
      value: pendingRequests.filter((r) => ['pending', 'pending_review'].includes(getEffectiveRequestStatus(r))).length,
      tone: 'text-amber-700 bg-amber-50 border-amber-100'
    },
    {
      label: 'Notifications',
      value: notifications.length,
      tone: 'text-sky-700 bg-sky-50 border-sky-100'
    }
  ];
  
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
            // Extract credentials array from various possible response structures
            let creds = [];
            if (Array.isArray(credResponse.data.data)) {
              creds = credResponse.data.data;
            } else if (credResponse.data.data && Array.isArray(credResponse.data.data.credentials)) {
              creds = credResponse.data.data.credentials;
            } else if (Array.isArray(credResponse.data.credentials)) {
              creds = credResponse.data.credentials;
            } else if (Array.isArray(credResponse.data)) {
              creds = credResponse.data;
            }
            
            console.debug('Extracted credentials array:', creds);
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
      <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 p-4 md:p-8 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-cyan-400 mx-auto"></div>
          <p className="mt-4 text-cyan-300/70">Loading your dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950">
      {/* Animated background blobs */}
      <div className="fixed inset-0 overflow-hidden -z-10">
        <motion.div 
          className="absolute -top-40 -right-40 w-80 h-80 bg-cyan-500 rounded-full opacity-15 blur-3xl"
          animate={{ x: [0, 30, 0], y: [0, 40, 0] }}
          transition={{ duration: 8, repeat: Infinity }}
        />
        <motion.div 
          className="absolute -bottom-40 -left-40 w-80 h-80 bg-cyan-400 rounded-full opacity-15 blur-3xl"
          animate={{ x: [0, -30, 0], y: [0, -40, 0] }}
          transition={{ duration: 10, repeat: Infinity }}
        />
      </div>

      <div className="relative">
        {/* Header - Full width */}
        <div className="w-full px-6 py-8 border-b border-cyan-500/20">
          <div className="max-w-full">
            <motion.div
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex justify-between items-center"
            >
              <div>
                <h1 className="text-4xl font-bold text-white">
                  Welcome back, <span className="bg-gradient-to-r from-cyan-400 to-cyan-300 bg-clip-text text-transparent">{userForHeader.name.split(' ')[0]}</span>
                </h1>
                <p className="text-cyan-300/70 mt-2">TrueCred ID: <code className="bg-cyan-900/40 px-3 py-1 rounded text-cyan-100">{userForHeader.truecred_id}</code></p>
              </div>
            </motion.div>
          </div>
        </div>

        {needsProfileCompletion ? (
          <ProfileCompletion onComplete={() => setNeedsProfileCompletion(false)} />
        ) : (
          <>
            {/* 3-Column Layout */}
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 p-6">
              {/* LEFT SIDEBAR - 2 columns */}
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.1 }}
                className="lg:col-span-2 space-y-6"
              >
                {/* TrueCred ID Card */}
                <div className="bg-cyan-950/30 backdrop-blur-md border border-cyan-500/30 rounded-xl p-4">
                  <p className="text-xs text-cyan-300 uppercase tracking-wide font-semibold">Your ID</p>
                  <p className="text-xl font-mono text-cyan-100 mt-2">{userForHeader.truecred_id}</p>
                  <p className="text-xs text-cyan-300/70 mt-3">Share with institutions</p>
                </div>

                {/* Quick Stats */}
                <div className="space-y-3">
                  {[
                    { label: 'Credentials', value: credentials.length, color: 'from-cyan-600 to-cyan-700' },
                    { label: 'Experiences', value: experiences.length, color: 'from-cyan-500 to-cyan-600' },
                    { label: 'In Review', value: pendingRequests.filter(r => ['review', 'pending'].includes(getEffectiveRequestStatus(r))).length, color: 'from-cyan-600 to-cyan-700' }
                  ].map((stat, i) => (
                    <div key={i} className={`bg-gradient-to-br ${stat.color} rounded-lg p-4 text-white`}>
                      <p className="text-xs opacity-90">{stat.label}</p>
                      <p className="text-3xl font-bold mt-1">{stat.value}</p>
                    </div>
                  ))}
                </div>
              </motion.div>

              {/* CENTER CONTENT - 8 columns */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
                className="lg:col-span-8 space-y-6"
              >
                {/* Action Buttons - WIDE */}
                <div className="bg-cyan-950/30 backdrop-blur-md border border-cyan-500/30 rounded-2xl p-8 shadow-2xl">
                  <h2 className="text-2xl font-bold text-white mb-6">Quick Actions</h2>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <motion.button
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                      onClick={() => document.querySelector('[data-action="upload-credential"]')?.click?.()}
                      className="group flex items-center gap-4 p-6 bg-gradient-to-br from-cyan-500 to-cyan-600 rounded-xl text-white hover:shadow-lg transition-all duration-300 hover:from-cyan-600 hover:to-cyan-700 hover:shadow-cyan-500/30"
                    >
                      <div className="p-3 bg-cyan-400 bg-opacity-30 rounded-lg group-hover:bg-opacity-50 transition-all">
                        <Upload className="w-6 h-6" />
                      </div>
                      <div className="text-left flex-1">
                        <h3 className="font-semibold text-lg">Upload New Credential</h3>
                        <p className="text-sm text-cyan-100">Request from institution</p>
                      </div>
                    </motion.button>
                    
                    <motion.button
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                      onClick={() => document.querySelector('[data-action="add-experience"]')?.click?.()}
                      className="group flex items-center gap-4 p-6 bg-gradient-to-br from-cyan-500 to-cyan-600 rounded-xl text-white hover:shadow-lg transition-all duration-300 hover:from-cyan-600 hover:to-cyan-700 hover:shadow-cyan-500/30"
                    >
                      <div className="p-3 bg-cyan-400 bg-opacity-30 rounded-lg group-hover:bg-opacity-50 transition-all">
                        <PlusCircle className="w-6 h-6" />
                      </div>
                      <div className="text-left flex-1">
                        <h3 className="font-semibold text-lg">Add New Experience</h3>
                        <p className="text-sm text-cyan-100">Log work history</p>
                      </div>
                    </motion.button>
                  </div>
                </div>

                {/* Hidden ActionButtons */}
                <div className="hidden">
                  <ActionButtons 
                    onAuthError={handleActionError} 
                    onSuccess={() => {
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
                          console.error('Failed to refresh dashboard', e);
                        } finally {
                          setLoading(false);
                        }
                      })();
                    }}
                  />
                </div>

                {/* Tab Navigation */}
                <div className="flex gap-2 overflow-x-auto pb-4">
                  {[
                    { id: 'intro', label: '🏠 Home' },
                    { id: 'requests', label: '📋 Requests' },
                    { id: 'overview', label: '📚 Credentials' },
                    { id: 'profile', label: '👤 Profile' }
                  ].map(tab => (
                    <motion.button
                      key={tab.id}
                      onClick={() => setActiveTab(tab.id)}
                      whileHover={{ scale: 1.05 }}
                      className={`px-6 py-3 rounded-lg font-semibold transition-all duration-300 whitespace-nowrap ${
                        activeTab === tab.id
                          ? 'bg-white text-slate-900 shadow-lg'
                              : 'bg-cyan-950/10 text-white hover:bg-cyan-950/20'
                      }`}
                    >
                      {tab.label}
                    </motion.button>
                  ))}
                </div>

                {/* Main Content Area */}
                <AnimatePresence mode="wait">
                  {activeTab === 'intro' && (
                    <motion.div
                      key="intro"
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -20 }}
                      className="space-y-6"
                    >
                      <div className="bg-gradient-to-br from-white to-purple-50 rounded-2xl p-8 shadow-xl">
                        <p className="text-sm uppercase tracking-wider text-cyan-400 font-semibold">TrueCred Platform</p>
                        <h2 className="text-4xl font-bold text-slate-900 mt-4">Own Your Digital Trust</h2>
                        <p className="text-lg text-slate-600 mt-6">Request credentials from institutions, track OCR verification in real-time, and build your verifiable portfolio.</p>
                      </div>

                      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        {[
                          { icon: Lock, title: 'Verified Credentials', desc: 'OCR-powered with confidence scores' },
                          { icon: Users, title: 'Direct Issuance', desc: 'Institutions issue to you directly' },
                          { icon: TrendingUp, title: 'Track Progress', desc: 'Monitor requests in real-time' },
                          { icon: Star, title: 'Blockchain Ready', desc: 'Export for permanence' }
                        ].map((feature, i) => (
                          <motion.div
                            key={i}
                            whileHover={{ y: -5 }}
                            className="bg-cyan-950/30 backdrop-blur-md border border-cyan-500/30 rounded-xl p-6 text-white hover:bg-cyan-950/50 transition-all duration-300"
                          >
                            <feature.icon className="w-8 h-8 mb-3 text-cyan-300" />
                            <h3 className="font-bold text-lg mb-2">{feature.title}</h3>
                            <p className="text-sm text-cyan-100">{feature.desc}</p>
                          </motion.div>
                        ))}
                      </div>
                    </motion.div>
                  )}

                  {activeTab === 'requests' && (
                    <motion.div
                      key="requests"
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -20 }}
                      className="space-y-6"
                    >
                      {pendingRequests && pendingRequests.length > 0 ? (
                        <div className="space-y-4">
                          {['approved', 'review', 'pending', 'rejected'].map(status => {
                            const statusReqs = pendingRequests.filter(r => getEffectiveRequestStatus(r) === status);
                            return statusReqs.length > 0 ? (
                              <div key={status} className="bg-cyan-950/30 backdrop-blur-md border border-cyan-500/30 rounded-xl p-6">
                                <h3 className="text-lg font-bold text-white mb-4">{getStatusLabel(status)} ({statusReqs.length})</h3>
                                <div className="space-y-3">
                                  {statusReqs.map(req => (
                                    <motion.div
                                      key={req.id}
                                      className={`p-4 rounded-lg border ${getStatusBadgeClass(status)} bg-opacity-20`}
                                    >
                                      <div className="flex justify-between items-start">
                                        <div className="flex-1">
                                          <h4 className="font-semibold text-white">{req.title}</h4>
                                          <p className="text-sm text-cyan-100 mt-1">{req.issuer}</p>
                                          {req.confidence_score !== undefined && (
                                            <div className="mt-2 flex items-center gap-2">
                                              <div className="h-2 bg-opacity-30 bg-white rounded-full flex-1" style={{width: '120px'}}>
                                                <div 
                                                  className={`h-full rounded-full ${
                                                    req.confidence_score > 50 ? 'bg-emerald-400' :
                                                    req.confidence_score > 30 ? 'bg-amber-400' : 'bg-red-400'
                                                  }`}
                                                  style={{width: `${req.confidence_score}%`}}
                                                />
                                              </div>
                                              <span className="text-xs font-mono text-cyan-100">{req.confidence_score}%</span>
                                            </div>
                                          )}
                                        </div>
                                        <div className={`px-3 py-1 rounded-full text-xs font-bold ${getStatusBadgeClass(status)}`}>
                                          {getStatusLabel(status)}
                                        </div>
                                      </div>
                                    </motion.div>
                                  ))}
                                </div>
                              </div>
                            ) : null;
                          })}
                        </div>
                      ) : (
                        <div className="bg-white bg-opacity-10 backdrop-blur-md border border-white border-opacity-20 rounded-xl p-12 text-center">
                          <p className="text-white text-lg">No requests yet</p>
                        </div>
                      )}
                    </motion.div>
                  )}

                  {activeTab === 'overview' && (
                    <motion.div
                      key="overview"
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -20 }}
                      className="space-y-6"
                    >
                      {credentials.length > 0 ? (
                        <>
                          <CredentialsList credentials={credentials} onVerificationUpdate={handleVerificationUpdate} />
                          {experiences.length > 0 && <ExperienceList experiences={experiences} />}
                        </>
                      ) : (
                        <div className="bg-white bg-opacity-10 backdrop-blur-md border border-white border-opacity-20 rounded-xl p-12 text-center">
                          <p className="text-white text-lg">No credentials</p>
                        </div>
                      )}
                    </motion.div>
                  )}

                  {activeTab === 'profile' && (
                    <motion.div
                      key="profile"
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -20 }}
                    >
                      {user?.profile_completed ? (
                        <div className="bg-cyan-950/30 backdrop-blur-md border border-cyan-500/30 rounded-xl p-8 text-white">
                          <h3 className="text-2xl font-bold mb-6">Your Profile</h3>
                          <div className="space-y-4">
                            <div>
                              <p className="text-cyan-300 text-sm">Name</p>
                              <p className="text-white font-semibold">{user?.first_name} {user?.last_name}</p>
                            </div>
                            <div>
                              <p className="text-cyan-300 text-sm">Email</p>
                              <p className="text-white font-semibold">{user?.email}</p>
                            </div>
                          </div>
                        </div>
                      ) : (
                        <ProfileCompletion onComplete={() => setNeedsProfileCompletion(false)} />
                      )}
                    </motion.div>
                  )}
                </AnimatePresence>
              </motion.div>

              {/* RIGHT SIDEBAR - 2 columns */}
              <motion.div
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.3 }}
                className="lg:col-span-2 space-y-6"
              >
                {/* Student Search - Moved to Top */}
                <div className="hidden lg:block">
                  <div className="bg-cyan-950/30 backdrop-blur-md border border-cyan-500/30 rounded-xl p-4">
                    <p className="text-xs text-cyan-300 uppercase tracking-wide font-semibold mb-3">🔍 Search for Students</p>
                    <p className="text-xs text-cyan-300/70 mb-3">Search by name, email, or TrueCred ID (e.g., TC123456)</p>
                    <StudentSearch onStudentSelect={(s) => setSelectedStudent(s)} />
                    <p className="text-xs text-cyan-300/60 mt-3">Enter at least 3 characters to search, or enter a complete TrueCred ID (TC######) for exact match.</p>
                  </div>
                </div>

                {/* Quick Info / Tips */}
                <div className="bg-white bg-opacity-10 backdrop-blur-md border border-white border-opacity-20 rounded-xl p-4">
                  <p className="text-xs text-cyan-300 uppercase tracking-wide font-semibold mb-3">💡 Tips</p>
                  <div className="space-y-2 text-xs text-cyan-100/80">
                    <p>• Upload certificates to get started</p>
                    <p>• Track verification status in real-time</p>
                    <p>• Share your TrueCred ID with institutions</p>
                    <p>• Build your verifiable portfolio</p>
                  </div>
                </div>

                {/* Notifications */}
                <div>
                  <NotificationPanel notifications={notifications} />
                </div>
              </motion.div>
            </div>
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