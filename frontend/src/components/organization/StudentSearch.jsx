import React, { useState, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import { Search, User, FileText, BadgeCheck, X } from 'lucide-react';
import { api } from '../../services/api';
import { useNavigate } from 'react-router-dom';

export default function StudentSearch({ onStudentSelect }) {
  const [searchTerm, setSearchTerm] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [searchTimeout, setSearchTimeout] = useState(null);
  const searchInputRef = useRef(null);
  const navigate = useNavigate();
  
  // Effect for debounced search
  useEffect(() => {
    if (searchTerm.length >= 3) {
      // Clear previous timeout
      if (searchTimeout) {
        clearTimeout(searchTimeout);
      }
      
      // Set new timeout for search
      const timeout = setTimeout(() => {
        searchStudents(searchTerm);
      }, 500);
      
      setSearchTimeout(timeout);
    } else {
      setSearchResults([]);
    }
    
    return () => {
      if (searchTimeout) {
        clearTimeout(searchTimeout);
      }
    };
  }, [searchTerm]);
  
  // Function to search for students
  const searchStudents = async (query) => {
    if (query.length < 3) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const response = await api.get(`/api/organization/search-students?query=${encodeURIComponent(query)}`);
      
      if (response.data.success) {
        setSearchResults(response.data.data.students || []);
      } else {
        setError(response.data.message || 'Error searching for students');
        setSearchResults([]);
      }
    } catch (error) {
      console.error('Error searching for students:', error);
      setError('Failed to search for students. Please try again.');
      // Leave results empty on error (no mock fallbacks)
      setSearchResults([]);
    } finally {
      setLoading(false);
    }
  };
  
  // Handle direct TrueCred ID search
  const searchByTrueCred = async () => {
    // Check if input is in TrueCred ID format (TC followed by 6 digits)
    const truecredPattern = /^TC\d{6}$/;
    
    if (truecredPattern.test(searchTerm)) {
      setLoading(true);
      setError(null);
      
      try {
        const response = await api.get(`/api/organization/student/${encodeURIComponent(searchTerm)}`);
        
        if (response.data.success) {
          setSearchResults([response.data.data.student]);
        } else {
          setError(response.data.message || 'Student not found');
          setSearchResults([]);
        }
      } catch (error) {
        console.error('Error finding student by TrueCred ID:', error);
        setError('Failed to find student. Please check the TrueCred ID and try again.');
        setSearchResults([]);
      } finally {
        setLoading(false);
      }
    }
  };
  
  // Handle search input change
  const handleSearchChange = (e) => {
    setSearchTerm(e.target.value);
  };
  
  // Handle search form submit
  const handleSearchSubmit = (e) => {
    e.preventDefault();
    searchByTrueCred();
  };
  
  // Handle student selection
  const handleStudentSelect = (student) => {
    if (onStudentSelect) {
      onStudentSelect(student);
    }
    
    // Clear search
    setSearchTerm('');
    setSearchResults([]);
    
    // Focus back on search input
    if (searchInputRef.current) {
      searchInputRef.current.focus();
    }
  };
  
  // Clear search
  const clearSearch = () => {
    setSearchTerm('');
    setSearchResults([]);
    setError(null);
    
    // Focus on search input
    if (searchInputRef.current) {
      searchInputRef.current.focus();
    }
  };
  
  return (
    <div className="mb-6">
      <h2 className="text-xl font-bold text-gray-800 mb-4">Search for Students</h2>
      
      <form onSubmit={handleSearchSubmit} className="mb-4">
        <div className="relative">
          <input
            ref={searchInputRef}
            type="text"
            value={searchTerm}
            onChange={handleSearchChange}
            placeholder="Search by name, email, or TrueCred ID (e.g., TC123456)"
            className="w-full px-4 py-2 pl-10 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-5 w-5" />
          
          {searchTerm && (
            <button
              type="button"
              onClick={clearSearch}
              className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
            >
              <X className="h-5 w-5" />
            </button>
          )}
        </div>
        
        <p className="text-sm text-gray-500 mt-2">
          Enter at least 3 characters to search, or enter a complete TrueCred ID (TC######) for exact match.
        </p>
      </form>
      
      {error && (
        <div className="p-4 mb-4 bg-red-50 rounded-lg border border-red-200">
          <p className="text-red-700">{error}</p>
        </div>
      )}
      
      {loading ? (
        <div className="p-4 text-center">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
          <p className="mt-2 text-gray-600">Searching...</p>
        </div>
      ) : (
        searchResults.length > 0 && (
          <motion.div
            className="bg-white rounded-lg shadow-md border"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
          >
            <h3 className="p-4 border-b text-lg font-medium text-gray-800">
              Search Results
            </h3>
            
            <div className="divide-y">
              {searchResults.map(student => (
                <motion.div
                  key={student.id}
                  className="p-4 hover:bg-gray-50 cursor-pointer flex items-center justify-between"
                  whileHover={{ backgroundColor: 'rgba(243, 244, 246, 1)' }}
                  onClick={() => {
                    // If a parent provided a selection handler, call it (e.g., for uploading credentials).
                    if (onStudentSelect) {
                      handleStudentSelect(student);
                    } else {
                      // Otherwise navigate to the student's public profile page.
                      navigate(`/students/${encodeURIComponent(student.truecred_id)}`);
                    }
                  }}
                >
                  <div className="flex items-center">
                    <div className="bg-blue-100 rounded-full p-2 mr-3">
                      <User className="h-6 w-6 text-blue-600" />
                    </div>
                    
                    <div>
                      <h4 className="font-medium text-gray-800">{student.name}</h4>
                      <p className="text-sm text-gray-600">{student.email}</p>
                      <p className="text-xs font-mono text-blue-700 mt-1">{student.truecred_id}</p>
                    </div>
                  </div>
                  
                  <div className="flex items-center">
                    {student.is_affiliated ? (
                      <div className="flex items-center text-green-600 text-sm">
                        <BadgeCheck className="h-5 w-5 mr-1" />
                        <span>Affiliated</span>
                      </div>
                    ) : (
                      <button
                        className="flex items-center text-blue-600 hover:text-blue-800 text-sm"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleStudentSelect(student);
                        }}
                      >
                        <FileText className="h-5 w-5 mr-1" />
                        <span>Select</span>
                      </button>
                    )}
                  </div>
                </motion.div>
              ))}
            </div>
          </motion.div>
        )
      )}
    </div>
  );
}
