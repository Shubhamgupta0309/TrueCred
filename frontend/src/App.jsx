import React from 'react';
import { RouterProvider } from 'react-router-dom';
import { useAuth } from './context/AuthContext.jsx';
import router from './router';

function App() {
  const { loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-purple-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-purple-600 mx-auto"></div>
          <p className="mt-4 text-gray-700">Loading TrueCred...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col bg-purple-50">      
      <div className="flex-grow flex items-center justify-center">
        <RouterProvider router={router} />
      </div>
    </div>
  );
}

export default App;
