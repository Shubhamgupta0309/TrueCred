import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function VerificationPendingPage() {
  const navigate = useNavigate();
  const { resendVerificationEmail } = useAuth();
  const [email, setEmail] = useState(localStorage.getItem('verificationEmail') || '');
  const [isResending, setIsResending] = useState(false);
  const [resendMessage, setResendMessage] = useState('');
  const [resendError, setResendError] = useState('');
  const [countdown, setCountdown] = useState(0);
  const [hasResent, setHasResent] = useState(false);

  useEffect(() => {
    // Check if email exists in local storage
    const storedEmail = localStorage.getItem('verificationEmail');
    if (!storedEmail) {
      // If no email in storage, redirect to auth page
      navigate('/auth');
    } else {
      setEmail(storedEmail);
    }
  }, [navigate]);

  useEffect(() => {
    // Handle countdown timer
    if (countdown > 0) {
      const timer = setTimeout(() => {
        setCountdown(countdown - 1);
      }, 1000);
      return () => clearTimeout(timer);
    }
  }, [countdown]);

  const handleResendEmail = async () => {
    if (!email) {
      setResendError('Please enter your email address');
      return;
    }

    if (countdown > 0) {
      return; // Don't allow resending during countdown
    }

    setIsResending(true);
    setResendMessage('');
    setResendError('');

    try {
      await resendVerificationEmail(email);
      setResendMessage('Verification email has been resent. Please check your inbox and spam folder.');
      setHasResent(true);
      // Set countdown to 60 seconds before allowing another resend
      setCountdown(60);
    } catch (error) {
      console.error('Failed to resend verification email:', error);
      setResendError('Failed to resend verification email. Please try again later.');
    } finally {
      setIsResending(false);
    }
  };

  const handleBackToLogin = () => {
    navigate('/auth');
  };

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
        className="relative w-full max-w-md"
      >
        <div className="bg-white rounded-2xl shadow-xl shadow-purple-500/10 overflow-hidden">
          {/* Header */}
          <div className="bg-gradient-to-r from-purple-600 to-purple-700 px-8 py-6 text-center">
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3 }}
            >
              <h2 className="text-2xl font-bold text-white">
                Email Verification Required
              </h2>
              <p className="text-purple-100 text-sm mt-1">
                Please verify your email to continue
              </p>
            </motion.div>
          </div>

          {/* Content */}
          <div className="px-8 py-8">
            <div className="flex flex-col items-center justify-center space-y-6">
              <div className="bg-purple-50 p-4 rounded-lg w-full text-center">
                <svg
                  className="w-16 h-16 text-purple-600 mx-auto mb-4"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
                  />
                </svg>
                <h3 className="text-lg font-semibold text-gray-800 mb-2">Check Your Email</h3>
                <p className="text-gray-600 mb-4">
                  We've sent a verification link to: <strong>{email}</strong>
                </p>
                <p className="text-gray-600 mb-4">
                  Please check your inbox and click the verification link to activate your account.
                </p>
                <div className="text-sm text-gray-500">
                  <p>Don't forget to check your spam folder if you can't find the email.</p>
                </div>
                {hasResent && (
                  <div className="mt-4 p-2 bg-blue-50 text-blue-700 rounded-md text-sm">
                    <p>A new verification email has been sent! Please check your inbox.</p>
                  </div>
                )}
              </div>

              {/* Resend Email Form */}
              <div className="w-full">
                <div className="mb-4">
                  <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
                    Didn't receive the email? Enter your address to resend:
                  </label>
                  <input
                    type="email"
                    id="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    placeholder="Your email address"
                  />
                </div>
                
                {resendMessage && (
                  <div className="mb-4 p-3 bg-green-50 text-green-700 rounded-lg border border-green-200">
                    {resendMessage}
                  </div>
                )}
                
                {resendError && (
                  <div className="mb-4 p-3 bg-red-50 text-red-700 rounded-lg border border-red-200">
                    {resendError}
                  </div>
                )}

                <div className="flex flex-col space-y-3">
                  <motion.button
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={handleResendEmail}
                    disabled={isResending || countdown > 0}
                    className="w-full bg-gradient-to-r from-purple-600 to-purple-700 text-white py-3 px-4 rounded-lg font-medium hover:from-purple-700 hover:to-purple-800 focus:ring-4 focus:ring-purple-300 focus:outline-none transition-all duration-200 shadow-lg hover:shadow-purple-500/25 disabled:opacity-75 disabled:cursor-not-allowed"
                  >
                    {isResending ? (
                      <div className="flex items-center justify-center">
                        <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                        Resending Email...
                      </div>
                    ) : countdown > 0 ? (
                      `Resend Available in ${countdown} seconds`
                    ) : (
                      'Resend Verification Email'
                    )}
                  </motion.button>

                  <motion.button
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={handleBackToLogin}
                    className="w-full bg-white text-purple-700 border border-purple-300 py-3 px-4 rounded-lg font-medium hover:bg-purple-50 focus:ring-4 focus:ring-purple-300 focus:outline-none transition-all duration-200"
                  >
                    Back to Login
                  </motion.button>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="text-center mt-6 text-gray-500 text-sm">
          <p>Need help? Contact our support team</p>
        </div>
      </motion.div>
    </div>
  );
}
