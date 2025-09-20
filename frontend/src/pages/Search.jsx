import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Search, Filter, MapPin, Building, Users, GraduationCap, Calendar, ChevronDown, ChevronUp, X } from 'lucide-react';
import { useAuth } from '../context/AuthContext.jsx';
import { api } from '../services/api';

export default function SearchPage() {
  const { user } = useAuth();
  const [searchQuery, setSearchQuery] = useState('');
  const [searchType, setSearchType] = useState('all');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showAdvancedFilters, setShowAdvancedFilters] = useState(false);
  const [filters, setFilters] = useState({
    // Basic filters
    institutionType: '',
    location: '',
    program: '',
    verified: false,

    // Advanced filters
    country: '',
    state: '',
    city: '',
    graduationYear: '',
    graduationYearAfter: '',
    graduationYearBefore: '',
    foundedAfter: '',
    foundedBefore: '',
    accreditationStatus: '',
    hasCredentials: false,
    hasExperiences: false,
    startDate: '',
    endDate: ''
  });

  // Search types
  const searchTypes = [
    { id: 'all', label: 'All', icon: Search },
    { id: 'institutions', label: 'Institutions', icon: Building },
    { id: 'students', label: 'Students', icon: Users },
    { id: 'credentials', label: 'Credentials', icon: GraduationCap }
  ];

  // Institution types
  const institutionTypes = [
    { value: '', label: 'All Types' },
    { value: 'university', label: 'University' },
    { value: 'college', label: 'College' },
    { value: 'company', label: 'Company' },
    { value: 'school', label: 'School' },
    { value: 'nonprofit', label: 'Non-Profit' },
    { value: 'government', label: 'Government' }
  ];

  // Accreditation statuses
  const accreditationStatuses = [
    { value: '', label: 'All Statuses' },
    { value: 'accredited', label: 'Accredited' },
    { value: 'pending', label: 'Pending' },
    { value: 'not_accredited', label: 'Not Accredited' }
  ];

  // Perform search
  const performSearch = async () => {
    if (!searchQuery.trim() && searchType !== 'all') return;

    setLoading(true);
    try {
      let endpoint = '/api/search/';
      let params = { q: searchQuery };

      if (searchType === 'institutions') {
        endpoint = '/api/search/institutions';
        params = {
          ...params,
          type: filters.institutionType,
          location: filters.location,
          country: filters.country,
          state: filters.state,
          city: filters.city,
          verified: filters.verified,
          accreditation_status: filters.accreditationStatus,
          founded_after: filters.foundedAfter,
          founded_before: filters.foundedBefore
        };
      } else if (searchType === 'students') {
        endpoint = '/api/search/students';
        params = {
          ...params,
          institution: filters.location,
          program: filters.program,
          graduation_year: filters.graduationYear,
          graduation_year_after: filters.graduationYearAfter,
          graduation_year_before: filters.graduationYearBefore,
          location: filters.location,
          country: filters.country,
          state: filters.state,
          city: filters.city,
          verified: filters.verified,
          has_credentials: filters.hasCredentials,
          has_experiences: filters.hasExperiences
        };
      } else if (searchType === 'credentials') {
        endpoint = '/api/search/credentials';
        params = {
          ...params,
          verified: filters.verified,
          start_date: filters.startDate,
          end_date: filters.endDate
        };
      }

      // Remove empty parameters
      Object.keys(params).forEach(key => {
        if (params[key] === '' || params[key] === null || params[key] === undefined) {
          delete params[key];
        }
      });

      const response = await api.get(endpoint, { params });
      const data = response.data.data;
      setResults(data.results || data.institutions || data.students || data.credentials || []);
    } catch (error) {
      console.error('Search error:', error);
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  // Handle search input
  const handleSearch = (e) => {
    e.preventDefault();
    performSearch();
  };

  // Handle filter changes
  const handleFilterChange = (key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  // Clear all filters
  const clearFilters = () => {
    setFilters({
      institutionType: '',
      location: '',
      program: '',
      verified: false,
      country: '',
      state: '',
      city: '',
      graduationYear: '',
      graduationYearAfter: '',
      graduationYearBefore: '',
      foundedAfter: '',
      foundedBefore: '',
      accreditationStatus: '',
      hasCredentials: false,
      hasExperiences: false,
      startDate: '',
      endDate: ''
    });
  };

  // Check if any advanced filters are active
  const hasActiveFilters = () => {
    return Object.entries(filters).some(([key, value]) => {
      if (key === 'verified') return value === true;
      if (key === 'hasCredentials') return value === true;
      if (key === 'hasExperiences') return value === true;
      return value !== '';
    });
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-6xl mx-auto px-4 py-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-8"
        >
          <h1 className="text-3xl font-bold text-gray-800 mb-2">Advanced Search & Discovery</h1>
          <p className="text-gray-600">Find institutions, students, and verified credentials with powerful filters</p>
        </motion.div>

        {/* Search Form */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-white rounded-2xl shadow-lg p-6 mb-8"
        >
          {/* Search Type Tabs */}
          <div className="flex flex-wrap gap-2 mb-6">
            {searchTypes.map((type) => {
              const Icon = type.icon;
              return (
                <button
                  key={type.id}
                  onClick={() => setSearchType(type.id)}
                  className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-colors ${
                    searchType === type.id
                      ? 'bg-purple-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  {type.label}
                </button>
              );
            })}
          </div>

          {/* Search Input */}
          <form onSubmit={handleSearch} className="mb-6">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder={`Search ${searchType}...`}
                className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              />
            </div>
          </form>

          {/* Basic Filters */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
            {searchType === 'institutions' && (
              <>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Institution Type</label>
                  <select
                    value={filters.institutionType}
                    onChange={(e) => handleFilterChange('institutionType', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                  >
                    {institutionTypes.map(type => (
                      <option key={type.value} value={type.value}>{type.label}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Location</label>
                  <input
                    type="text"
                    value={filters.location}
                    onChange={(e) => handleFilterChange('location', e.target.value)}
                    placeholder="City, State, Country"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                  />
                </div>
              </>
            )}

            {searchType === 'students' && (
              <>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Institution</label>
                  <input
                    type="text"
                    value={filters.location}
                    onChange={(e) => handleFilterChange('location', e.target.value)}
                    placeholder="Institution name"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Program</label>
                  <input
                    type="text"
                    value={filters.program}
                    onChange={(e) => handleFilterChange('program', e.target.value)}
                    placeholder="Degree/Program"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                  />
                </div>
              </>
            )}

            {searchType === 'credentials' && (
              <>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Start Date</label>
                  <input
                    type="date"
                    value={filters.startDate}
                    onChange={(e) => handleFilterChange('startDate', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">End Date</label>
                  <input
                    type="date"
                    value={filters.endDate}
                    onChange={(e) => handleFilterChange('endDate', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                  />
                </div>
              </>
            )}

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Verification Status</label>
              <select
                value={filters.verified}
                onChange={(e) => handleFilterChange('verified', e.target.value === 'true')}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
              >
                <option value={false}>All</option>
                <option value={true}>Verified Only</option>
              </select>
            </div>
          </div>

          {/* Advanced Filters Toggle */}
          <div className="mb-4">
            <button
              type="button"
              onClick={() => setShowAdvancedFilters(!showAdvancedFilters)}
              className="flex items-center gap-2 text-purple-600 hover:text-purple-700 font-medium"
            >
              <Filter className="w-4 h-4" />
              Advanced Filters
              {hasActiveFilters() && (
                <span className="bg-purple-100 text-purple-800 text-xs px-2 py-1 rounded-full">
                  Active
                </span>
              )}
              {showAdvancedFilters ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
            </button>
          </div>

          {/* Advanced Filters */}
          {showAdvancedFilters && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="border-t pt-4 mb-6"
            >
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                {/* Location Filters */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Country</label>
                  <input
                    type="text"
                    value={filters.country}
                    onChange={(e) => handleFilterChange('country', e.target.value)}
                    placeholder="Country"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">State/Province</label>
                  <input
                    type="text"
                    value={filters.state}
                    onChange={(e) => handleFilterChange('state', e.target.value)}
                    placeholder="State/Province"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">City</label>
                  <input
                    type="text"
                    value={filters.city}
                    onChange={(e) => handleFilterChange('city', e.target.value)}
                    placeholder="City"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                  />
                </div>
              </div>

              {/* Institution-specific filters */}
              {searchType === 'institutions' && (
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Founded After</label>
                    <input
                      type="date"
                      value={filters.foundedAfter}
                      onChange={(e) => handleFilterChange('foundedAfter', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Founded Before</label>
                    <input
                      type="date"
                      value={filters.foundedBefore}
                      onChange={(e) => handleFilterChange('foundedBefore', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Accreditation Status</label>
                    <select
                      value={filters.accreditationStatus}
                      onChange={(e) => handleFilterChange('accreditationStatus', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                    >
                      {accreditationStatuses.map(status => (
                        <option key={status.value} value={status.value}>{status.label}</option>
                      ))}
                    </select>
                  </div>
                </div>
              )}

              {/* Student-specific filters */}
              {searchType === 'students' && (
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Graduation Year</label>
                    <input
                      type="number"
                      value={filters.graduationYear}
                      onChange={(e) => handleFilterChange('graduationYear', e.target.value)}
                      placeholder="2024"
                      min="1900"
                      max="2030"
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Graduated After</label>
                    <input
                      type="number"
                      value={filters.graduationYearAfter}
                      onChange={(e) => handleFilterChange('graduationYearAfter', e.target.value)}
                      placeholder="2020"
                      min="1900"
                      max="2030"
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Graduated Before</label>
                    <input
                      type="number"
                      value={filters.graduationYearBefore}
                      onChange={(e) => handleFilterChange('graduationYearBefore', e.target.value)}
                      placeholder="2030"
                      min="1900"
                      max="2030"
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                    />
                  </div>
                </div>
              )}

              {/* Content filters for students */}
              {searchType === 'students' && (
                <div className="flex flex-wrap gap-4 mb-4">
                  <label className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      checked={filters.hasCredentials}
                      onChange={(e) => handleFilterChange('hasCredentials', e.target.checked)}
                      className="w-4 h-4 text-purple-600 rounded focus:ring-purple-500"
                    />
                    <span className="text-sm font-medium text-gray-700">Has Credentials</span>
                  </label>
                  <label className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      checked={filters.hasExperiences}
                      onChange={(e) => handleFilterChange('hasExperiences', e.target.checked)}
                      className="w-4 h-4 text-purple-600 rounded focus:ring-purple-500"
                    />
                    <span className="text-sm font-medium text-gray-700">Has Experiences</span>
                  </label>
                </div>
              )}

              {/* Clear filters button */}
              {hasActiveFilters() && (
                <div className="flex justify-end">
                  <button
                    type="button"
                    onClick={clearFilters}
                    className="flex items-center gap-2 px-4 py-2 text-gray-600 hover:text-gray-800 font-medium"
                  >
                    <X className="w-4 h-4" />
                    Clear All Filters
                  </button>
                </div>
              )}
            </motion.div>
          )}

          {/* Search Button */}
          <div className="flex justify-end">
            <button
              type="submit"
              disabled={loading || (!searchQuery.trim() && searchType !== 'all')}
              className="px-6 py-2 bg-purple-600 text-white rounded-lg font-medium hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {loading ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  Searching...
                </>
              ) : (
                <>
                  <Search className="w-4 h-4" />
                  Search
                </>
              )}
            </button>
          </div>
        </motion.div>

        {/* Results */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
        >
          {results.length > 0 ? (
            <div className="bg-white rounded-2xl shadow-lg p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-bold text-gray-800">
                  Search Results ({results.length})
                </h2>
                <div className="text-sm text-gray-600">
                  {searchType === 'all' ? 'All types' : searchType.charAt(0).toUpperCase() + searchType.slice(1)}
                </div>
              </div>

              <div className="space-y-4">
                {results.map((result, index) => (
                  <motion.div
                    key={result.id || index}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.05 }}
                    className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          <h3 className="text-lg font-semibold text-gray-800">
                            {result.name || result.title || `${result.first_name} ${result.last_name}`}
                          </h3>
                          {result.verified && (
                            <span className="bg-green-100 text-green-800 text-xs px-2 py-1 rounded-full">
                              Verified
                            </span>
                          )}
                          {result.type && (
                            <span className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded-full">
                              {result.type}
                            </span>
                          )}
                        </div>

                        {result.description && (
                          <p className="text-gray-600 mb-2">{result.description}</p>
                        )}

                        <div className="flex flex-wrap gap-4 text-sm text-gray-500">
                          {result.location && (
                            <div className="flex items-center gap-1">
                              <MapPin className="w-4 h-4" />
                              {result.location}
                            </div>
                          )}
                          {result.institution && (
                            <div className="flex items-center gap-1">
                              <Building className="w-4 h-4" />
                              {result.institution}
                            </div>
                          )}
                          {result.program && (
                            <div className="flex items-center gap-1">
                              <GraduationCap className="w-4 h-4" />
                              {result.program}
                            </div>
                          )}
                          {result.graduation_year && (
                            <div className="flex items-center gap-1">
                              <Calendar className="w-4 h-4" />
                              Graduated {result.graduation_year}
                            </div>
                          )}
                          {result.founded_date && (
                            <div className="flex items-center gap-1">
                              <Calendar className="w-4 h-4" />
                              Founded {new Date(result.founded_date).getFullYear()}
                            </div>
                          )}
                          {result.issued_date && (
                            <div className="flex items-center gap-1">
                              <Calendar className="w-4 h-4" />
                              Issued {new Date(result.issued_date).toLocaleDateString()}
                            </div>
                          )}
                        </div>

                        {result.skills && result.skills.length > 0 && (
                          <div className="mt-2">
                            <div className="flex flex-wrap gap-1">
                              {result.skills.slice(0, 5).map((skill, skillIndex) => (
                                <span
                                  key={skillIndex}
                                  className="bg-purple-100 text-purple-800 text-xs px-2 py-1 rounded"
                                >
                                  {skill}
                                </span>
                              ))}
                              {result.skills.length > 5 && (
                                <span className="text-xs text-gray-500">
                                  +{result.skills.length - 5} more
                                </span>
                              )}
                            </div>
                          </div>
                        )}
                      </div>

                      <div className="ml-4">
                        <button className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors">
                          View Details
                        </button>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>

              {/* Load More Button */}
              {results.length >= 20 && (
                <div className="text-center mt-6">
                  <button className="px-6 py-2 border border-purple-600 text-purple-600 rounded-lg hover:bg-purple-50 transition-colors">
                    Load More Results
                  </button>
                </div>
              )}
            </div>
          ) : searchQuery && !loading ? (
            <div className="text-center py-12">
              <Search className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-gray-600 mb-2">No results found</h3>
              <p className="text-gray-500">
                Try adjusting your search terms or filters to find what you're looking for.
              </p>
            </div>
          ) : (
            <div className="text-center py-12">
              <Search className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-gray-600 mb-2">Start your search</h3>
              <p className="text-gray-500">
                Enter a search term above to find institutions, students, or credentials.
              </p>
            </div>
          )}
        </motion.div>
      </div>
    </div>
  );
}