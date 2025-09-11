import React, { useState } from 'react';
import { api } from '../services/api';

const StudentLookup = ({ onStudentSelect }) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchType, setSearchType] = useState('email');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [searchResults, setSearchResults] = useState([]);

  const handleSearch = async (e) => {
    e.preventDefault();
    
    if (!searchQuery.trim()) {
      setError('Please enter a search term');
      return;
    }
    
    setLoading(true);
    setError(null);
    setSearchResults([]);
    
    try {
      const response = await api.get(`/users/search`, {
        params: {
          query: searchQuery,
          type: searchType,
          role: 'student'
        }
      });
      
      if (response.data && Array.isArray(response.data.users)) {
        setSearchResults(response.data.users);
        
        if (response.data.users.length === 0) {
          setError('No students found matching your search criteria');
        }
      } else {
        throw new Error('Invalid response format from server');
      }
    } catch (err) {
      console.error('Student search error:', err);
      setError(err.response?.data?.message || 'Failed to search for students');
      setSearchResults([]);
    } finally {
      setLoading(false);
    }
  };
  
  const handleStudentSelect = (student) => {
    if (onStudentSelect) {
      onStudentSelect(student);
    }
    
    // Clear search results
    setSearchResults([]);
    setSearchQuery('');
  };

  return (
    <div className="mb-6">
      <h3 className="text-lg font-semibold mb-3 text-purple-700">Find Student</h3>
      
      <form onSubmit={handleSearch} className="mb-4">
        <div className="flex flex-col sm:flex-row gap-3">
          <div className="flex-grow">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
              placeholder={searchType === 'email' ? 'Enter student email' : 'Enter wallet address'}
            />
          </div>
          
          <div className="w-full sm:w-40">
            <select
              value={searchType}
              onChange={(e) => setSearchType(e.target.value)}
              className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
            >
              <option value="email">Email</option>
              <option value="wallet">Wallet</option>
            </select>
          </div>
          
          <button
            type="submit"
            className={`bg-purple-600 hover:bg-purple-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline ${loading ? 'opacity-50 cursor-not-allowed' : ''}`}
            disabled={loading}
          >
            {loading ? 'Searching...' : 'Search'}
          </button>
        </div>
      </form>
      
      {error && (
        <div className="bg-red-100 border-l-4 border-red-500 text-red-700 p-3 mb-3" role="alert">
          <p>{error}</p>
        </div>
      )}
      
      {searchResults.length > 0 && (
        <div className="bg-white shadow rounded-md overflow-hidden">
          <ul className="divide-y divide-gray-200">
            {searchResults.map((student) => (
              <li key={student.id} className="p-4 hover:bg-purple-50 cursor-pointer" onClick={() => handleStudentSelect(student)}>
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-medium text-gray-900">{student.name}</h4>
                    <p className="text-sm text-gray-500">{student.email}</p>
                  </div>
                  <div className="text-right">
                    <span className="text-xs bg-purple-100 text-purple-800 px-2 py-1 rounded-full">Student</span>
                    {student.wallet_address && (
                      <p className="text-xs text-gray-500 mt-1 font-mono">{student.wallet_address.substring(0, 6)}...{student.wallet_address.substring(student.wallet_address.length - 4)}</p>
                    )}
                  </div>
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default StudentLookup;
