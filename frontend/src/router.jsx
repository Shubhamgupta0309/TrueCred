import { createBrowserRouter } from 'react-router-dom';
import { Navigate } from 'react-router-dom';
import AuthPage from './pages/AuthPage';
import StudentDashboard from './pages/StudentDashboard';
import CollegeDashboard from './pages/CollegeDashboard';
import CompanyDashboard from './pages/CompanyDashboard';
import EmailVerificationPage from './pages/EmailVerificationPage';
import VerificationPendingPage from './pages/VerificationPendingPage';
import TestVerificationLinks from './pages/TestVerificationLinks';
import ProtectedRoute from './components/auth/ProtectedRoute';

/**
 * Application router configuration with future flags enabled
 * to prevent React Router v7 deprecation warnings
 */
const router = createBrowserRouter([
  { path: "/", element: <AuthPage /> },
  { path: "/auth", element: <AuthPage /> },
  { path: "/verify-email", element: <EmailVerificationPage /> },
  { path: "/verification-pending", element: <VerificationPendingPage /> },
  { path: "/test-verification", element: <TestVerificationLinks /> },
  { 
    path: "/student-dashboard", 
    element: <ProtectedRoute element={<StudentDashboard />} allowedRoles={['student']} /> 
  },
  { 
    path: "/college-dashboard", 
    element: <ProtectedRoute element={<CollegeDashboard />} allowedRoles={['college']} /> 
  },
  { 
    path: "/company-dashboard", 
    element: <ProtectedRoute element={<CompanyDashboard />} allowedRoles={['company']} /> 
  },
  { path: "*", element: <Navigate to="/" replace /> }
], {
  future: {
    v7_startTransition: true,
    v7_relativeSplatPath: true
  }
});

export default router;
