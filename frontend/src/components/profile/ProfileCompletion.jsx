import React, { useState, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import { useAuth } from '../../context/AuthContext';
import { api, organizationService } from '../../services/api';
import { ChevronDown } from 'lucide-react';

export default function ProfileCompletion({ onComplete, initialUser }) {
  const { user, updateUser } = useAuth();
  const dropdownRef = useRef(null);

  const [formData, setFormData] = useState({
    firstName: user?.first_name || '',
    lastName: user?.last_name || '',
    education: [],
    currentEducation: {
      institution: '',
      institutionId: '',
      degree: '',
      fieldOfStudy: '',
      startDate: '',
      endDate: '',
      current: false
    },
    searchText: '',
    searchResults: []
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [toast, setToast] = useState(null);
  const [confirmRemoveId, setConfirmRemoveId] = useState(null);
  const [showSearchResults, setShowSearchResults] = useState(false);

  // State for degree and course dropdowns
  const [showDegreeDropdown, setShowDegreeDropdown] = useState(false);
  const [showCourseDropdown, setShowCourseDropdown] = useState(false);
  const degreeRef = useRef(null);
  const courseRef = useRef(null);

  // Predefined degree options
  const degreeOptions = [
    "Bachelor of Engineering (B.E.)",
    "Bachelor of Technology (B.Tech.)",
    "Master of Engineering (M.E.)",
    "Master of Technology (M.Tech.)",
    "Master of Computer Applications (MCA)",
    "Bachelor of Science (B.Sc.)",
    "Master of Science (M.Sc.)",
    "Doctor of Philosophy (Ph.D.)"
  ];

  // Predefined course options
  const courseOptions = [
    "Information Technology",
    "Computer Engineering",
    "Artificial Intelligence",
    "Data Science",
    "Mechanical Engineering",
    "Electrical Engineering",
    "Civil Engineering",
    "Electronics & Communication"
  ];

  // Hydrate formData from initialUser if provided
  useEffect(() => {
    const src = initialUser || user;
    if (src) {
      try {
        const existingEducation = Array.isArray(src.education)
          ? src.education.map((edu, idx) => ({
              id: edu.id || `${Date.now()}-${idx}`,
              institution: edu.institution,
              institutionId: edu.institution_id || edu.institutionId || '',
              degree: edu.degree,
              fieldOfStudy: edu.field_of_study || edu.fieldOfStudy || '',
              startDate: edu.start_date || edu.startDate || '',
              endDate: edu.end_date || edu.endDate || '',
              current: !!edu.current
            }))
          : [];

        setFormData(prev => ({
          ...prev,
          firstName: src.first_name || src.firstName || prev.firstName,
          lastName: src.last_name || src.lastName || prev.lastName,
          education: existingEducation
        }));
      } catch (err) {
        console.warn('Failed to hydrate ProfileCompletion from initialUser:', err);
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [initialUser, user]);

  // Close dropdowns when clicking outside
  useEffect(() => {
    function handleClickOutside(event) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setShowSearchResults(false);
      }
      if (degreeRef.current && !degreeRef.current.contains(event.target)) {
        setShowDegreeDropdown(false);
      }
      if (courseRef.current && !courseRef.current.contains(event.target)) {
        setShowCourseDropdown(false);
      }
    }

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Input change handler
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  // Education field change handler
  const handleEducationChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      currentEducation: {
        ...prev.currentEducation,
        [name]: type === 'checkbox' ? checked : value
      }
    }));
  };

  const handleDegreeSelect = (degree) => {
    setFormData(prev => ({
      ...prev,
      currentEducation: {
        ...prev.currentEducation,
        degree: degree
      }
    }));
    setShowDegreeDropdown(false);
  };

  const handleCourseSelect = (course) => {
    setFormData(prev => ({
      ...prev,
      currentEducation: {
        ...prev.currentEducation,
        fieldOfStudy: course
      }
    }));
    setShowCourseDropdown(false);
  };

  // Search for institutions (debounced simple implementation)
  const searchInstitutions = async (query) => {
    try {
      const response = await organizationService.getInstitutions(query);
      if (response?.data?.success && Array.isArray(response.data.institutions)) {
        setFormData(prev => ({ ...prev, searchResults: response.data.institutions }));
        setShowSearchResults(true);
      } else {
        // No fallback mock data: show empty results and allow the UI to display "No matching institutions found"
        setFormData(prev => ({ ...prev, searchResults: [] }));
        setShowSearchResults(true);
      }
    } catch (err) {
      console.error('Error searching institutions:', err);
      setError('Failed to search institutions. Please try again.');
      setFormData(prev => ({ ...prev, searchResults: [] }));
      setShowSearchResults(true);
    }
  };

  const selectInstitution = (institution) => {
    setFormData(prev => ({
      ...prev,
      currentEducation: {
        ...prev.currentEducation,
        institution: institution.name,
        institutionId: institution.id
      },
      searchText: institution.name,
      searchResults: []
    }));
    setShowSearchResults(false);
  };

  const addEducation = () => {
    const { institution, degree, fieldOfStudy, startDate } = formData.currentEducation;
    if (!institution || !degree || !fieldOfStudy || !startDate) {
      setError('Please fill in all required education fields');
      return;
    }

    setFormData(prev => ({
      ...prev,
      education: [...prev.education, { ...prev.currentEducation, id: Date.now() }],
      currentEducation: {
        institution: '',
        institutionId: '',
        degree: '',
        fieldOfStudy: '',
        startDate: '',
        endDate: '',
        current: false
      }
    }));
    setError(null);
  };

  const removeEducation = (id) => {
    const prevEducation = formData.education;
    const newEducation = prevEducation.filter(edu => edu.id !== id);
    setFormData(prev => ({ ...prev, education: newEducation }));

    // Persist immediately
    (async () => {
      setLoading(true);
      setError(null);
      try {
        const payload = {
          first_name: formData.firstName,
          last_name: formData.lastName,
          education: newEducation.map(edu => ({
            institution: edu.institution,
            institution_id: edu.institutionId,
            degree: edu.degree,
            field_of_study: edu.fieldOfStudy,
            start_date: edu.startDate,
            end_date: edu.endDate,
            current: !!edu.current
          }))
        };

        const response = await api.put('/api/user/profile', payload);
        if (response?.data?.success) {
          try { updateUser({ ...user, ...response.data.user }); } catch (e) { /* ignore */ }
          setToast('Profile updated successfully');
          setTimeout(() => setToast(null), 3000);
        } else {
          throw new Error(response?.data?.message || 'Failed to save profile');
        }
      } catch (err) {
        console.error('Failed to persist education removal:', err);
        setError('Failed to remove education — changes were reverted.');
        setFormData(prev => ({ ...prev, education: prevEducation }));
      } finally {
        setLoading(false);
      }
    })();
  };

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const payload = {
        first_name: formData.firstName,
        last_name: formData.lastName,
        education: formData.education.map(edu => ({
          institution: edu.institution,
          institution_id: edu.institutionId,
          degree: edu.degree,
          field_of_study: edu.fieldOfStudy,
          start_date: edu.startDate,
          end_date: edu.endDate,
          current: !!edu.current
        }))
      };

      const response = await api.put('/api/user/profile', payload);

      if (response?.data?.success) {
        const savedUser = response.data.user || {};
        try { updateUser({ ...user, ...savedUser, profile_completed: true }); } catch (e) { /* ignore */ }

        const savedEducation = Array.isArray(savedUser.education)
          ? savedUser.education.map((edu, idx) => ({
              id: edu.id || `${Date.now()}-${idx}`,
              institution: edu.institution,
              institutionId: edu.institution_id || '',
              degree: edu.degree,
              fieldOfStudy: edu.field_of_study || edu.fieldOfStudy || '',
              startDate: edu.start_date || edu.startDate || '',
              endDate: edu.end_date || edu.endDate || '',
              current: !!edu.current
            }))
          : [];

        setFormData(prev => ({
          ...prev,
          firstName: savedUser.first_name || prev.firstName,
          lastName: savedUser.last_name || prev.lastName,
          education: savedEducation,
          currentEducation: {
            institution: '',
            institutionId: '',
            degree: '',
            fieldOfStudy: '',
            startDate: '',
            endDate: '',
            current: false
          }
        }));

        if (onComplete) onComplete();
        setToast('Profile updated successfully');
        setTimeout(() => setToast(null), 3500);
      } else {
        setError(response?.data?.message || 'Failed to save profile.');
      }
    } catch (err) {
      if (err.response?.data?.message) {
        setError(err.response.data.message);
      } else {
        console.error('Error updating profile:', err);
        setError('An error occurred while updating your profile. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <motion.div
      className="bg-white p-6 rounded-lg shadow-lg max-w-3xl mx-auto"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <h2 className="text-2xl font-bold text-gray-800 mb-6">Complete Your Profile</h2>

      {user?.truecred_id && (
        <div className="mb-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
          <h3 className="text-lg font-semibold text-blue-800">Your TrueCred ID</h3>
          <p className="text-2xl font-mono text-blue-600 mt-2">{user.truecred_id}</p>
          <p className="text-sm text-blue-700 mt-1">
            This is your unique identifier in the TrueCred system. Share this ID with organizations 
            that need to issue credentials to you.
          </p>
        </div>
      )}

      {error && (
        <div className="mb-6 p-4 bg-red-50 rounded-lg border border-red-200">
          <p className="text-red-700">{error}</p>
        </div>
      )}

      <form onSubmit={handleSubmit}>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          <div>
            <label className="block text-gray-700 mb-2" htmlFor="firstName">First Name</label>
            <input
              id="firstName"
              name="firstName"
              type="text"
              value={formData.firstName}
              onChange={handleInputChange}
              className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            />
          </div>

          <div>
            <label className="block text-gray-700 mb-2" htmlFor="lastName">Last Name</label>
            <input
              id="lastName"
              name="lastName"
              type="text"
              value={formData.lastName}
              onChange={handleInputChange}
              className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            />
          </div>
        </div>

        <div className="mb-6">
          <h3 className="text-xl font-semibold text-gray-800 mb-4">Education</h3>

          {formData.education.length > 0 && (
            <div className="mb-6">
              <h4 className="text-lg font-medium text-gray-700 mb-3">Added Education</h4>
              {formData.education.map(edu => (
                <div key={edu.id} className="bg-gray-50 p-4 rounded-lg mb-3 flex justify-between items-center">
                  <div>
                    <p className="font-medium">{edu.degree} in {edu.fieldOfStudy}</p>
                    <p className="text-gray-600">{edu.institution}</p>
                    <p className="text-sm text-gray-500">{edu.startDate} - {edu.current ? 'Present' : edu.endDate}</p>
                  </div>
                  <button type="button" onClick={() => setConfirmRemoveId(edu.id)} className="text-red-600 hover:text-red-800">Remove</button>
                </div>
              ))}
            </div>
          )}

          <div className="bg-gray-50 p-4 rounded-lg">
            <h4 className="text-lg font-medium text-gray-700 mb-3">Add Education</h4>

            <div className="mb-4 relative">
              <label className="block text-gray-700 mb-2" htmlFor="searchText">Institution <span className="text-xs text-blue-600">(click to see options)</span></label>
              <div className="relative">
                <input
                  id="searchText"
                  name="searchText"
                  type="text"
                  value={formData.searchText}
                  onChange={(e) => setFormData(prev => ({ ...prev, searchText: e.target.value }))}
                  onClick={() => { searchInstitutions(''); setShowSearchResults(true); }}
                  onFocus={() => { searchInstitutions(''); setShowSearchResults(true); }}
                  className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 pr-10"
                  placeholder="Search or select your institution..."
                />
                <button type="button" onClick={() => { searchInstitutions(''); setShowSearchResults(!showSearchResults); }} className="absolute inset-y-0 right-0 flex items-center pr-3">
                  <ChevronDown className="h-5 w-5 text-gray-400" />
                </button>
              </div>

              {showSearchResults && (
                <div ref={dropdownRef} className="absolute z-10 w-full mt-1 bg-white border rounded-lg shadow-lg max-h-60 overflow-y-auto">
                  {formData.searchResults.length > 0 ? (
                    formData.searchResults.map(institution => (
                      <div key={institution.id} className="p-3 hover:bg-gray-100 cursor-pointer border-b border-gray-100" onClick={() => selectInstitution(institution)}>{institution.name}</div>
                    ))
                  ) : (
                    <div className="p-3 text-gray-500 text-center">{formData.searchText ? "No matching institutions found" : "Loading institutions..."}</div>
                  )}
                </div>
              )}

              {formData.currentEducation.institution && (
                <div className="mt-2 p-2 bg-blue-50 rounded border border-blue-200"><p className="text-blue-800">Selected: {formData.currentEducation.institution}</p></div>
              )}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
              <div>
                <label className="block text-gray-700 mb-2" htmlFor="degree">Degree</label>
                <div ref={degreeRef} className="relative">
                  <div className="flex items-center w-full px-4 py-2 border rounded-lg cursor-pointer" onClick={() => setShowDegreeDropdown(!showDegreeDropdown)}>
                    <input id="degree" name="degree" type="text" value={formData.currentEducation.degree} onChange={handleEducationChange} className="flex-grow focus:outline-none cursor-pointer" placeholder="Select your degree" readOnly />
                    <ChevronDown size={20} className="text-gray-500" />
                  </div>

                  {showDegreeDropdown && (
                    <div className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-md shadow-lg max-h-60 overflow-auto">
                      {degreeOptions.map((degree, index) => (
                        <div key={index} className="p-2 hover:bg-gray-100 cursor-pointer" onClick={() => handleDegreeSelect(degree)}>{degree}</div>
                      ))}
                    </div>
                  )}
                </div>
              </div>

              <div>
                <label className="block text-gray-700 mb-2" htmlFor="fieldOfStudy">Field of Study</label>
                <div ref={courseRef} className="relative">
                  <div className="flex items-center w-full px-4 py-2 border rounded-lg cursor-pointer" onClick={() => setShowCourseDropdown(!showCourseDropdown)}>
                    <input id="fieldOfStudy" name="fieldOfStudy" type="text" value={formData.currentEducation.fieldOfStudy} onChange={handleEducationChange} className="flex-grow focus:outline-none cursor-pointer" placeholder="Select your field of study" readOnly />
                    <ChevronDown size={20} className="text-gray-500" />
                  </div>

                  {showCourseDropdown && (
                    <div className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-md shadow-lg max-h-60 overflow-auto">
                      {courseOptions.map((course, index) => (
                        <div key={index} className="p-2 hover:bg-gray-100 cursor-pointer" onClick={() => handleCourseSelect(course)}>{course}</div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
              <div>
                <label className="block text-gray-700 mb-2" htmlFor="startDate">Start Date</label>
                <input id="startDate" name="startDate" type="date" value={formData.currentEducation.startDate} onChange={handleEducationChange} className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" />
              </div>

              <div>
                <label className="block text-gray-700 mb-2" htmlFor="endDate">End Date</label>
                <input id="endDate" name="endDate" type="date" value={formData.currentEducation.endDate} onChange={handleEducationChange} className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" disabled={formData.currentEducation.current} />
              </div>
            </div>

            <div className="mb-4">
              <label className="flex items-center"><input type="checkbox" name="current" checked={formData.currentEducation.current} onChange={handleEducationChange} className="mr-2" />
                <span className="text-gray-700">I currently study here</span>
              </label>
            </div>

            <button type="button" onClick={addEducation} className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">Add Education</button>
          </div>
        </div>

        <div className="flex justify-end items-center space-x-4">
          {toast && (<div className="px-4 py-2 bg-green-100 text-green-800 rounded shadow-sm">{toast}</div>)}
          <button type="submit" disabled={loading || formData.education.length === 0} title={formData.education.length === 0 ? 'Add at least one education entry before completing your profile' : ''} className={`px-6 py-2 rounded-lg text-white ${loading || formData.education.length === 0 ? 'bg-gray-400 cursor-not-allowed' : 'bg-green-600 hover:bg-green-700'} transition-colors`}>{loading ? 'Saving...' : 'Complete Profile'}</button>
        </div>
      </form>

      {/* Confirm removal modal */}
      {confirmRemoveId && (
        <div className="fixed inset-0 flex items-center justify-center z-50">
          <div className="absolute inset-0 bg-black opacity-50"></div>
          <div className="bg-white rounded-lg p-6 z-60 max-w-md mx-4 shadow-lg">
            <h3 className="text-lg font-semibold mb-4">Confirm removal</h3>
            <p className="mb-6">Are you sure you want to remove this education entry? This action can be undone by re-adding the entry.</p>
            <div className="flex justify-end gap-3">
              <button onClick={() => setConfirmRemoveId(null)} className="px-4 py-2 rounded border">Cancel</button>
              <button onClick={() => { const id = confirmRemoveId; setConfirmRemoveId(null); removeEducation(id); }} className="px-4 py-2 rounded bg-red-600 text-white">Remove</button>
            </div>
          </div>
        </div>
      )}
    </motion.div>
  );
}
