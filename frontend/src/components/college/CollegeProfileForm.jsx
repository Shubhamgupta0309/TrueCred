import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Save, Building, Map, Phone, Mail, Globe, AlertCircle, CheckCircle } from 'lucide-react';
import { api, collegeService } from '../../services/api';

const CollegeProfileForm = ({ user, onUpdate }) => {
  const [formData, setFormData] = useState({
    name: '',
    fullName: '',
    address: '',
    city: '',
    state: '',
    country: '',
    postalCode: '',
    website: '',
    phone: '',
    email: '',
    accreditationBody: '',
    establishmentYear: '',
    description: ''
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  const [isEditing, setIsEditing] = useState(false);

  // Load existing data if available
  useEffect(() => {
    const fetchCollegeProfile = async () => {
      try {
        console.log('Fetching college profile data...');
        const response = await collegeService.getProfile();
        console.log('College profile response:', response.data);
        
        if (response.data && response.data.success) {
          // Check if the profile exists
          if (response.data.data.exists === false) {
            // Profile doesn't exist yet
            setIsEditing(true); // Enable editing mode to create a new profile
            setSuccess(false);
            setError('No college profile found. Please create one.');
            return;
          }
          
          // Profile exists, populate the form
          setFormData(prevData => ({
            ...prevData,
            ...response.data.data
          }));
        }
      } catch (err) {
        console.error('Error fetching college profile:', err);
        // Enable editing mode if there was an error
        setIsEditing(true);
        setError('Unable to fetch profile data. Please create a new one.');
      }
    };

    fetchCollegeProfile();
  }, []);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(false);

    try {
      // Make sure name field is provided
      if (!formData.name || formData.name.trim() === '') {
        setError('College name is required');
        setLoading(false);
        return;
      }

      console.log('Submitting college profile data:', formData);
      
      // Set default values for required fields if they're empty
      const submissionData = {
        ...formData,
        name: formData.name.trim()
      };
      
      const response = await collegeService.updateProfile(submissionData);
      console.log('College profile update response:', response.data);
      
      if (response.data && response.data.success) {
        setSuccess(true);
        setIsEditing(false);
        if (onUpdate) {
          onUpdate(formData);
        }
      } else {
        setError(response.data?.message || 'Failed to update college profile');
      }
    } catch (err) {
      console.error('Error updating college profile:', err);
      
      // More detailed error handling
      if (err.response) {
        // The request was made and the server responded with a status code
        // that falls out of the range of 2xx
        setError(`Error ${err.response.status}: ${err.response.data?.message || 'Failed to update profile'}`);
      } else if (err.request) {
        // The request was made but no response was received
        setError('No response received from server. Please check your network connection.');
      } else {
        // Something happened in setting up the request that triggered an Error
        setError('An error occurred while updating your profile. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-cyan-950/30 border border-cyan-500/30 rounded-2xl shadow-lg shadow-cyan-500/10 p-6"
    >
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center">
          <Building className="h-6 w-6 text-cyan-400 mr-2" />
          <h2 className="text-xl font-bold text-cyan-100">College Information</h2>
        </div>
        
        {!isEditing && (
          <div className="flex gap-4">
            <button
              type="button"
              data-profile-edit
              onClick={() => setIsEditing(true)}
              className="px-4 py-2 bg-cyan-900/40 text-cyan-200 rounded-lg hover:bg-cyan-900/60 transition-colors"
            >
              Edit Details
            </button>
            <button
              type="button"
              onClick={async () => {
                setLoading(true);
                try {
                  const testProfile = { ...formData, name: formData.name || 'Test College' };
                  console.log('Testing profile update with data:', testProfile);
                  const response = await api.post('/college/profile', testProfile);
                  console.log('Test profile update response:', response.data);
                  alert('Profile update test succeeded!');
                } catch (err) {
                  console.error('Test profile update failed:', err);
                  alert(`Test failed: ${err.message || 'Unknown error'}`);
                } finally {
                  setLoading(false);
                }
              }}
              className="px-4 py-2 bg-cyan-900/40 text-cyan-200 rounded-lg hover:bg-cyan-900/60 transition-colors"
            >
              Test Update
            </button>
          </div>
        )}
      </div>

      {error && (
        <div className="mb-6 p-4 bg-cyan-950/30 rounded-lg border border-cyan-500/30 flex items-center">
          <AlertCircle className="h-5 w-5 text-red-500 mr-2" />
          <p className="text-cyan-100">{error}</p>
        </div>
      )}

      {success && (
        <div className="mb-6 p-4 bg-cyan-950/30 rounded-lg border border-cyan-500/30 flex items-center">
          <CheckCircle className="h-5 w-5 text-green-500 mr-2" />
          <p className="text-cyan-100">College profile updated successfully!</p>
        </div>
      )}

      {!isEditing && !loading ? (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h3 className="font-semibold text-cyan-200 mb-1">College Name</h3>
              <p className="text-cyan-100">{formData.name || 'Not specified'}</p>
            </div>
            <div>
              <h3 className="font-semibold text-cyan-200 mb-1">Full Legal Name</h3>
              <p className="text-cyan-100">{formData.fullName || 'Not specified'}</p>
            </div>
          </div>

          <div>
            <h3 className="font-semibold text-cyan-200 mb-1">Address</h3>
            <p className="text-cyan-100">
              {formData.address ? (
                <>
                  {formData.address}, {formData.city}, {formData.state}, {formData.country} {formData.postalCode}
                </>
              ) : (
                'Not specified'
              )}
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div>
              <h3 className="font-semibold text-cyan-200 mb-1">Website</h3>
              <p className="text-cyan-100">
                {formData.website ? (
                  <a href={formData.website} target="_blank" rel="noopener noreferrer" className="text-cyan-300 hover:underline">
                    {formData.website}
                  </a>
                ) : (
                  'Not specified'
                )}
              </p>
            </div>
            <div>
              <h3 className="font-semibold text-cyan-200 mb-1">Phone</h3>
              <p className="text-cyan-100">{formData.phone || 'Not specified'}</p>
            </div>
            <div>
              <h3 className="font-semibold text-cyan-200 mb-1">Email</h3>
              <p className="text-cyan-100">{formData.email || 'Not specified'}</p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h3 className="font-semibold text-cyan-200 mb-1">Accreditation Body</h3>
              <p className="text-cyan-100">{formData.accreditationBody || 'Not specified'}</p>
            </div>
            <div>
              <h3 className="font-semibold text-cyan-200 mb-1">Established</h3>
              <p className="text-cyan-100">{formData.establishmentYear || 'Not specified'}</p>
            </div>
          </div>

          <div>
            <h3 className="font-semibold text-cyan-200 mb-1">Description</h3>
            <p className="text-cyan-100">{formData.description || 'Not specified'}</p>
          </div>
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-cyan-200 mb-2" htmlFor="name">
                College Name*
              </label>
              <input
                id="name"
                name="name"
                type="text"
                value={formData.name}
                onChange={handleInputChange}
                className="w-full px-4 py-2 border border-cyan-500/30 bg-slate-900 text-cyan-100 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-500"
                required
                placeholder="e.g., Stanford University"
              />
            </div>
            
            <div>
              <label className="block text-cyan-200 mb-2" htmlFor="fullName">
                Full Legal Name
              </label>
              <input
                id="fullName"
                name="fullName"
                type="text"
                value={formData.fullName}
                onChange={handleInputChange}
                className="w-full px-4 py-2 border border-cyan-500/30 bg-slate-900 text-cyan-100 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-500"
                placeholder="e.g., Leland Stanford Junior University"
              />
            </div>
          </div>
          
          <div>
            <label className="block text-cyan-200 mb-2" htmlFor="address">
              Address
            </label>
            <input
              id="address"
              name="address"
              type="text"
              value={formData.address}
              onChange={handleInputChange}
              className="w-full px-4 py-2 border border-cyan-500/30 bg-slate-900 text-cyan-100 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-500"
              placeholder="Street address"
            />
          </div>
          
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <label className="block text-cyan-200 mb-2" htmlFor="city">
                City
              </label>
              <input
                id="city"
                name="city"
                type="text"
                value={formData.city}
                onChange={handleInputChange}
                className="w-full px-4 py-2 border border-cyan-500/30 bg-slate-900 text-cyan-100 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-500"
                placeholder="City"
              />
            </div>
            
            <div>
              <label className="block text-cyan-200 mb-2" htmlFor="state">
                State/Province
              </label>
              <input
                id="state"
                name="state"
                type="text"
                value={formData.state}
                onChange={handleInputChange}
                className="w-full px-4 py-2 border border-cyan-500/30 bg-slate-900 text-cyan-100 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-500"
                placeholder="State/Province"
              />
            </div>
            
            <div>
              <label className="block text-cyan-200 mb-2" htmlFor="country">
                Country
              </label>
              <input
                id="country"
                name="country"
                type="text"
                value={formData.country}
                onChange={handleInputChange}
                className="w-full px-4 py-2 border border-cyan-500/30 bg-slate-900 text-cyan-100 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-500"
                placeholder="Country"
              />
            </div>
            
            <div>
              <label className="block text-cyan-200 mb-2" htmlFor="postalCode">
                Postal Code
              </label>
              <input
                id="postalCode"
                name="postalCode"
                type="text"
                value={formData.postalCode}
                onChange={handleInputChange}
                className="w-full px-4 py-2 border border-cyan-500/30 bg-slate-900 text-cyan-100 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-500"
                placeholder="Postal/ZIP code"
              />
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-cyan-200 mb-2" htmlFor="website">
                Website
              </label>
              <input
                id="website"
                name="website"
                type="url"
                value={formData.website}
                onChange={handleInputChange}
                className="w-full px-4 py-2 border border-cyan-500/30 bg-slate-900 text-cyan-100 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-500"
                placeholder="https://www.example.edu"
              />
            </div>
            
            <div>
              <label className="block text-cyan-200 mb-2" htmlFor="phone">
                Phone
              </label>
              <input
                id="phone"
                name="phone"
                type="tel"
                value={formData.phone}
                onChange={handleInputChange}
                className="w-full px-4 py-2 border border-cyan-500/30 bg-slate-900 text-cyan-100 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-500"
                placeholder="+1 (123) 456-7890"
              />
            </div>
            
            <div>
              <label className="block text-cyan-200 mb-2" htmlFor="email">
                Email
              </label>
              <input
                id="email"
                name="email"
                type="email"
                value={formData.email}
                onChange={handleInputChange}
                className="w-full px-4 py-2 border border-cyan-500/30 bg-slate-900 text-cyan-100 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-500"
                placeholder="admissions@example.edu"
              />
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-cyan-200 mb-2" htmlFor="accreditationBody">
                Accreditation Body
              </label>
              <input
                id="accreditationBody"
                name="accreditationBody"
                type="text"
                value={formData.accreditationBody}
                onChange={handleInputChange}
                className="w-full px-4 py-2 border border-cyan-500/30 bg-slate-900 text-cyan-100 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-500"
                placeholder="e.g., WASC Senior College and University Commission"
              />
            </div>
            
            <div>
              <label className="block text-cyan-200 mb-2" htmlFor="establishmentYear">
                Establishment Year
              </label>
              <input
                id="establishmentYear"
                name="establishmentYear"
                type="text"
                value={formData.establishmentYear}
                onChange={handleInputChange}
                className="w-full px-4 py-2 border border-cyan-500/30 bg-slate-900 text-cyan-100 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-500"
                placeholder="e.g., 1885"
              />
            </div>
          </div>
          
          <div>
            <label className="block text-cyan-200 mb-2" htmlFor="description">
              Description
            </label>
            <textarea
              id="description"
              name="description"
              value={formData.description}
              onChange={handleInputChange}
              className="w-full px-4 py-2 border border-cyan-500/30 bg-slate-900 text-cyan-100 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-500"
              rows={4}
              placeholder="Brief description of your institution..."
            />
          </div>
          
          <div className="flex justify-end gap-4">
            {isEditing && (
              <button
                type="button"
                onClick={() => setIsEditing(false)}
                className="px-6 py-2 bg-cyan-900/40 text-cyan-100 rounded-lg hover:bg-cyan-900/60 transition-colors"
                disabled={loading}
              >
                Cancel
              </button>
            )}
            
            <button
              type="submit"
              className="px-6 py-2 bg-cyan-600 text-slate-950 rounded-lg hover:bg-cyan-500 transition-colors flex items-center"
              disabled={loading}
            >
              {loading ? (
                <>
                  <span className="animate-spin rounded-full h-4 w-4 border-t-2 border-b-2 border-white mr-2"></span>
                  Saving...
                </>
              ) : (
                <>
                  <Save className="h-4 w-4 mr-2" />
                  Save Information
                </>
              )}
            </button>
          </div>
        </form>
      )}
    </motion.div>
  );
};

export default CollegeProfileForm;
