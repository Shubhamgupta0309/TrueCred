import React from 'react';
import { RouterProvider } from 'react-router-dom';
import { useAuth } from './context/AuthContext.jsx';
import router from './router';
import ErrorBoundary from './components/error/ErrorBoundary';

function App() {
  const { loading, error } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-purple-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-purple-600 mx-auto"></div>
          <p className="mt-4 text-gray-700">Loading TrueCred...</p>
          <p className="mt-2 text-sm text-gray-500">Please wait while we set up your session...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-purple-50">
        <div className="bg-white p-8 rounded-lg shadow-lg max-w-md w-full">
          <h2 className="text-2xl font-bold text-red-600 mb-4">Error</h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={() => window.location.reload()}
            className="bg-purple-600 text-white px-4 py-2 rounded hover:bg-purple-700"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <ErrorBoundary>
      <div className="min-h-screen flex flex-col bg-purple-50">      
        <div className="flex-grow flex items-center justify-center">
          <RouterProvider router={router} />
        </div>
      </div>
    </ErrorBoundary>
  );
}

export default App;
