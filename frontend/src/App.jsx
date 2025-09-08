import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';

// Import your components
import AuthPage from './pages/AuthPage';
import StudentDashboard from './pages/StudentDashboard';
import CollegeDashboard from './pages/CollegeDashboard';
import CompanyDashboard from './pages/CompanyDashboard';

function App() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-purple-50">
      <Router>
        <Routes>
          {/* Route for authentication page */}
          <Route path="/" element={<AuthPage />} />

        {/* Route for student dashboard */}
        <Route path="/student-dashboard" element={<StudentDashboard />} />

        {/* Route for college dashboard */}
        <Route path="/college-dashboard" element={<CollegeDashboard />} />

        {/* Route for company dashboard */}
        <Route path="/company-dashboard" element={<CompanyDashboard />} />

        {/* Add more routes as needed */}
      </Routes>
    </Router>
    </div>
  );
}

export default App;
