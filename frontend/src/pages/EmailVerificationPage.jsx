import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import { CheckCircle, XCircle, Loader } from 'lucide-react';
import { useAuth } from '../context/AuthContext.jsx';

export default function EmailVerificationPage() {
  const [status, setStatus] = useState('verifying'); // 'verifying', 'success', 'error'
  const [message, setMessage] = useState('');
  const { verifyEmail } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    const verifyEmailToken = async () => {
      try {
        // Get token from URL query parameter
        const queryParams = new URLSearchParams(location.search);
        const token = queryParams.get('token');
        
        if (!token) {
          setStatus('error');
          setMessage('Verification token is missing.');
          return;
        }
        
        // Call the API to verify the email
        const result = await verifyEmail(token);
        
        if (result.success) {
          setStatus('success');
          setMessage(result.message || 'Your email has been verified successfully!');
          
          // Redirect to dashboard after 3 seconds
          setTimeout(() => {
            const role = localStorage.getItem('userRole') || 'student';
            if (role === 'student') {
              navigate('/student-dashboard');
            } else if (role === 'college') {
              navigate('/college-dashboard');
            } else if (role === 'company') {
              navigate('/company-dashboard');
            } else {
              navigate('/student-dashboard'); // Default
            }
          }, 3000);
        } else {
          setStatus('error');
          setMessage(result.message || 'Failed to verify your email. The link may be invalid or expired.');
        }
      } catch (error) {
        console.error('Error verifying email:', error);
        setStatus('error');
        
        // Check if it's an API error with a message
        if (error.response && error.response.data && error.response.data.message) {
          setMessage(error.response.data.message);
        } else {
          setMessage('An error occurred while verifying your email. Please try again later.');
        }
      }
    };

    verifyEmailToken();
  }, [location, verifyEmail, navigate]);

  return (
    <div className="min-h-screen w-full bg-gradient-to-br from-purple-50 via-white to-purple-50 flex items-center justify-center p-4">
      {/* Background decoration */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-purple-200 rounded-full opacity-20 blur-3xl"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-purple-300 rounded-full opacity-20 blur-3xl"></div>
      </div>
      
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="bg-white rounded-2xl shadow-xl shadow-purple-500/10 max-w-md w-full p-8 text-center"
      >
        {status === 'verifying' && (
          <>
            <div className="flex justify-center mb-6">
              <Loader size={64} className="text-purple-600 animate-spin" />
            </div>
            <h2 className="text-2xl font-bold text-gray-800 mb-3">Verifying Your Email</h2>
            <p className="text-gray-600">Please wait while we verify your email address...</p>
          </>
        )}
        
        {status === 'success' && (
          <>
            <div className="flex justify-center mb-6">
              <CheckCircle size={64} className="text-green-600" />
            </div>
            <h2 className="text-2xl font-bold text-gray-800 mb-3">Email Verified!</h2>
            <p className="text-gray-600 mb-6">{message}</p>
            <p className="text-sm text-gray-500">Redirecting you to the dashboard in a few seconds...</p>
            <div className="mt-4">
              <div className="w-full bg-gray-200 rounded-full h-1.5">
                <motion.div 
                  className="bg-green-500 h-1.5 rounded-full" 
                  initial={{ width: 0 }}
                  animate={{ width: "100%" }}
                  transition={{ duration: 3 }}
                />
              </div>
            </div>
          </>
        )}
        
        {status === 'error' && (
          <>
            <div className="flex justify-center mb-6">
              <XCircle size={64} className="text-red-600" />
            </div>
            <h2 className="text-2xl font-bold text-gray-800 mb-3">Verification Failed</h2>
            <p className="text-gray-600 mb-6">{message}</p>
            <div className="flex flex-col sm:flex-row gap-3 justify-center">
              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => navigate('/auth')}
                className="bg-purple-600 text-white py-3 px-6 rounded-lg font-medium hover:bg-purple-700 focus:ring-4 focus:ring-purple-300 focus:outline-none transition-all duration-200"
              >
                Return to Login
              </motion.button>
              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => window.location.reload()}
                className="border border-gray-300 text-gray-700 py-3 px-6 rounded-lg font-medium hover:bg-gray-50 focus:ring-4 focus:ring-gray-200 focus:outline-none transition-all duration-200"
              >
                Try Again
              </motion.button>
            </div>
          </>
        )}
      </motion.div>
    </div>
  );
}
