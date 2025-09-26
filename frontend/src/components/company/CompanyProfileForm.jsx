import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Building, Mail, Globe, Phone, CheckCircle, AlertCircle, Save } from 'lucide-react';
import { companyService, api } from '../../services/api';

export default function CompanyProfileForm({ user, onUpdate }) {
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

  useEffect(() => {
    // Attempt to fetch company profile if companyService has an endpoint
    const fetchProfile = async () => {
      try {
        if (companyService.getProfile) {
          const resp = await companyService.getProfile();
          if (resp.data && resp.data.success) {
            setFormData(prev => ({ ...prev, ...resp.data.data }));
          }
        } else {
          // Populate from user if available
          setFormData(prev => ({
            ...prev,
            name: user?.name || '',
            email: user?.email || ''
          }));
        }
      } catch (err) {
        console.warn('Company profile fetch not available:', err);
      }
    };
    fetchProfile();
  }, []);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      // If companyService updateProfile exists, use it; otherwise POST to /company/profile
      const submit = companyService.updateProfile ? companyService.updateProfile : (data) => api.post('/api/company/profile', data);
      const resp = await submit(formData);
      if (resp.data && resp.data.success) {
        setSuccess(true);
        setIsEditing(false);
        if (onUpdate) onUpdate(formData);
      } else {
        setError(resp.data?.message || 'Failed to save profile');
      }
    } catch (err) {
      console.error('Error saving company profile:', err);
      setError(err.response?.data?.message || err.message || 'Network error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <motion.div className="bg-white rounded-2xl shadow-lg p-6">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Building className="h-5 w-5 text-teal-600" />
          <h3 className="text-lg font-semibold">Company Profile</h3>
        </div>
        {!isEditing && (
          <button onClick={() => setIsEditing(true)} className="px-3 py-1 bg-teal-100 text-teal-700 rounded">Edit</button>
        )}
      </div>

      {error && (
        <div className="mb-4 p-3 bg-red-50 rounded">
          <AlertCircle className="inline-block mr-2" /> <span className="text-red-700">{error}</span>
        </div>
      )}

      {success && (
        <div className="mb-4 p-3 bg-green-50 rounded">
          <CheckCircle className="inline-block mr-2" /> <span className="text-green-700">Saved</span>
        </div>
      )}

      {!isEditing ? (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h3 className="font-semibold text-gray-700 mb-1">Company Name</h3>
              <p className="text-gray-800">{formData.name || 'Not specified'}</p>
            </div>
            <div>
              <h3 className="font-semibold text-gray-700 mb-1">Full Legal Name</h3>
              <p className="text-gray-800">{formData.fullName || 'Not specified'}</p>
            </div>
          </div>

          <div>
            <h3 className="font-semibold text-gray-700 mb-1">Address</h3>
            <p className="text-gray-800">{formData.address || 'Not specified'}</p>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <h3 className="font-semibold text-gray-700 mb-1">City</h3>
              <p className="text-gray-800">{formData.city || 'Not specified'}</p>
            </div>
            <div>
              <h3 className="font-semibold text-gray-700 mb-1">State/Province</h3>
              <p className="text-gray-800">{formData.state || 'Not specified'}</p>
            </div>
            <div>
              <h3 className="font-semibold text-gray-700 mb-1">Country</h3>
              <p className="text-gray-800">{formData.country || 'Not specified'}</p>
            </div>
            <div>
              <h3 className="font-semibold text-gray-700 mb-1">Postal Code</h3>
              <p className="text-gray-800">{formData.postalCode || 'Not specified'}</p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <h3 className="font-semibold text-gray-700 mb-1">Website</h3>
              <p className="text-gray-800">{formData.website || 'Not specified'}</p>
            </div>
            <div>
              <h3 className="font-semibold text-gray-700 mb-1">Phone</h3>
              <p className="text-gray-800">{formData.phone || 'Not specified'}</p>
            </div>
            <div>
              <h3 className="font-semibold text-gray-700 mb-1">Email</h3>
              <p className="text-gray-800">{formData.email || 'Not specified'}</p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <h3 className="font-semibold text-gray-700 mb-1">Accreditation Body</h3>
              <p className="text-gray-800">{formData.accreditationBody || 'Not specified'}</p>
            </div>
            <div>
              <h3 className="font-semibold text-gray-700 mb-1">Establishment Year</h3>
              <p className="text-gray-800">{formData.establishmentYear || 'Not specified'}</p>
            </div>
          </div>

          <div>
            <h3 className="font-semibold text-gray-700 mb-1">Description</h3>
            <p className="text-gray-800">{formData.description || 'Not specified'}</p>
          </div>
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-gray-700 mb-2" htmlFor="name">
                Company Name*
              </label>
              <input
                id="name"
                name="name"
                type="text"
                value={formData.name}
                onChange={handleChange}
                className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500"
                required
                placeholder="e.g., PrimeX Technologies"
              />
            </div>
            
            <div>
              <label className="block text-gray-700 mb-2" htmlFor="fullName">
                Full Legal Name
              </label>
              <input
                id="fullName"
                name="fullName"
                type="text"
                value={formData.fullName}
                onChange={handleChange}
                className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500"
                placeholder="e.g., PrimeX Technologies Private Limited"
              />
            </div>
          </div>
          
          <div>
            <label className="block text-gray-700 mb-2" htmlFor="address">
              Address
            </label>
            <input
              id="address"
              name="address"
              type="text"
              value={formData.address}
              onChange={handleChange}
              className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500"
              placeholder="Street address"
            />
          </div>
          
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <label className="block text-gray-700 mb-2" htmlFor="city">
                City
              </label>
              <input
                id="city"
                name="city"
                type="text"
                value={formData.city}
                onChange={handleChange}
                className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500"
                placeholder="City"
              />
            </div>
            
            <div>
              <label className="block text-gray-700 mb-2" htmlFor="state">
                State/Province
              </label>
              <input
                id="state"
                name="state"
                type="text"
                value={formData.state}
                onChange={handleChange}
                className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500"
                placeholder="State/Province"
              />
            </div>
            
            <div>
              <label className="block text-gray-700 mb-2" htmlFor="country">
                Country
              </label>
              <input
                id="country"
                name="country"
                type="text"
                value={formData.country}
                onChange={handleChange}
                className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500"
                placeholder="Country"
              />
            </div>
            
            <div>
              <label className="block text-gray-700 mb-2" htmlFor="postalCode">
                Postal Code
              </label>
              <input
                id="postalCode"
                name="postalCode"
                type="text"
                value={formData.postalCode}
                onChange={handleChange}
                className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500"
                placeholder="Postal/ZIP code"
              />
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-gray-700 mb-2" htmlFor="website">
                Website
              </label>
              <input
                id="website"
                name="website"
                type="url"
                value={formData.website}
                onChange={handleChange}
                className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500"
                placeholder="https://www.example.com"
              />
            </div>
            
            <div>
              <label className="block text-gray-700 mb-2" htmlFor="phone">
                Phone
              </label>
              <input
                id="phone"
                name="phone"
                type="tel"
                value={formData.phone}
                onChange={handleChange}
                className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500"
                placeholder="+1 (123) 456-7890"
              />
            </div>
            
            <div>
              <label className="block text-gray-700 mb-2" htmlFor="email">
                Email
              </label>
              <input
                id="email"
                name="email"
                type="email"
                value={formData.email}
                onChange={handleChange}
                className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500"
                placeholder="contact@example.com"
              />
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-gray-700 mb-2" htmlFor="accreditationBody">
                Accreditation Body
              </label>
              <input
                id="accreditationBody"
                name="accreditationBody"
                type="text"
                value={formData.accreditationBody}
                onChange={handleChange}
                className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500"
                placeholder="e.g., ISO 9001 Certified"
              />
            </div>
            
            <div>
              <label className="block text-gray-700 mb-2" htmlFor="establishmentYear">
                Establishment Year
              </label>
              <input
                id="establishmentYear"
                name="establishmentYear"
                type="text"
                value={formData.establishmentYear}
                onChange={handleChange}
                className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500"
                placeholder="e.g., 2010"
              />
            </div>
          </div>
          
          <div>
            <label className="block text-gray-700 mb-2" htmlFor="description">
              Description
            </label>
            <textarea
              id="description"
              name="description"
              value={formData.description}
              onChange={handleChange}
              className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500"
              rows={4}
              placeholder="Brief description of your company..."
            />
          </div>
          
          <div className="flex justify-end gap-4">
            {isEditing && (
              <button
                type="button"
                onClick={() => setIsEditing(false)}
                className="px-6 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 transition-colors"
                disabled={loading}
              >
                Cancel
              </button>
            )}
            
            <button
              type="submit"
              className="px-6 py-2 bg-teal-600 text-white rounded-lg hover:bg-teal-700 transition-colors flex items-center"
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
}
