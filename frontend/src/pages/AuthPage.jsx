
import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import InputField from '../components/auth/InputField';
import MetaMaskConnect from '../components/auth/MetaMaskConnect';
import ManualWalletInput from '../components/auth/ManualWalletInput';
import ToggleLink from '../components/auth/ToggleLink';
import EmailVerificationReminder from '../components/auth/EmailVerificationReminder';
import { useNavigate, useLocation } from 'react-router-dom';
import { createPageUrl } from '../utils';
import { useAuth } from '../context/AuthContext.jsx';


export default function AuthPage() {
  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    role: '',
    customRole: ''
  });
  const [errors, setErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [successMessage, setSuccessMessage] = useState('');
  const [showVerificationReminder, setShowVerificationReminder] = useState(false);
  const [verificationEmail, setVerificationEmail] = useState('');
  const [showCustomRoleInput, setShowCustomRoleInput] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const { login, register, error: authError, loading, isAuthenticated, user } = useAuth();

  const roleOptions = [
    { value: 'student', label: 'Student' },
    { value: 'college', label: 'College' },
    { value: 'company', label: 'Company' },
    { value: 'other', label: 'Other' }
  ];

  // Redirect if already authenticated
  useEffect(() => {
    if (isAuthenticated && user) {
      console.log('User already authenticated, checking redirect destination');
      
      // Check if user was redirected from a protected route
      const from = location.state?.from?.pathname;
      if (from && from !== '/' && from !== '/auth') {
        console.log('Redirecting back to intended destination:', from);
        navigate(from, { replace: true });
        return;
      }
      
      // Default redirect based on user role
      console.log('Redirecting to dashboard based on role');
      if (user.role === 'student') {
        navigate('/student-dashboard');
      } else if (user.role === 'college') {
        navigate('/college-dashboard');
      } else if (user.role === 'company') {
        navigate('/company-dashboard');
      } else {
        navigate('/student-dashboard'); // Default
      }
    }
  }, [isAuthenticated, user, navigate, location]);

  // Reset form when switching between login/register
  useEffect(() => {
    setFormData({
      email: '',
      password: '',
      confirmPassword: '',
      role: '',
      customRole: ''
    });
    setErrors({});
    setSuccessMessage('');
    setShowCustomRoleInput(false);
  }, [isLogin]);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    
    // Check if the role is "other" to show the custom role input
    if (name === 'role' && value === 'other') {
      setShowCustomRoleInput(true);
    } else if (name === 'role' && value !== 'other') {
      setShowCustomRoleInput(false);
    }
    
    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
  };

  const validateForm = () => {
    const newErrors = {};

    // Email validation
    if (!formData.email) {
      newErrors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Please enter a valid email address';
    }

    // Password validation
    if (!formData.password) {
      newErrors.password = 'Password is required';
    } else if (formData.password.length < 6) {
      newErrors.password = 'Password must be at least 6 characters';
    }

    // Register-specific validations
    if (!isLogin) {
      if (!formData.confirmPassword) {
        newErrors.confirmPassword = 'Please confirm your password';
      } else if (formData.password !== formData.confirmPassword) {
        newErrors.confirmPassword = 'Passwords do not match';
      }
      if (!formData.role) {
        newErrors.role = 'Please select your role';
      }
      if (formData.role === 'other' && !formData.customRole) {
        newErrors.customRole = 'Please specify your role';
      }
    }

    return newErrors;
  };

  const handleSubmit = async (e) => {
    e.preventDefault(); // Prevent the default form submission
    const newErrors = validateForm();

    if (Object.keys(newErrors).length > 0) {
      console.log('Form validation errors:', newErrors);
      setErrors(newErrors);
      return;
    }

    setIsSubmitting(true);
    setErrors({});
    setSuccessMessage('');
    
    console.log('Submitting form data:', formData);
    console.log('Current auth error state:', authError);

    try {
      if (isLogin) {
        // Handle login with real API
        const result = await login(formData.email, formData.password);
        
        if (result === true) {
          // Clear any existing errors
          setErrors({});
          setSuccessMessage('Login successful! Redirecting...');
          
          // Redirect based on role after a short delay
          setTimeout(() => {
            const role = localStorage.getItem('userRole');
            if (role === 'issuer') {
              navigate('/issuer-dashboard');
            } else {
              navigate('/holder-dashboard'); // Default for holder
            }
          }, 1500);
        } else if (result && result.needsVerification) {
          // Store email for verification page
          localStorage.setItem('verificationEmail', result.email || formData.email);
          
          // Redirect to verification pending page
          setTimeout(() => {
            navigate('/verification-pending');
          }, 500);
        } else {
          // Display the error from auth system with a clear message
          console.log('Authentication error from context:', authError);
          
          // Use the most specific error message available
          const errorMessage = authError || 
                              (result && result.message) || 
                              'Invalid email or password. Please try again.';
          
          setErrors({ general: errorMessage });
          // Make sure the error is prominently displayed
          setTimeout(() => {
            document.querySelector('.auth-error-message')?.scrollIntoView({ behavior: 'smooth' });
          }, 100);
          setSuccessMessage('');
        }
      } else {
        // Handle registration with real API
        // Generate username from email and make sure it only contains valid characters
        const emailPrefix = formData.email.split('@')[0];
        // Replace any non-alphanumeric characters (except underscore) with empty string
        let sanitizedUsername = emailPrefix.replace(/[^a-zA-Z0-9_]/g, '');
        
        // If username would be empty after sanitization, use a default plus random number
        if (!sanitizedUsername || sanitizedUsername.length < 3) {
          const randomSuffix = Math.floor(1000 + Math.random() * 9000); // 4-digit random number
          sanitizedUsername = `user${randomSuffix}`;
        }
        
        const userData = {
          username: sanitizedUsername,
          email: formData.email,
          password: formData.password,
          // No name collected on UI; provide a sensible default for backend
          name: `User ${sanitizedUsername}`,
          role: formData.role === 'other' ? formData.customRole : formData.role
        };
        
        const result = await register(userData);
        
        if (result.success) {
          // Check if email verification is required
          if (result.needsEmailVerification) {
            // Store the email for verification page
            localStorage.setItem('verificationEmail', formData.email);
            
            setSuccessMessage('Account created successfully! Please verify your email.');
            setErrors({}); // Clear any errors
            
            // Redirect to verification pending page
            setTimeout(() => {
              navigate('/verification-pending');
            }, 1500);
          } else {
            // User is verified and logged in, redirect to dashboard
            setSuccessMessage('Account created successfully! Redirecting to dashboard...');
            setErrors({}); // Clear any errors
            
            // Redirect to dashboard based on role
            setTimeout(() => {
              const role = localStorage.getItem('userRole');
              const redirectPath = role === 'issuer' ? '/issuer-dashboard' : '/holder-dashboard';
              navigate(redirectPath);
            }, 1500);
          }
        } else {
          // Display the error from auth system
          console.log('Registration error from context:', authError);
          
          // Use the most specific error message available
          const errorMessage = result.error || authError || 'Registration failed. Please try again.';
          
          setErrors({ general: errorMessage });
          // Make sure the error is prominently displayed
          setTimeout(() => {
            document.querySelector('.auth-error-message')?.scrollIntoView({ behavior: 'smooth' });
          }, 100);
          setSuccessMessage('');
        }
      }
    } catch (error) {
      console.error('Auth error:', error);
      setErrors({ general: 'An unexpected error occurred. Please try again.' });
      // Ensure the error is visible
      setTimeout(() => {
        document.querySelector('.auth-error-message')?.scrollIntoView({ behavior: 'smooth' });
      }, 100);
    } finally {
      setIsSubmitting(false);
      
      // Log the final state for debugging
      console.log('Form submission completed');
      console.log('Current errors:', errors);
      console.log('Auth error after submission:', authError);
    }
  };

  const toggleMode = () => {
    setIsLogin(!isLogin);
  };

  return (
    <div className="min-h-screen w-full bg-gradient-to-br from-purple-50 via-white to-purple-50 flex items-center justify-center p-4">
      {/* Background decoration */}
       <div className="absolute inset-0 overflow-hidden">
      <div className="absolute -top-40 -right-40 w-80 h-80 bg-purple-200 rounded-full opacity-20 blur-3xl"></div>
      <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-purple-300 rounded-full opacity-20 blur-3xl"></div>
    </div>

      {/* Email Verification Reminder */}
      <AnimatePresence>
        {showVerificationReminder && (
          <EmailVerificationReminder 
            email={verificationEmail} 
            onClose={() => setShowVerificationReminder(false)} 
          />
        )}
      </AnimatePresence>

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
              key={isLogin}
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3 }}
            >
              <h2 className="text-2xl font-bold text-white">
                {isLogin ? 'Welcome Back' : 'Create Account'}
              </h2>
              <p className="text-purple-100 text-sm mt-1">
                {isLogin ? 'Sign in to your account' : 'Join our community today'}
              </p>
            </motion.div>
          </div>

          {/* Success Message */}
          <AnimatePresence>
            {successMessage && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="bg-green-50 border-l-4 border-green-500 px-8 py-4"
              >
                <div className="flex items-center">
                  <svg className="w-5 h-5 text-green-500 mr-3" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                  <p className="text-green-700 text-sm font-medium">{successMessage}</p>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Form */}
          <div className="px-8 py-6">
            <form onSubmit={handleSubmit} className="space-y-6" noValidate>
              <AnimatePresence mode="wait">
                <motion.div
                  key={isLogin ? 'login' : 'register'}
                  initial={{ opacity: 0, x: isLogin ? -20 : 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: isLogin ? 20 : -20 }}
                  transition={{ duration: 0.3 }}
                  className="space-y-4"
                >
                  <InputField
                    label="Email Address"
                    type="email"
                    name="email"
                    id="email"
                    value={formData.email}
                    onChange={handleInputChange}
                    error={errors.email}
                    placeholder="Enter your email"
                    required
                    autoComplete="email"
                  />

                  <InputField
                    label="Password"
                    type="password"
                    name="password"
                    id="password"
                    value={formData.password}
                    onChange={handleInputChange}
                    error={errors.password}
                    placeholder="Enter your password"
                    required
                    autoComplete="current-password"
                  />

                  {!isLogin && (
                    <>
                      <InputField
                        label="Confirm Password"
                        type="password"
                        name="confirmPassword"
                        id="confirmPassword"
                        value={formData.confirmPassword}
                        onChange={handleInputChange}
                        error={errors.confirmPassword}
                        placeholder="Confirm your password"
                        required
                        autoComplete="new-password"
                      />
                      
                      <InputField
                        label="Role"
                        type="select"
                        name="role"
                        id="role"
                        value={formData.role}
                        onChange={handleInputChange}
                        error={errors.role}
                        options={roleOptions}
                        required
                        autoComplete="off"
                      />
                      
                      {/* Show custom role input when "Other" is selected */}
                      {showCustomRoleInput && (
                        <InputField
                          label="Specify Your Role"
                          type="text"
                          name="customRole"
                          id="customRole"
                          value={formData.customRole}
                          onChange={handleInputChange}
                          error={errors.customRole}
                          placeholder="Enter your specific role"
                          required
                          autoComplete="off"
                        />
                      )}
                    </>
                  )}
                </motion.div>
              </AnimatePresence>

              {/* General Error Message */}
              {errors.general && (
                <motion.div 
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="mt-4 bg-red-50 border-l-4 border-red-500 p-4 shadow-sm auth-error-message"
                >
                  <div className="flex">
                    <div className="flex-shrink-0">
                      <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                      </svg>
                    </div>
                    <div className="ml-3">
                      <p className="text-sm font-medium text-red-700">{errors.general}</p>
                    </div>
                  </div>
                </motion.div>
              )}

              {/* Submit Button */}
              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                type="submit"
                disabled={isSubmitting}
                className="w-full bg-gradient-to-r from-purple-600 to-purple-700 text-white py-3 px-4 rounded-lg font-medium hover:from-purple-700 hover:to-purple-800 focus:ring-4 focus:ring-purple-300 focus:outline-none transition-all duration-200 shadow-lg hover:shadow-purple-500/25 disabled:opacity-75 disabled:cursor-not-allowed"
              >
                {isSubmitting ? (
                  <div className="flex items-center justify-center">
                    <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    {isLogin ? 'Signing In...' : 'Creating Account...'}
                  </div>
                ) : (
                  isLogin ? 'Sign In' : 'Create Account'
                )}
              </motion.button>

              {/* Forgot Password Link (Login only) */}
              {isLogin && (
                <div className="text-center">
                  <button
                    type="button"
                    className="text-sm text-purple-600 hover:text-purple-800 transition-colors duration-200"
                  >
                    Forgot your password?
                  </button>
                </div>
              )}

              {/* Registration note about wallet connection */}
              {!isLogin && (
                <div className="mt-4 bg-blue-50 border-l-4 border-blue-500 p-4">
                  <div className="flex">
                    <div className="flex-shrink-0">
                      <svg className="h-5 w-5 text-blue-400" viewBox="0 0 20 20" fill="currentColor">
                        <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2h-1V9a1 1 0 00-1-1z" clipRule="evenodd" />
                      </svg>
                    </div>
                    <div className="ml-3">
                      <p className="text-sm text-blue-700">
                        Create an account with your details first. You'll be able to connect your wallet after registration.
                      </p>
                    </div>
                  </div>
                </div>
              )}
            </form>

            {/* MetaMask Connect - Only shown on login page */}
            {isLogin && (
              <div className="mt-6">
                <div className="relative">
                  <div className="absolute inset-0 flex items-center">
                    <div className="w-full border-t border-gray-300"></div>
                  </div>
                  <div className="relative flex justify-center text-sm">
                    <span className="px-2 bg-white text-gray-500">Or login with wallet</span>
                  </div>
                </div>
                
                <div className="mt-4">
                  <MetaMaskConnect />
                  <ManualWalletInput />
                </div>
              </div>
            )}

            {/* Toggle Link */}
            <ToggleLink isLogin={isLogin} onToggle={toggleMode} />
          </div>
        </div>

        {/* Footer */}
        <div className="text-center mt-6 text-gray-500 text-sm">
          <p>By continuing, you agree to our Terms of Service and Privacy Policy</p>
        </div>
      </motion.div>
    </div>
  );
}
