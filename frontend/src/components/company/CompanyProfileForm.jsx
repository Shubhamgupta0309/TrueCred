import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Building, Mail, Globe, Phone, CheckCircle, AlertCircle } from 'lucide-react';
import { companyService, api } from '../../services/api';

export default function CompanyProfileForm({ user, onUpdate }) {
  const [formData, setFormData] = useState({
    name: '',
    website: '',
    address: '',
    phone: '',
    email: ''
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
        <div>
          <p className="font-medium">{formData.name || 'Not specified'}</p>
          <p className="text-sm text-gray-600">{formData.email || 'Not specified'}</p>
          <p className="text-sm text-gray-600">{formData.website || ''}</p>
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium">Company Name</label>
            <input name="name" value={formData.name} onChange={handleChange} className="w-full border rounded p-2" required />
          </div>
          <div>
            <label className="block text-sm font-medium">Email</label>
            <input name="email" value={formData.email} onChange={handleChange} className="w-full border rounded p-2" />
          </div>
          <div>
            <label className="block text-sm font-medium">Website</label>
            <input name="website" value={formData.website} onChange={handleChange} className="w-full border rounded p-2" />
          </div>
          <div className="flex justify-end">
            <button type="submit" disabled={loading} className="px-4 py-2 bg-teal-600 text-white rounded">
              {loading ? 'Saving...' : 'Save'}
            </button>
          </div>
        </form>
      )}
    </motion.div>
  );
}
