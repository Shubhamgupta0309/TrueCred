import React, { useState, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import { Upload, PlusCircle, Check, AlertCircle, X, Building, School, Briefcase, ChevronDown } from 'lucide-react';
import axios from 'axios';
import { api, organizationService } from '../../services/api';
import { isAuthenticated } from '../../utils/tokenUtils';

export default function ActionButtons({ onAuthError, onSuccess }) {
  const [uploading, setUploading] = useState(false);
  const [uploadingExp, setUploadingExp] = useState(false);
  const [uploadStatus, setUploadStatus] = useState(null); // 'success', 'error', or null
  const [expUploadStatus, setExpUploadStatus] = useState(null); // 'success', 'error', or null
  const [statusMessage, setStatusMessage] = useState('');
  const [expStatusMessage, setExpStatusMessage] = useState('');
  const fileInputRef = useRef(null);
  const expFileInputRef = useRef(null);
  const companyDropdownRef = useRef(null);
  const collegeDropdownRef = useRef(null);
  const [showCredModal, setShowCredModal] = useState(false);
  const [showExpModal, setShowExpModal] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [selectedExpFile, setSelectedExpFile] = useState(null);
  const [companies, setCompanies] = useState([]);
  const [colleges, setColleges] = useState([]);
  const [loadingCompanies, setLoadingCompanies] = useState(false);
  const [loadingColleges, setLoadingColleges] = useState(false);
  const [companySearchText, setCompanySearchText] = useState('');
  const [collegeSearchText, setCollegeSearchText] = useState(null); // Initialize as null to control dropdown visibility
  const [showDegreeDropdown, setShowDegreeDropdown] = useState(false);
  const degreeRef = useRef(null);
  
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
  
  const [credentialInfo, setCredentialInfo] = useState({
    institution: '',
    institutionType: 'college', // 'college' or 'company'
    title: '', // Custom title like "UI Test, Exam Form"
    credentialName: '', // Degree name like "Bachelor of Engineering (B.E.)"
    issuedDate: '',
    institution_id: '' // Add institution_id to store the database ID
  });
  const [experienceInfo, setExperienceInfo] = useState({
    company: '',
    company_id: '', // Add company_id to store the database ID
    position: '',
    startDate: '',
    endDate: '',
    isCurrent: false
  });

  // Check auth before any action
  const checkAuthBeforeAction = () => {
    if (!isAuthenticated()) {
      // Call the onAuthError callback if provided
      if (onAuthError) {
        onAuthError({ response: { status: 401 } });
      }
      return false;
    }
    return true;
  };
  
  // Fetch companies when the experience modal is shown
  useEffect(() => {
    if (showExpModal) {
      fetchCompanies();
    }
  }, [showExpModal]);
  
  // Fetch colleges when the credential modal is shown
  useEffect(() => {
    if (showCredModal) {
      fetchColleges();
    }
  }, [showCredModal]);
  
  // Handle clicks outside the company dropdown
  useEffect(() => {
    function handleClickOutside(event) {
      if (companyDropdownRef.current && !companyDropdownRef.current.contains(event.target)) {
        setCompanySearchText('');
      }
      if (collegeDropdownRef.current && !collegeDropdownRef.current.contains(event.target) && 
          !event.target.name === 'institution') { // Don't close dropdown when clicking on the input itself
        setCollegeSearchText(null); // Set to null to hide the dropdown
      }
      if (degreeRef.current && !degreeRef.current.contains(event.target)) {
        setShowDegreeDropdown(false);
      }
    }
    
    // Add event listener
    document.addEventListener("mousedown", handleClickOutside);
    
    // Clean up
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, []);
  
  // Function to fetch companies from backend
  const fetchCompanies = async () => {
    if (!checkAuthBeforeAction()) return;
    
    setLoadingCompanies(true);
    try {
      // Call the companies endpoint
      const response = await api.get('/api/organizations/companies');
      if (response.data.success && response.data.companies) {
        setCompanies(response.data.companies);
      } else {
        // Fallback to mock data if response format is unexpected
        throw new Error('Unexpected response format');
      }
    } catch (error) {
      console.error('Error fetching companies:', error);
      // Leave companies empty on error; do not fallback to mock data
      setCompanies([]);
    } finally {
      setLoadingCompanies(false);
    }
  };
  
  // Function to fetch colleges from backend
  const fetchColleges = async (searchQuery = '') => {
    if (!checkAuthBeforeAction()) return;
    
    setLoadingColleges(true);
    try {
      console.log('Fetching colleges for dropdown with query:', searchQuery);
      // Call the institutions endpoint using organization service
      const response = await organizationService.getInstitutions(searchQuery);
      console.log('College response:', response.data);
      
      if (response.data.success && response.data.institutions) {
        // Sort institutions alphabetically by fullName or name
        const sortedInstitutions = response.data.institutions.sort((a, b) => {
          const nameA = (a.fullName || a.name).toLowerCase();
          const nameB = (b.fullName || b.name).toLowerCase();
          return nameA.localeCompare(nameB);
        });
        setColleges(sortedInstitutions);
      } else {
        // Fallback to mock data if response format is unexpected
        throw new Error('Unexpected response format');
      }
    } catch (error) {
      console.error('Error fetching colleges:', error);
      // Leave colleges empty on error; do not fallback to mock data
      setColleges([]);
    } finally {
      setLoadingColleges(false);
    }
  };
  
  // Function to handle company selection from dropdown
  const handleCompanySelect = (company) => {
    setExperienceInfo(prev => ({ 
      ...prev, 
      company: company.name,
      company_id: company.id
    }));
    setCompanySearchText('');
  };
  
  // Function to handle college selection from dropdown
  const handleCollegeSelect = (college) => {
    setCredentialInfo(prev => ({ 
      ...prev, 
      institution: college.fullName || college.name,
      institution_id: college.id
    }));
    setCollegeSearchText('');
  };

  const handleFileSelect = (event) => {
    // Check authentication first
    if (!checkAuthBeforeAction()) return;
    
    const file = event.target.files[0];
    if (!file) return;

    // Check if file is a PDF
    if (file.type !== 'application/pdf') {
      setUploadStatus('error');
      setStatusMessage('Only PDF files are allowed.');
      return;
    }

    // Check file size (limit to 5MB)
    if (file.size > 5 * 1024 * 1024) {
      setUploadStatus('error');
      setStatusMessage('File size exceeds 5MB limit.');
      return;
    }

    setSelectedFile(file);
    setShowCredModal(true);
    
    // Make sure colleges are loaded for the dropdown
    fetchColleges();
  };

  const handleExpFileSelect = (event) => {
    // Check authentication first
    if (!checkAuthBeforeAction()) return;
    
    const file = event.target.files[0];
    if (!file) return;

    // Check if file is a PDF
    if (file.type !== 'application/pdf') {
      setExpUploadStatus('error');
      setExpStatusMessage('Only PDF files are allowed.');
      return;
    }

    // Check file size (limit to 5MB)
    if (file.size > 5 * 1024 * 1024) {
      setExpUploadStatus('error');
      setExpStatusMessage('File size exceeds 5MB limit.');
      return;
    }

    setSelectedExpFile(file);
    setShowExpModal(true);
  };

  // Update college search text and filter institutions
  const handleCredentialInfoChange = (e) => {
    const { name, value } = e.target;
    
    // If changing institution, also update the search text
    if (name === 'institution') {
      setCollegeSearchText(value);
      // Fetch institutions with the search query
      fetchColleges(value);
    }
    
    setCredentialInfo(prev => ({ ...prev, [name]: value }));
  };
  
  // Handler for selecting a degree from dropdown
  const handleDegreeSelect = (degree) => {
    setCredentialInfo(prev => ({ 
      ...prev, 
      credentialName: degree 
    }));
    setShowDegreeDropdown(false);
  };

  const handleExperienceInfoChange = (e) => {
    const { name, value, type, checked } = e.target;
    
    // If changing company, also update the search text
    if (name === 'company') {
      setCompanySearchText(value);
    }
    
    setExperienceInfo(prev => ({ 
      ...prev, 
      [name]: type === 'checkbox' ? checked : value 
    }));
  };

  const uploadCredential = async () => {
    // Check authentication first
    if (!checkAuthBeforeAction()) return;
    
    if (!selectedFile || !credentialInfo.institution || !credentialInfo.title) return;

    setUploading(true);
    setUploadStatus(null);
    setShowCredModal(false);

    // Create form data
    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('filename', selectedFile.name);
    formData.append('metadata', JSON.stringify({
      type: 'credential',
      uploadedAt: new Date().toISOString(),
      description: 'Credential document upload',
      institution: credentialInfo.institution,
      institutionType: credentialInfo.institutionType,
      title: credentialInfo.title, // Custom title
      credentialName: credentialInfo.credentialName, // Degree name
      issuedDate: credentialInfo.issuedDate,
      institution_id: credentialInfo.institution_id || null // Include institution ID
    }));

    try {
      // Use the enhanced api instance with token refresh to upload to IPFS
      const response = await api.post('/api/ipfs/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });

      console.log('Upload successful:', response.data);
      // Build a credential request payload referencing the uploaded IPFS uri
      // Backend may return different shapes; normalize common keys:
      // - result from api_response: { data: { ... } }
      // - services.ipfs_service.store_document returns { document_hash, document_gateway_url, metadata_hash }
      const respData = response.data.data || response.data || {};
      const ipfsUri = respData.document_gateway_url || respData.document_url || respData.ipfs_uri || respData.document_hash || respData.Hash || respData.hash || null;
      // If we received just a raw hash (document_hash), convert to gateway URL when possible
      let attachmentUri = null;
      if (ipfsUri) {
        // If it's a bare hash (no scheme and not a url), convert to gateway URL using configured gateway (frontend can't know it reliably),
        // but the backend often includes a full gateway URL in document_gateway_url. We prefer gateway URL when present.
        attachmentUri = ipfsUri;
      }
      const requestPayload = {
        title: credentialInfo.title || `Credential from ${credentialInfo.institution}`,
        issuer: credentialInfo.institution,
        type: 'credential',
        issue_date: credentialInfo.issuedDate || null,
        metadata: {
          institution_id: credentialInfo.institution_id || null,
          institutionType: credentialInfo.institutionType,
          credentialName: credentialInfo.credentialName, // Keep degree name in metadata
          uploadedAt: new Date().toISOString(),
          source: 'student_request',
        },
        attachments: attachmentUri ? [{ uri: attachmentUri, filename: selectedFile.name, verified: false }] : []
      };

      // Call the credential request API (creates a pending request)
      const reqResp = await api.post('/api/credentials/request', requestPayload);
      console.log('Credential request response:', reqResp.data);

      setUploadStatus('success');
      setStatusMessage(reqResp.data.message || `Credential request submitted to ${credentialInfo.institution}.`);
      // Notify parent to refresh dashboard data
      if (onSuccess && typeof onSuccess === 'function') {
        try { onSuccess(); } catch (e) { console.warn('onSuccess callback failed', e); }
      }
    } catch (error) {
      console.error('Error uploading file:', error);
      
      // Check if it's an auth error
      if (error.response?.status === 401) {
        if (onAuthError) {
          onAuthError(error);
        }
        setUploadStatus('error');
        setStatusMessage('Authentication required. Please log in and try again.');
      } else {
        setUploadStatus('error');
        setStatusMessage(error.response?.data?.message || 'Failed to submit credential request. Please try again.');
      }
    } finally {
      setUploading(false);
      // Reset the file input and form
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
      setSelectedFile(null);
      setCredentialInfo({
        institution: '',
        institutionType: 'college',
        title: '',
        credentialName: '',
        issuedDate: '',
        institution_id: ''
      });
    }
  };

  const uploadExperience = async () => {
    // Check authentication first
    if (!checkAuthBeforeAction()) return;
    
    if (!selectedExpFile || !experienceInfo.company) return;

    setUploadingExp(true);
    setExpUploadStatus(null);
    setShowExpModal(false);

    // Create form data
    const formData = new FormData();
    formData.append('file', selectedExpFile);
    formData.append('filename', selectedExpFile.name);
    formData.append('metadata', JSON.stringify({
      type: 'experience',
      uploadedAt: new Date().toISOString(),
      description: 'Experience document upload',
      company: experienceInfo.company,
      company_id: experienceInfo.company_id || null, // Include company ID
      position: experienceInfo.position,
      startDate: experienceInfo.startDate,
      endDate: experienceInfo.isCurrent ? 'Present' : experienceInfo.endDate,
      isCurrent: experienceInfo.isCurrent
    }));

    try {
      // Use the enhanced api instance with token refresh to upload to IPFS
      const response = await api.post('/api/ipfs/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });

      console.log('Upload successful:', response.data);
      const ipfsUri = response.data.ipfs_uri || response.data.data?.ipfs_uri || response.data.data?.document_url || null;
      const experienceRequest = {
        title: experienceInfo.position || `Experience at ${experienceInfo.company}`,
        company: experienceInfo.company,
        duration: experienceInfo.isCurrent ? `${experienceInfo.startDate} - Present` : `${experienceInfo.startDate} - ${experienceInfo.endDate}`,
        metadata: {
          company_id: experienceInfo.company_id || null,
          uploadedAt: new Date().toISOString(),
          source: 'student_request'
        },
        attachments: ipfsUri ? [{ uri: ipfsUri, filename: selectedExpFile.name, verified: false }] : []
      };

      const reqResp = await api.post('/api/experiences/request', experienceRequest);
      console.log('Experience request response:', reqResp.data);
      setExpUploadStatus('success');
      setExpStatusMessage(reqResp.data.message || `Experience request submitted to ${experienceInfo.company}.`);
    } catch (error) {
      console.error('Error uploading file:', error);
      
      // Check if it's an auth error
      if (error.response?.status === 401) {
        if (onAuthError) {
          onAuthError(error);
        }
        setExpUploadStatus('error');
        setExpStatusMessage('Authentication required. Please log in and try again.');
      } else {
  setExpUploadStatus('error');
  setExpStatusMessage(error.response?.data?.message || 'Failed to submit experience request. Please try again.');
      }
    } finally {
      setUploadingExp(false);
      // Reset the file input and form
      if (expFileInputRef.current) {
        expFileInputRef.current.value = '';
      }
      setSelectedExpFile(null);
      setExperienceInfo({
        company: '',
        position: '',
        startDate: '',
        endDate: '',
        isCurrent: false,
        company_id: ''
      });
    }
  };

  const triggerFileInput = () => {
    // Check authentication first
    if (!checkAuthBeforeAction()) return;
    
    // First, fetch colleges
    fetchColleges();
    
    // Then open file dialog
    fileInputRef.current?.click();
  };

  const triggerExpFileInput = () => {
    expFileInputRef.current?.click();
  };

  const closeCredModal = () => {
    setShowCredModal(false);
    setSelectedFile(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const closeExpModal = () => {
    setShowExpModal(false);
    setSelectedExpFile(null);
    if (expFileInputRef.current) {
      expFileInputRef.current.value = '';
    }
  };

  return (
    <div className="bg-white rounded-2xl shadow-lg shadow-purple-500/10 p-6 h-full flex flex-col justify-center">
      <h3 className="text-lg font-bold text-gray-800 mb-4">Quick Actions</h3>
      <div className="space-y-4">
        <input 
          type="file" 
          ref={fileInputRef}
          className="hidden" 
          accept=".pdf" 
          onChange={handleFileSelect} 
        />
        <motion.button
          whileHover={{ scale: 1.03 }}
          whileTap={{ scale: 0.97 }}
          onClick={triggerFileInput}
          disabled={uploading}
          className="w-full flex items-center justify-center gap-3 px-4 py-3 bg-gradient-to-r from-purple-600 to-purple-700 text-white rounded-lg font-semibold hover:from-purple-700 hover:to-purple-800 focus:ring-4 focus:ring-purple-300 focus:outline-none transition-all duration-200 shadow-lg hover:shadow-purple-500/30 disabled:opacity-70 disabled:cursor-not-allowed"
        >
          {uploading ? (
            <div className="animate-spin rounded-full h-5 w-5 border-t-2 border-b-2 border-white"></div>
          ) : (
            <Upload className="w-5 h-5" />
          )}
          <span>{uploading ? 'Uploading...' : 'Upload New Credential'}</span>
        </motion.button>
        
        {uploadStatus && (
          <div className={`p-3 rounded-lg flex items-center gap-2 text-sm ${
            uploadStatus === 'success' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
          }`}>
            {uploadStatus === 'success' ? <Check size={16} /> : <AlertCircle size={16} />}
            <span>{statusMessage}</span>
          </div>
        )}
        
        <input 
          type="file" 
          ref={expFileInputRef}
          className="hidden" 
          accept=".pdf" 
          onChange={handleExpFileSelect} 
        />
        <motion.button
          whileHover={{ scale: 1.03 }}
          whileTap={{ scale: 0.97 }}
          onClick={triggerExpFileInput}
          disabled={uploadingExp}
          className="w-full flex items-center justify-center gap-3 px-4 py-3 bg-gradient-to-r from-indigo-500 to-blue-500 text-white rounded-lg font-semibold hover:from-indigo-600 hover:to-blue-600 focus:ring-4 focus:ring-indigo-300 focus:outline-none transition-all duration-200 shadow-lg hover:shadow-indigo-500/30 disabled:opacity-70 disabled:cursor-not-allowed"
        >
          {uploadingExp ? (
            <div className="animate-spin rounded-full h-5 w-5 border-t-2 border-b-2 border-white"></div>
          ) : (
            <PlusCircle className="w-5 h-5" />
          )}
          <span>{uploadingExp ? 'Uploading...' : 'Add New Experience'}</span>
        </motion.button>

        {expUploadStatus && (
          <div className={`p-3 rounded-lg flex items-center gap-2 text-sm ${
            expUploadStatus === 'success' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
          }`}>
            {expUploadStatus === 'success' ? <Check size={16} /> : <AlertCircle size={16} />}
            <span>{expStatusMessage}</span>
          </div>
        )}
      </div>

      {/* Credential Modal */}
      {showCredModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl w-full max-w-md">
            <div className="flex justify-between items-center p-4 border-b">
              <h3 className="text-lg font-semibold text-gray-800">Credential Details</h3>
              <button 
                onClick={closeCredModal}
                className="text-gray-500 hover:text-gray-700"
              >
                <X size={20} />
              </button>
            </div>
            <div className="p-4">
              <div className="space-y-4">
                <div className="space-y-2">
                  <div className="flex gap-2 mb-4">
                    <button
                      type="button"
                      className={`flex-1 flex items-center justify-center gap-2 p-3 rounded-lg border ${
                        credentialInfo.institutionType === 'college' 
                          ? 'bg-purple-100 border-purple-500 text-purple-700' 
                          : 'bg-white border-gray-300 text-gray-700'
                      }`}
                      onClick={() => setCredentialInfo(prev => ({ ...prev, institutionType: 'college' }))}
                    >
                      <School size={20} />
                      <span>College/University</span>
                    </button>
                    <button
                      type="button"
                      className={`flex-1 flex items-center justify-center gap-2 p-3 rounded-lg border ${
                        credentialInfo.institutionType === 'company' 
                          ? 'bg-blue-100 border-blue-500 text-blue-700' 
                          : 'bg-white border-gray-300 text-gray-700'
                      }`}
                      onClick={() => setCredentialInfo(prev => ({ ...prev, institutionType: 'company' }))}
                    >
                      <Building size={20} />
                      <span>Company/Organization</span>
                    </button>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      {credentialInfo.institutionType === 'college' ? 'College/University Name' : 'Company/Organization Name'} 
                      <span className="text-xs text-purple-600 ml-1">(click to see options)</span>
                    </label>
                    <div className="relative">
                      <div className="flex items-center relative">
                        <input
                          type="text"
                          name="institution"
                          value={collegeSearchText || credentialInfo.institution}
                          onChange={handleCredentialInfoChange}
                          onClick={() => {
                            // Fetch institutions when clicked
                            fetchColleges();
                            // Show dropdown on click regardless of whether there's text
                            setCollegeSearchText(''); // Set to empty string to show dropdown
                          }}
                          placeholder={credentialInfo.institutionType === 'college' ? 'Search or select your institution...' : 'Search or select your organization...'}
                          className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                          required
                        />
                        <button
                          type="button"
                          onClick={() => {
                            fetchColleges();
                            setCollegeSearchText('');
                          }}
                          className="absolute right-2 text-gray-400 hover:text-purple-500"
                        >
                          <ChevronDown size={18} />
                        </button>
                      </div>
                      
                      {/* Dropdown for colleges/institutions - Show on click or when typing */}
                      {/* Always show dropdown when collegeSearchText has a value (including empty string) */}
                      {collegeSearchText !== null && (
                        <div 
                          ref={collegeDropdownRef}
                          className="absolute z-10 mt-1 w-full bg-white border border-gray-300 rounded-md shadow-lg max-h-60 overflow-auto"
                        >
                          {loadingColleges ? (
                            <div className="p-2 text-center text-gray-500">Loading institutions...</div>
                          ) : (
                            <>
                              {(credentialInfo.institutionType === 'college' ? colleges : companies)
                                .filter(item => 
                                  !collegeSearchText || collegeSearchText.trim() === '' || 
                                  (item.fullName || item.name).toLowerCase().includes(collegeSearchText.toLowerCase())
                                )
                                .map(item => (
                                  <div 
                                    key={item.id}
                                    className="p-2 hover:bg-gray-100 cursor-pointer"
                                    onClick={() => {
                                      if (credentialInfo.institutionType === 'college') {
                                        handleCollegeSelect(item);
                                      } else {
                                        handleCollegeSelect(item); // Reusing the same function for both types
                                      }
                                    }}
                                  >
                                    {item.fullName || item.name}
                                  </div>
                                ))
                              }
                              {(credentialInfo.institutionType === 'college' ? colleges : companies).filter(item => 
                                !collegeSearchText || collegeSearchText.trim() === '' || 
                                (item.fullName || item.name).toLowerCase().includes(collegeSearchText.toLowerCase())
                              ).length === 0 && (
                                <div className="p-2 text-center text-gray-500">
                                  No matches found. Your entry will be used.
                                </div>
                              )}
                            </>
                          )}
                        </div>
                      )}
                    </div>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Title <span className="text-xs text-purple-600 ml-1">(required, e.g. UI Test, Exam Form)</span>
                    </label>
                    <input
                      type="text"
                      name="title"
                      value={credentialInfo.title || ''}
                      onChange={handleCredentialInfoChange}
                      placeholder="Enter credential title, e.g. UI Test, Exam Form, Degree Name"
                      className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                      required
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Degree/Credential Name
                    </label>
                    <div ref={degreeRef} className="relative">
                      <div 
                        className="flex items-center w-full p-2 border border-gray-300 rounded-md cursor-pointer"
                        onClick={() => setShowDegreeDropdown(!showDegreeDropdown)}
                      >
                        <input
                          type="text"
                          name="credentialName"
                          value={credentialInfo.credentialName}
                          onChange={handleCredentialInfoChange}
                          placeholder="Select or enter your degree/credential"
                          className="flex-grow focus:outline-none focus:ring-2 focus:ring-purple-500 border-none"
                          readOnly={showDegreeDropdown}
                        />
                        <ChevronDown size={18} className="text-gray-400" />
                      </div>
                      
                      {showDegreeDropdown && (
                        <div className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-md shadow-lg max-h-60 overflow-auto">
                          {degreeOptions.map((degree, index) => (
                            <div
                              key={index}
                              className="p-2 hover:bg-gray-100 cursor-pointer"
                              onClick={() => handleDegreeSelect(degree)}
                            >
                              {degree}
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Date Issued
                    </label>
                    <input
                      type="date"
                      name="issuedDate"
                      value={credentialInfo.issuedDate}
                      onChange={handleCredentialInfoChange}
                      className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                    />
                  </div>
                </div>

                <div className="text-sm text-gray-600">
                  <p>Selected file: <span className="font-medium">{selectedFile?.name}</span></p>
                  <p className="mt-1">The credential will be sent to {credentialInfo.institution} for verification.</p>
                </div>
              </div>
            </div>
            <div className="flex justify-end gap-2 p-4 border-t">
              <button
                onClick={closeCredModal}
                className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={uploadCredential}
                disabled={!credentialInfo.institution || !credentialInfo.title}
                className="px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Upload Credential
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Experience Modal */}
      {showExpModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl w-full max-w-md">
            <div className="flex justify-between items-center p-4 border-b">
              <h3 className="text-lg font-semibold text-gray-800">Experience Details</h3>
              <button 
                onClick={closeExpModal}
                className="text-gray-500 hover:text-gray-700"
              >
                <X size={20} />
              </button>
            </div>
            <div className="p-4">
              <div className="space-y-4">
                <div className="space-y-2">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Company Name
                    </label>
                    <div className="relative">
                      <input
                        type="text"
                        name="company"
                        value={companySearchText || experienceInfo.company}
                        onChange={(e) => {
                          setCompanySearchText(e.target.value);
                          handleExperienceInfoChange(e);
                        }}
                        placeholder="e.g., Google Inc."
                        className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                        required
                      />
                      
                      {/* Dropdown for companies */}
                      {companySearchText && (
                        <div 
                          ref={companyDropdownRef}
                          className="absolute z-10 mt-1 w-full bg-white border border-gray-300 rounded-md shadow-lg max-h-60 overflow-auto"
                        >
                          {loadingCompanies ? (
                            <div className="p-2 text-center text-gray-500">Loading companies...</div>
                          ) : (
                            <>
                              {companies
                                .filter(company => 
                                  company.name.toLowerCase().includes(companySearchText.toLowerCase())
                                )
                                .map(company => (
                                  <div 
                                    key={company.id}
                                    className="p-2 hover:bg-gray-100 cursor-pointer"
                                    onClick={() => {
                                      handleCompanySelect(company);
                                    }}
                                  >
                                    {company.name}
                                  </div>
                                ))
                              }
                              {companies.filter(company => 
                                company.name.toLowerCase().includes(companySearchText.toLowerCase())
                              ).length === 0 && (
                                <div className="p-2 text-center text-gray-500">
                                  No companies found. Your entry will be used.
                                </div>
                              )}
                            </>
                          )}
                        </div>
                      )}
                    </div>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Position/Role
                    </label>
                    <input
                      type="text"
                      name="position"
                      value={experienceInfo.position}
                      onChange={handleExperienceInfoChange}
                      placeholder="e.g., Software Engineer"
                      className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Start Date
                    </label>
                    <input
                      type="date"
                      name="startDate"
                      value={experienceInfo.startDate}
                      onChange={handleExperienceInfoChange}
                      className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    />
                  </div>
                  
                  <div className="flex items-center mb-2">
                    <input
                      type="checkbox"
                      id="isCurrent"
                      name="isCurrent"
                      checked={experienceInfo.isCurrent}
                      onChange={handleExperienceInfoChange}
                      className="h-4 w-4 text-indigo-600 focus:ring-indigo-500"
                    />
                    <label htmlFor="isCurrent" className="ml-2 text-sm text-gray-700">
                      I currently work here
                    </label>
                  </div>
                  
                  {!experienceInfo.isCurrent && (
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        End Date
                      </label>
                      <input
                        type="date"
                        name="endDate"
                        value={experienceInfo.endDate}
                        onChange={handleExperienceInfoChange}
                        className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                      />
                    </div>
                  )}
                </div>

                <div className="text-sm text-gray-600">
                  <p>Selected file: <span className="font-medium">{selectedExpFile?.name}</span></p>
                  <p className="mt-1">The experience will be sent to {experienceInfo.company} for verification.</p>
                </div>
              </div>
            </div>
            <div className="flex justify-end gap-2 p-4 border-t">
              <button
                onClick={closeExpModal}
                className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={uploadExperience}
                disabled={!experienceInfo.company}
                className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Upload Experience
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}