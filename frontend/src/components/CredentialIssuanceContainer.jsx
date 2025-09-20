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
    studentEmail: '',
    credentialType: '',
    details: '',
    expiryDate: ''
  });
  const [isLoading, setIsLoading] = useState(false);
  const [emailError, setEmailError] = useState('');
  // Fetch students for this college on mount
  // Remove student fetching, switch to manual email entry

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm(prev => ({ ...prev, [name]: value }));
    if (name === 'studentEmail') setEmailError('');
  };

  const handleSelectChange = (value, name) => {
    setForm(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setEmailError('');

    try {
      // 1. Look up student by email
      const lookupResp = await fetch(`/api/user/by-email?email=${encodeURIComponent(form.studentEmail)}`, {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('accessToken')}` }
      });
      const lookupData = await lookupResp.json();
      if (!lookupData.success || !lookupData.user || !lookupData.user.id) {
        setEmailError('No student found with this email.');
        setIsLoading(false);
        return;
      }
      const studentId = lookupData.user.id;

      // 2. Issue credential to student
      const payload = {
        title: form.credentialType,
        type: form.credentialType,
        description: form.details,
        expiry_date: form.expiryDate,
        issuer: user.organization || user.email
      };
      const issueResp = await fetch(`/api/organization/upload-credential/${studentId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('accessToken')}`
        },
        body: JSON.stringify(payload)
      });
      const issueData = await issueResp.json();
      if (issueData.success) {
        window.alert("Credential Issued: The credential has been successfully issued to the student.");
        setForm({
          studentEmail: '',
          credentialType: '',
          details: '',
          expiryDate: ''
        });
      } else {
        window.alert("Error: " + (issueData.message || "Failed to issue credential."));
      }
    } catch (error) {
      window.alert("Error: Failed to issue credential. Please try again.");
      console.error("Issue credential error:", error);
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
              <label htmlFor="studentEmail" className="block font-medium">Student Email</label>
              <input
                id="studentEmail"
                name="studentEmail"
                type="email"
                placeholder="Enter student email"
                value={form.studentEmail}
                onChange={handleChange}
                required
                className="w-full border border-gray-300 rounded px-3 py-2"
              />
              {emailError && <div className="text-red-500 text-sm">{emailError}</div>}
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
          <div className="mt-4">
            <button type="submit" disabled={isLoading} className="bg-purple-600 text-white px-4 py-2 rounded hover:bg-purple-700">
              {isLoading ? "Issuing..." : "Issue Credential"}
            </button>
          </div>
        </form>
      </div>
    </motion.div>
  );
}

export default CredentialIssuanceContainer;
