import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { api } from '../services/api';
import { useNavigate } from 'react-router-dom';

const emptyEdu = {
  institution: '',
  degree: '',
  field_of_study: '',
  start_date: '',
  end_date: '',
  current: false
};

// Dropdown options
const degreeOptions = [
  'Bachelor of Science (BSc)',
  'Bachelor of Arts (BA)',
  'Bachelor of Engineering (BEng)',
  'Bachelor of Technology (BTech)',
  'Master of Science (MSc)',
  'Master of Arts (MA)',
  'Master of Engineering (MEng)',
  'Master of Technology (MTech)',
  'Doctor of Philosophy (PhD)',
  'Doctor of Science (DSc)',
  'Doctor of Engineering (DEng)',
  'Associate Degree',
  'Diploma',
  'Certificate',
  'Other'
];

const fieldOfStudyOptions = [
  'Computer Science',
  'Information Technology',
  'Software Engineering',
  'Data Science',
  'Artificial Intelligence',
  'Machine Learning',
  'Cybersecurity',
  'Electrical Engineering',
  'Mechanical Engineering',
  'Civil Engineering',
  'Chemical Engineering',
  'Biomedical Engineering',
  'Business Administration',
  'Finance',
  'Marketing',
  'Economics',
  'Mathematics',
  'Physics',
  'Chemistry',
  'Biology',
  'Psychology',
  'Sociology',
  'English Literature',
  'History',
  'Political Science',
  'Law',
  'Medicine',
  'Nursing',
  'Pharmacy',
  'Other'
];

const Profile = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [education, setEducation] = useState([ { ...emptyEdu } ]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [profileCompleted, setProfileCompleted] = useState(false);
  const [colleges, setColleges] = useState([]);
  const [collegesLoading, setCollegesLoading] = useState(true);
  const [customValues, setCustomValues] = useState({
    institution: '',
    degree: '',
    field_of_study: ''
  });

  useEffect(() => {
    // Fetch colleges for dropdown
    const fetchColleges = async () => {
      try {
        const response = await api.get('/api/user/all-colleges');
        if (response.data.success) {
          setColleges(response.data.colleges);
        }
      } catch (err) {
        console.error('Error fetching colleges:', err);
        // If API fails, use fallback options
        setColleges([
          { id: 'other', name: 'Other' }
        ]);
      } finally {
        setCollegesLoading(false);
      }
    };

    // Fetch profile data
    const fetchProfile = async () => {
      setIsLoading(true);
      try {
        const response = await api.get('/api/user/profile');
        const data = response.data;
        if (data.success && data.user) {
          setEducation(data.user.education && data.user.education.length > 0 ? data.user.education : [ { ...emptyEdu } ]);
          setProfileCompleted(!!data.user.profile_completed);
        }
      } catch (err) {
        console.error('Error fetching profile:', err);
        setError('Failed to fetch profile');
      }
      setIsLoading(false);
    };

    fetchColleges();
    fetchProfile();
  }, []);

  // Process education data after colleges are loaded
  useEffect(() => {
    if (!collegesLoading && education.length > 0) {
      const processedEducation = education.map(edu => {
        const processedEdu = { ...edu };
        
        // Check if institution is not in colleges list and not already 'Other'
        if (edu.institution && edu.institution !== 'Other' && !colleges.find(c => c.name === edu.institution)) {
          setCustomValues(prev => ({ ...prev, institution: edu.institution }));
          processedEdu.institution = 'Other';
        }
        
        // Check if degree is not in degree options and not already 'Other'
        if (edu.degree && edu.degree !== 'Other' && !degreeOptions.includes(edu.degree)) {
          setCustomValues(prev => ({ ...prev, degree: edu.degree }));
          processedEdu.degree = 'Other';
        }
        
        // Check if field_of_study is not in field options and not already 'Other'
        if (edu.field_of_study && edu.field_of_study !== 'Other' && !fieldOfStudyOptions.includes(edu.field_of_study)) {
          setCustomValues(prev => ({ ...prev, field_of_study: edu.field_of_study }));
          processedEdu.field_of_study = 'Other';
        }
        
        return processedEdu;
      });
      
      // Only update if there are changes
      const hasChanges = processedEducation.some((edu, idx) => 
        edu.institution !== education[idx].institution ||
        edu.degree !== education[idx].degree ||
        edu.field_of_study !== education[idx].field_of_study
      );
      
      if (hasChanges) {
        setEducation(processedEducation);
      }
    }
  }, [collegesLoading, colleges, education]);

  const handleEduChange = (idx, field, value) => {
    setEducation(prev => prev.map((e, i) => i === idx ? { ...e, [field]: value } : e));
    setError('');
    setSuccess('');
  };

  const handleCustomValueChange = (field, value) => {
    setCustomValues(prev => ({ ...prev, [field]: value }));
  };

  const getDisplayValue = (field, value) => {
    if (value === 'Other') {
      return customValues[field] || '';
    }
    return value;
  };

  const getActualValue = (field, value) => {
    if (value === 'Other') {
      return customValues[field] || 'Other';
    }
    return value;
  };

  const addEducation = () => {
    setEducation(prev => [ ...prev, { ...emptyEdu } ]);
  };

  const removeEducation = (idx) => {
    if (education.length > 1) {
      setEducation(prev => prev.filter((_, i) => i !== idx));
    }
  };

  const validateEdu = edu => {
    // Check institution
    if (!edu.institution || !edu.institution.trim()) return false;
    if (edu.institution === 'Other' && (!customValues.institution || !customValues.institution.trim())) return false;
    
    // Check degree
    if (!edu.degree || !edu.degree.trim()) return false;
    if (edu.degree === 'Other' && (!customValues.degree || !customValues.degree.trim())) return false;
    
    // Check field of study
    if (!edu.field_of_study || !edu.field_of_study.trim()) return false;
    if (edu.field_of_study === 'Other' && (!customValues.field_of_study || !customValues.field_of_study.trim())) return false;
    
    // Check start date
    if (!edu.start_date || !edu.start_date.trim()) return false;
    
    // Check end date if not current
    if (!edu.current && (!edu.end_date || !edu.end_date.trim())) return false;
    
    return true;
  };

  const handleSave = async () => {
    setIsLoading(true);
    setError('');
    setSuccess('');
    // Validate all education entries
    for (let i = 0; i < education.length; i++) {
      if (!validateEdu(education[i])) {
        setError(`Education entry ${i+1} is invalid. Please select from dropdown or provide custom values for Institution, Degree, and Field of Study. All fields except end date (if current) are required.`);
        setIsLoading(false);
        return;
      }
    }
    try {
      const response = await api.put('/api/user/profile', { education });
      const data = response.data;
      if (data.success) {
        setSuccess('Profile saved successfully!');
        setProfileCompleted(true);
      } else {
        setError(data.message || 'Failed to save profile');
      }
    } catch (err) {
      console.error('Error saving profile:', err);
      setError('Failed to save profile');
    }
    setIsLoading(false);
  };

  return (
    <div className="max-w-4xl mx-auto p-8 bg-white rounded-lg shadow-lg">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-3xl font-bold text-gray-800">Student Profile</h2>
        <button
          onClick={() => navigate('/student-dashboard')}
          className="bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-md font-medium transition-colors duration-200 flex items-center gap-2"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
          Back to Dashboard
        </button>
      </div>
      {profileCompleted && (
        <div className="inline-block bg-green-100 text-green-800 px-4 py-2 rounded-lg mb-4 font-medium">
          ✓ Profile Complete
        </div>
      )}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-4">
          {error}
        </div>
      )}
      {success && (
        <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg mb-4">
          {success}
        </div>
      )}
      
      <form onSubmit={e => { e.preventDefault(); handleSave(); }} className="space-y-6">
        {education.map((edu, idx) => (
          <div key={idx} className="bg-gray-50 p-6 rounded-lg border border-gray-200">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold text-gray-700">Education {idx + 1}</h3>
              {education.length > 1 && (
                <button 
                  type="button" 
                  onClick={() => removeEducation(idx)}
                  className="bg-red-500 hover:bg-red-600 text-white px-3 py-1 rounded-md text-sm font-medium transition-colors duration-200"
                >
                  Remove
                </button>
              )}
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Institution</label>
                <select 
                  value={edu.institution} 
                  onChange={e => handleEduChange(idx, 'institution', e.target.value)} 
                  className="w-full border border-gray-300 px-3 py-2 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white"
                  required
                  disabled={collegesLoading}
                >
                  <option value="">
                    {collegesLoading ? 'Loading colleges...' : 'Select Institution'}
                  </option>
                  {colleges.map(college => (
                    <option key={college.id} value={college.name}>
                      {college.name}
                    </option>
                  ))}
                  <option value="Other">Other</option>
                </select>
                {edu.institution === 'Other' && (
                  <input
                    type="text"
                    value={customValues.institution}
                    onChange={e => {
                      handleCustomValueChange('institution', e.target.value);
                      handleEduChange(idx, 'institution', e.target.value);
                    }}
                    placeholder="Enter institution name"
                    className="w-full mt-2 border border-gray-300 px-3 py-2 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    required
                  />
                )}
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Degree</label>
                <select 
                  value={edu.degree} 
                  onChange={e => handleEduChange(idx, 'degree', e.target.value)} 
                  className="w-full border border-gray-300 px-3 py-2 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white"
                  required
                >
                  <option value="">Select Degree</option>
                  {degreeOptions.filter(option => option !== 'Other').map(option => (
                    <option key={option} value={option}>{option}</option>
                  ))}
                  <option value="Other">Other</option>
                </select>
                {edu.degree === 'Other' && (
                  <input
                    type="text"
                    value={customValues.degree}
                    onChange={e => {
                      handleCustomValueChange('degree', e.target.value);
                      handleEduChange(idx, 'degree', e.target.value);
                    }}
                    placeholder="Enter degree name"
                    className="w-full mt-2 border border-gray-300 px-3 py-2 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    required
                  />
                )}
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Field of Study</label>
                <select 
                  value={edu.field_of_study} 
                  onChange={e => handleEduChange(idx, 'field_of_study', e.target.value)} 
                  className="w-full border border-gray-300 px-3 py-2 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white"
                  required
                >
                  <option value="">Select Field of Study</option>
                  {fieldOfStudyOptions.filter(option => option !== 'Other').map(option => (
                    <option key={option} value={option}>{option}</option>
                  ))}
                  <option value="Other">Other</option>
                </select>
                {edu.field_of_study === 'Other' && (
                  <input
                    type="text"
                    value={customValues.field_of_study}
                    onChange={e => {
                      handleCustomValueChange('field_of_study', e.target.value);
                      handleEduChange(idx, 'field_of_study', e.target.value);
                    }}
                    placeholder="Enter field of study"
                    className="w-full mt-2 border border-gray-300 px-3 py-2 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    required
                  />
                )}
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Start Date</label>
                <input 
                  type="date" 
                  value={edu.start_date} 
                  onChange={e => handleEduChange(idx, 'start_date', e.target.value)} 
                  className="w-full border border-gray-300 px-3 py-2 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  required 
                />
              </div>
              
              <div className="flex items-center space-x-2">
                <input 
                  type="checkbox" 
                  id={`current-${idx}`}
                  checked={edu.current} 
                  onChange={e => handleEduChange(idx, 'current', e.target.checked)} 
                  className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500"
                />
                <label htmlFor={`current-${idx}`} className="text-sm font-medium text-gray-700">
                  Currently studying here
                </label>
              </div>
              
              {!edu.current && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">End Date</label>
                  <input 
                    type="date" 
                    value={edu.end_date} 
                    onChange={e => handleEduChange(idx, 'end_date', e.target.value)} 
                    className="w-full border border-gray-300 px-3 py-2 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    required 
                  />
                </div>
              )}
            </div>
          </div>
        ))}
        
        <div className="flex flex-col sm:flex-row gap-4 pt-4">
          <button 
            type="button" 
            onClick={addEducation}
            className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-md font-medium transition-colors duration-200"
          >
            + Add Education
          </button>
          <button 
            type="submit" 
            className="bg-green-600 hover:bg-green-700 text-white px-6 py-2 rounded-md font-medium transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
            disabled={isLoading}
          >
            {isLoading ? 'Saving...' : 'Save Profile'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default Profile;
