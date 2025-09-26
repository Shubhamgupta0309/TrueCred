import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Mail, Send } from 'lucide-react';
import { api } from '../../services/api';
import { useAuth } from '../../context/AuthContext';

export default function EmailVerificationReminder({ email, onClose }) {
  const [isResending, setIsResending] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const { resendVerificationEmail, currentUser } = useAuth();
  
  // Use the email from props or currentUser as a fallback
  const userEmail = email || currentUser?.email;

  const handleResendVerification = async () => {
    setIsResending(true);
    setMessage('');
    setError('');

    try {
      // Use the AuthContext method if available, otherwise fall back to direct API call
      let result;
      if (resendVerificationEmail) {
        result = await resendVerificationEmail(userEmail);
      } else {
        const response = await api.post('/api/auth/resend-verification', { email: userEmail });
        result = response.data;
      }
      
      if (result.success) {
        setMessage('Verification email sent! Please check your inbox.');
      } else {
        setError(result.message || 'Failed to send verification email.');
      }
    } catch (err) {
      console.error('Error resending verification:', err);
      setError('Failed to send verification email. Please try again.');
    } finally {
      setIsResending(false);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className={onClose ? "fixed inset-0 flex items-center justify-center p-4 bg-black/50 z-50" : "flex items-center justify-center p-4"}
    >
      <div className="bg-white rounded-2xl shadow-xl max-w-md w-full p-6">
        <div className="text-center mb-6">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-yellow-100 rounded-full mb-4">
            <Mail className="w-8 h-8 text-yellow-600" />
          </div>
          <h2 className="text-2xl font-bold text-gray-800">Email Verification Required</h2>
          <p className="text-gray-600 mt-2">
            We've sent a verification link to <strong>{userEmail}</strong>. 
            Please check your inbox (and spam folder) and click the link to verify your email address.
          </p>
          <p className="text-gray-500 mt-2 text-sm">
            You must verify your email before you can access your account.
          </p>
        </div>

        {message && (
          <div className="mb-4 p-3 bg-green-50 border-l-4 border-green-500 text-green-700">
            {message}
          </div>
        )}

        {error && (
          <div className="mb-4 p-3 bg-red-50 border-l-4 border-red-500 text-red-700">
            {error}
          </div>
        )}

        <div className="flex flex-col sm:flex-row gap-3">
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={handleResendVerification}
            disabled={isResending}
            className="flex-1 bg-yellow-500 text-white py-3 px-4 rounded-lg font-medium hover:bg-yellow-600 focus:ring-4 focus:ring-yellow-300 focus:outline-none transition-all duration-200 flex items-center justify-center gap-2 disabled:opacity-75"
          >
            {isResending ? (
              <>
                <div className="animate-spin h-5 w-5 border-2 border-white border-t-transparent rounded-full" />
                <span>Sending...</span>
              </>
            ) : (
              <>
                <Send className="w-5 h-5" />
                <span>Resend Verification Email</span>
              </>
            )}
          </motion.button>
          {onClose ? (
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={onClose}
              className="flex-1 border border-gray-300 text-gray-700 py-3 px-4 rounded-lg font-medium hover:bg-gray-50 focus:ring-4 focus:ring-gray-200 focus:outline-none transition-all duration-200"
            >
              Close
            </motion.button>
          ) : (
            <motion.a
              href="/auth"
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className="flex-1 border border-gray-300 text-gray-700 py-3 px-4 rounded-lg font-medium hover:bg-gray-50 focus:ring-4 focus:ring-gray-200 focus:outline-none transition-all duration-200 text-center flex items-center justify-center"
            >
              Back to Login
            </motion.a>
          )}
        </div>
      </div>
    </motion.div>
  );
}
