import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
// import { Button } from "./ui/button";
// import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "./ui/card";
// import { Label } from "./ui/label";
// import { Input } from "./ui/input";
// import { Textarea } from "./ui/textarea";
// import { useToast } from "./ui/use-toast";
// import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./ui/select";

import { useAuth } from '../context/AuthContext';

const CredentialIssuanceContainer = () => {
  const { user } = useAuth();
  // const { toast } = useToast();
  const [form, setForm] = useState({
    truecredId: '',
    credentialType: '',
    details: '',
    expiryDate: '',
    certificate: null
  });
  const [isLoading, setIsLoading] = useState(false);
  const [isValidatingId, setIsValidatingId] = useState(false);
  const [idValidation, setIdValidation] = useState({ isValid: false, message: '', student: null });
  const [idValidationTimeout, setIdValidationTimeout] = useState(null);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm(prev => ({ ...prev, [name]: value }));
    
    // Validate TrueCred ID when it changes
    if (name === 'truecredId') {
      validateTrueCredId(value);
    }
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    setForm(prev => ({ ...prev, certificate: file }));
  };

  const validateTrueCredId = async (truecredId) => {
    if (!truecredId || truecredId.length < 3) {
      setIdValidation({ isValid: false, message: '', student: null });
      return;
    }

    // Clear previous timeout
    if (idValidationTimeout) {
      clearTimeout(idValidationTimeout);
    }

    // Debounce validation
    const timeout = setTimeout(async () => {
      setIsValidatingId(true);
      try {
        const token = localStorage.getItem('accessToken');
        if (!token) {
          setIdValidation({
            isValid: false,
            message: 'Not authenticated - please log in',
            student: null
          });
          setIsValidatingId(false);
          return;
        }

        const response = await fetch(`/api/organization/student/${truecredId}`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        
        // Check if response is ok before parsing JSON
        if (!response.ok) {
          const errorText = await response.text();
          console.error('API Error Response:', errorText);
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const contentType = response.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
          const textResponse = await response.text();
          console.error('Non-JSON response:', textResponse);
          throw new Error('Server returned non-JSON response');
        }
        
        const data = await response.json();
        
        if (data.success && data.data.student) {
          setIdValidation({
            isValid: true,
            message: 'TC token is correct',
            student: data.data.student
          });
        } else {
          setIdValidation({
            isValid: false,
            message: data.message || 'Invalid TrueCred ID',
            student: null
          });
        }
      } catch (error) {
        console.error('ID validation error:', error);
        
        // Check if it's an HTML response (server error)
        if (error.message.includes('JSON') || error.message.includes('doctype') || error.message.includes('Unexpected token')) {
          setIdValidation({
            isValid: false,
            message: 'Server connection error - please check if backend is running',
            student: null
          });
        } else if (error.message.includes('HTTP 404')) {
          setIdValidation({
            isValid: false,
            message: 'API endpoint not found - please check server configuration',
            student: null
          });
        } else if (error.message.includes('HTTP 403')) {
          setIdValidation({
            isValid: false,
            message: 'Access denied - please check your authentication',
            student: null
          });
        } else {
          setIdValidation({
            isValid: false,
            message: `Error: ${error.message}`,
            student: null
          });
        }
      } finally {
        setIsValidatingId(false);
      }
    }, 500); // 500ms debounce

    setIdValidationTimeout(timeout);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!idValidation.isValid || !idValidation.student) {
      window.alert("Please enter a valid TrueCred ID first.");
      return;
    }

    setIsLoading(true);

    try {
      const studentId = idValidation.student.id;

      // Prepare form data for file upload
      const formData = new FormData();
      formData.append('title', form.credentialType);
      formData.append('type', form.credentialType);
      formData.append('description', form.details);
      formData.append('expiry_date', form.expiryDate);
      if (form.certificate) {
        formData.append('certificate', form.certificate);
      }

      const response = await fetch(`/api/organization/upload-credential/${studentId}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('accessToken')}`
        },
        body: formData
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      if (data.success) {
        window.alert("Credential Issued: The credential has been successfully issued to the student.");
        setForm({
          truecredId: '',
          credentialType: '',
          details: '',
          expiryDate: '',
          certificate: null
        });
        setIdValidation({ isValid: false, message: '', student: null });
      } else {
        window.alert("Error: " + (data.message || "Failed to issue credential."));
      }
    } catch (error) {
      console.error("Issue credential error:", error);
      window.alert("Error: Failed to issue credential. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="w-full max-w-4xl mx-auto p-4"
    >
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="mb-4">
          <h2 className="text-2xl font-bold">Issue New Credential</h2>
          <p className="text-gray-600">Fill in the details to issue a new verifiable credential to a student</p>
        </div>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <label htmlFor="truecredId" className="block font-medium">TrueCred ID</label>
              <div className="relative">
                <input
                  id="truecredId"
                  name="truecredId"
                  type="text"
                  placeholder="Enter TrueCred ID"
                  value={form.truecredId}
                  onChange={handleChange}
                  required
                  className="w-full border border-gray-300 rounded px-3 py-2 pr-8"
                />
                {isValidatingId && (
                  <div className="absolute right-2 top-2">
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-purple-600"></div>
                  </div>
                )}
              </div>
              {idValidation.message && (
                <div className={`text-sm ${idValidation.isValid ? 'text-green-600' : 'text-red-600'}`}>
                  {idValidation.message}
                  {!idValidation.isValid && idValidation.message.includes('Server') && (
                    <button 
                      onClick={() => window.location.reload()} 
                      className="ml-2 text-xs underline hover:no-underline"
                    >
                      Retry
                    </button>
                  )}
                </div>
              )}
              {idValidation.isValid && idValidation.student && (
                <div className="mt-2 p-3 bg-green-50 border border-green-200 rounded-md">
                  <div className="text-sm font-medium text-green-800">Student Found:</div>
                  <div className="text-sm text-green-700 mt-1">
                    <div><strong>Name:</strong> {idValidation.student.name}</div>
                    <div><strong>Email:</strong> {idValidation.student.email}</div>
                    <div><strong>TrueCred ID:</strong> {idValidation.student.truecred_id}</div>
                  </div>
                </div>
              )}
            </div>
            <div className="space-y-2">
              <label htmlFor="credentialType" className="block font-medium">Credential Type</label>
              <select
                id="credentialType"
                name="credentialType"
                value={form.credentialType}
                onChange={handleChange}
                required
                className="w-full border border-gray-300 rounded px-3 py-2"
              >
                <option value="">Select type</option>
                <option value="degree">Degree</option>
                <option value="certificate">Certificate</option>
                <option value="diploma">Diploma</option>
                <option value="badge">Badge</option>
                <option value="award">Award</option>
                <option value="license">License</option>
                <option value="other">Other</option>
              </select>
            </div>
          </div>
          <div className="space-y-2">
            <label htmlFor="details" className="block font-medium">Details</label>
            <textarea
              id="details"
              name="details"
              value={form.details}
              onChange={handleChange}
              placeholder="Enter credential details"
              rows={3}
              required
              className="w-full border border-gray-300 rounded px-3 py-2"
            ></textarea>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <label htmlFor="expiryDate" className="block font-medium">Expiry Date</label>
              <input
                id="expiryDate"
                name="expiryDate"
                type="date"
                value={form.expiryDate}
                onChange={handleChange}
                className="w-full border border-gray-300 rounded px-3 py-2"
              />
            </div>
            <div className="space-y-2">
              <label htmlFor="certificate" className="block font-medium">Certificate File (PDF only - uploads to IPFS)</label>
              <input
                id="certificate"
                name="certificate"
                type="file"
                accept=".pdf"
                onChange={handleFileChange}
                className="w-full border border-gray-300 rounded px-3 py-2"
              />
              <div className="text-xs text-gray-500">
                Only PDF files are accepted. File will be securely stored on IPFS.
              </div>
              {form.certificate && (
                <div className="text-sm text-green-600">
                  Selected: {form.certificate.name} ({(form.certificate.size / 1024 / 1024).toFixed(2)} MB)
                </div>
              )}
            </div>
          </div>
          <div className="mt-4">
            <button 
              type="submit" 
              disabled={isLoading || !idValidation.isValid}
              className="bg-purple-600 text-white px-4 py-2 rounded hover:bg-purple-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
            >
              {isLoading ? "Issuing..." : "Issue Credential"}
            </button>
            {!idValidation.isValid && form.truecredId && (
              <span className="ml-2 text-sm text-red-600">
                Please enter a valid TrueCred ID first
              </span>
            )}
          </div>
        </form>
      </div>
    </motion.div>
  );
}

export default CredentialIssuanceContainer;
