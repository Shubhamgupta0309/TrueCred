import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Upload, FileText, X, Calendar, AlertCircle, CheckCircle } from 'lucide-react';
import { api } from '../../services/api';

export default function StudentCredentialUpload({ student, onComplete }) {
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    type: 'certificate',
    issue_date: new Date().toISOString().split('T')[0],
    expiry_date: '',
    document: null
  });
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  
  // Handle input changes
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };
  
  // Handle file selection
  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      // Limit file size to 5MB
      if (file.size > 5 * 1024 * 1024) {
        setError('File size exceeds 5MB limit');
        return;
      }
      
      // Read file as base64
      const reader = new FileReader();
      reader.onload = (event) => {
        setFormData(prev => ({
          ...prev,
          document: event.target.result
        }));
      };
      reader.readAsDataURL(file);
    }
  };
  
  // Remove file
  const removeFile = () => {
    setFormData(prev => ({
      ...prev,
      document: null
    }));
  };
  
  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(false);
    setUploadProgress(0);
    
    // Simulate upload progress
    const progressInterval = setInterval(() => {
      setUploadProgress(prev => {
        const newProgress = prev + 5;
        return newProgress > 90 ? 90 : newProgress;
      });
    }, 300);
    
    try {
      const payload = {
        ...formData,
        student_id: student.id
      };
      
      // Upload credential
      const response = await api.post(`/api/organization/upload-credential/${student.id}`, payload);
      
      if (response.data.success) {
        setSuccess(true);
        setUploadProgress(100);
        
        // Reset form after success
        setTimeout(() => {
          setFormData({
            title: '',
            description: '',
            type: 'certificate',
            issue_date: new Date().toISOString().split('T')[0],
            expiry_date: '',
            document: null
          });
          
          // Call completion callback
          if (onComplete) {
            onComplete(response.data.data);
          }
        }, 2000);
      } else {
        setError(response.data.message || 'Failed to upload credential');
        setUploadProgress(0);
      }
    } catch (error) {
      console.error('Error uploading credential:', error);
      setError('An error occurred while uploading the credential. Please try again.');
      setUploadProgress(0);
    } finally {
      clearInterval(progressInterval);
      setLoading(false);
    }
  };
  
  return (
    <motion.div
      className="bg-white p-6 rounded-lg shadow-lg"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <div className="flex items-start justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-800">Upload Credential</h2>
          <p className="text-gray-600 mt-1">
            For student: <span className="font-medium">{student.name}</span>
          </p>
          <p className="text-sm font-mono text-blue-700">{student.truecred_id}</p>
        </div>
        
        {success && (
          <div className="bg-green-100 text-green-800 p-2 rounded-full">
            <CheckCircle className="h-6 w-6" />
          </div>
        )}
      </div>
      
      {error && (
        <div className="mb-6 p-4 bg-red-50 rounded-lg border border-red-200 flex items-center">
          <AlertCircle className="h-5 w-5 text-red-500 mr-2" />
          <p className="text-red-700">{error}</p>
        </div>
      )}
      
      {success ? (
        <div className="p-6 bg-green-50 rounded-lg border border-green-200 text-center">
          <CheckCircle className="h-12 w-12 text-green-500 mx-auto mb-4" />
          <h3 className="text-xl font-bold text-green-800 mb-2">Credential Uploaded Successfully!</h3>
          <p className="text-green-700">
            The credential has been issued to {student.name} and recorded on the blockchain.
          </p>
          <button
            onClick={() => {
              setSuccess(false);
              if (onComplete) onComplete();
            }}
            className="mt-6 px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
          >
            Continue
          </button>
        </div>
      ) : (
        <form onSubmit={handleSubmit}>
          <div className="mb-6">
            <label className="block text-gray-700 mb-2" htmlFor="title">
              Credential Title*
            </label>
            <input
              id="title"
              name="title"
              type="text"
              value={formData.title}
              onChange={handleInputChange}
              className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
              placeholder="e.g., Bachelor of Science in Computer Science"
            />
          </div>
          
          <div className="mb-6">
            <label className="block text-gray-700 mb-2" htmlFor="type">
              Credential Type*
            </label>
            <select
              id="type"
              name="type"
              value={formData.type}
              onChange={handleInputChange}
              className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            >
              <option value="diploma">Diploma</option>
              <option value="degree">Degree</option>
              <option value="certificate">Certificate</option>
              <option value="badge">Badge</option>
              <option value="award">Award</option>
              <option value="license">License</option>
              <option value="other">Other</option>
            </select>
          </div>
          
          <div className="mb-6">
            <label className="block text-gray-700 mb-2" htmlFor="description">
              Description
            </label>
            <textarea
              id="description"
              name="description"
              value={formData.description}
              onChange={handleInputChange}
              rows="3"
              className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Provide details about this credential"
            ></textarea>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            <div>
              <label className="block text-gray-700 mb-2" htmlFor="issue_date">
                Issue Date*
              </label>
              <div className="relative">
                <input
                  id="issue_date"
                  name="issue_date"
                  type="date"
                  value={formData.issue_date}
                  onChange={handleInputChange}
                  className="w-full px-4 py-2 pl-10 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
                <Calendar className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-5 w-5" />
              </div>
            </div>
            
            <div>
              <label className="block text-gray-700 mb-2" htmlFor="expiry_date">
                Expiry Date <span className="text-gray-500">(optional)</span>
              </label>
              <div className="relative">
                <input
                  id="expiry_date"
                  name="expiry_date"
                  type="date"
                  value={formData.expiry_date}
                  onChange={handleInputChange}
                  className="w-full px-4 py-2 pl-10 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <Calendar className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-5 w-5" />
              </div>
            </div>
          </div>
          
          <div className="mb-6">
            <label className="block text-gray-700 mb-2">
              Document <span className="text-gray-500">(optional, max 5MB)</span>
            </label>
            
            {formData.document ? (
              <div className="p-4 border border-blue-200 bg-blue-50 rounded-lg">
                <div className="flex items-center justify-between">
                  <div className="flex items-center">
                    <FileText className="h-6 w-6 text-blue-600 mr-3" />
                    <span className="text-blue-800">Document attached</span>
                  </div>
                  <button
                    type="button"
                    onClick={removeFile}
                    className="text-red-600 hover:text-red-800"
                  >
                    <X className="h-5 w-5" />
                  </button>
                </div>
              </div>
            ) : (
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
                <Upload className="h-8 w-8 text-gray-400 mx-auto mb-2" />
                <p className="text-gray-500 mb-2">Drag and drop a file here, or click to select</p>
                <input
                  type="file"
                  className="hidden"
                  id="document-upload"
                  onChange={handleFileChange}
                  accept=".pdf,.doc,.docx,.jpg,.jpeg,.png"
                />
                <label
                  htmlFor="document-upload"
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors inline-block cursor-pointer"
                >
                  Select File
                </label>
              </div>
            )}
          </div>
          
          {loading && (
            <div className="mb-6">
              <div className="w-full bg-gray-200 rounded-full h-2.5">
                <div 
                  className="bg-blue-600 h-2.5 rounded-full transition-all duration-300" 
                  style={{ width: `${uploadProgress}%` }}
                ></div>
              </div>
              <p className="text-sm text-gray-600 mt-2 text-center">
                {uploadProgress < 100 
                  ? `Uploading and recording on blockchain... ${uploadProgress}%`
                  : 'Upload complete!'}
              </p>
            </div>
          )}
          
          <div className="flex justify-end">
            <button
              type="submit"
              disabled={loading}
              className={`px-6 py-2 rounded-lg text-white ${
                loading ? 'bg-gray-400' : 'bg-green-600 hover:bg-green-700'
              } transition-colors`}
            >
              {loading ? 'Uploading...' : 'Issue Credential'}
            </button>
          </div>
        </form>
      )}
    </motion.div>
  );
}
