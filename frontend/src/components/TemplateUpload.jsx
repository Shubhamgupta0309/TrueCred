import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Upload, CheckCircle, AlertCircle, FileText, Loader2 } from 'lucide-react';
import axios from 'axios';

const rawBaseUrl = (import.meta.env.VITE_API_URL || 'http://localhost:5000').replace(/\/$/, '');
const API_BASE_URL = rawBaseUrl.endsWith('/api') ? rawBaseUrl : `${rawBaseUrl}/api`;
const getAuthToken = () => localStorage.getItem('accessToken') || localStorage.getItem('token') || '';

const TemplateUpload = ({ organizationId, organizationName, organizationType }) => {
  const [templateFile, setTemplateFile] = useState(null);
  const [templateName, setTemplateName] = useState('');
  const [templateType, setTemplateType] = useState('');
  const [requiredFields, setRequiredFields] = useState('');
  const [optionalFields, setOptionalFields] = useState('');
  const [uploading, setUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState(null);
  const [error, setError] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);

  const templateTypes = [
    { value: 'degree', label: 'Degree Certificate' },
    { value: 'diploma', label: 'Diploma Certificate' },
    { value: 'internship', label: 'Internship Certificate' },
    { value: 'work_experience', label: 'Work Experience Certificate' },
    { value: 'training', label: 'Training Certificate' },
    { value: 'achievement', label: 'Achievement Certificate' },
    { value: 'other', label: 'Other' }
  ];

  useEffect(() => {
    // Cleanup preview URL on unmount
    return () => {
      if (previewUrl) {
        URL.revokeObjectURL(previewUrl);
      }
    };
  }, [previewUrl]);

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      // Validate file type
      const validTypes = ['image/png', 'image/jpeg', 'image/jpg', 'application/pdf'];
      if (!validTypes.includes(file.type)) {
        setError('Please upload a PNG, JPG, or PDF file');
        return;
      }

      // Validate file size (max 10MB)
      if (file.size > 10 * 1024 * 1024) {
        setError('File size must be less than 10MB');
        return;
      }

      setTemplateFile(file);
      setError(null);
      
      // Create preview for images
      if (file.type.startsWith('image/')) {
        const url = URL.createObjectURL(file);
        setPreviewUrl(url);
      } else {
        setPreviewUrl(null);
      }
    }
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    
    if (!templateFile || !templateName || !templateType) {
      setError('Please fill in all required fields');
      return;
    }

    setUploading(true);
    setError(null);
    setUploadResult(null);

    try {
      const formData = new FormData();
      formData.append('template_file', templateFile);
      formData.append('template_name', templateName);
      formData.append('template_type', templateType);
      formData.append('organization_id', organizationId);
      formData.append('organization_name', organizationName);
      formData.append('organization_type', organizationType);
      
      // Parse and add field lists
      const reqFields = requiredFields.split(',').map(f => f.trim()).filter(f => f);
      const optFields = optionalFields.split(',').map(f => f.trim()).filter(f => f);
      formData.append('required_fields', JSON.stringify(reqFields));
      formData.append('optional_fields', JSON.stringify(optFields));

      const token = getAuthToken();
      const response = await axios.post(
        `${API_BASE_URL}/templates/upload`,
        formData,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'multipart/form-data'
          }
        }
      );

      if (response.data.success) {
        setUploadResult(response.data.data);
        // Reset form
        setTemplateFile(null);
        setTemplateName('');
        setTemplateType('');
        setRequiredFields('');
        setOptionalFields('');
        setPreviewUrl(null);
        
        // Reset file input
        const fileInput = document.getElementById('template-file-input');
        if (fileInput) {
          fileInput.value = '';
        }
      }
    } catch (err) {
      console.error('Upload error:', err);
      setError(err.response?.data?.message || 'Failed to upload template');
    } finally {
      setUploading(false);
    }
  };

  return (
    <Card className="w-full max-w-2xl mx-auto">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Upload className="h-5 w-5" />
          Upload Certificate Template
        </CardTitle>
        <CardDescription>
          Upload a master certificate template for OCR-based verification
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleUpload} className="space-y-6">
          {/* File Upload */}
          <div className="space-y-2">
            <Label htmlFor="template-file-input">Certificate Template *</Label>
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-gray-400 transition">
              <Input
                id="template-file-input"
                type="file"
                accept=".png,.jpg,.jpeg,.pdf"
                onChange={handleFileChange}
                className="hidden"
              />
              <label htmlFor="template-file-input" className="cursor-pointer">
                {templateFile ? (
                  <div className="space-y-2">
                    <FileText className="h-12 w-12 mx-auto text-green-600" />
                    <p className="text-sm font-medium">{templateFile.name}</p>
                    <p className="text-xs text-gray-500">
                      {(templateFile.size / 1024).toFixed(2)} KB
                    </p>
                  </div>
                ) : (
                  <div className="space-y-2">
                    <Upload className="h-12 w-12 mx-auto text-gray-400" />
                    <p className="text-sm text-gray-600">
                      Click to upload or drag and drop
                    </p>
                    <p className="text-xs text-gray-500">
                      PNG, JPG or PDF (max 10MB)
                    </p>
                  </div>
                )}
              </label>
            </div>
            
            {/* Preview */}
            {previewUrl && (
              <div className="mt-4">
                <img 
                  src={previewUrl} 
                  alt="Preview" 
                  className="max-w-full h-auto max-h-64 mx-auto border rounded"
                />
              </div>
            )}
          </div>

          {/* Template Name */}
          <div className="space-y-2">
            <Label htmlFor="template-name">Template Name *</Label>
            <Input
              id="template-name"
              placeholder="e.g., Computer Science Degree 2024"
              value={templateName}
              onChange={(e) => setTemplateName(e.target.value)}
              required
            />
          </div>

          {/* Template Type */}
          <div className="space-y-2">
            <Label htmlFor="template-type">Certificate Type *</Label>
            <Select value={templateType} onValueChange={setTemplateType}>
              <SelectTrigger>
                <SelectValue placeholder="Select certificate type" />
              </SelectTrigger>
              <SelectContent>
                {templateTypes.map((type) => (
                  <SelectItem key={type.value} value={type.value}>
                    {type.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Required Fields */}
          <div className="space-y-2">
            <Label htmlFor="required-fields">Required Fields</Label>
            <Input
              id="required-fields"
              placeholder="name, date, course (comma-separated)"
              value={requiredFields}
              onChange={(e) => setRequiredFields(e.target.value)}
            />
            <p className="text-xs text-gray-500">
              Fields that must be present for verification
            </p>
          </div>

          {/* Optional Fields */}
          <div className="space-y-2">
            <Label htmlFor="optional-fields">Optional Fields</Label>
            <Input
              id="optional-fields"
              placeholder="grade, roll_number (comma-separated)"
              value={optionalFields}
              onChange={(e) => setOptionalFields(e.target.value)}
            />
            <p className="text-xs text-gray-500">
              Additional fields that may be extracted
            </p>
          </div>

          {/* Error Alert */}
          {error && (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          {/* Success Alert */}
          {uploadResult && (
            <Alert className="bg-green-50 border-green-200">
              <CheckCircle className="h-4 w-4 text-green-600" />
              <AlertDescription className="text-green-800">
                <p className="font-semibold">Template uploaded successfully!</p>
                <p className="text-sm mt-1">
                  OCR Confidence: {uploadResult.confidence}%
                </p>
                {uploadResult.key_fields && Object.keys(uploadResult.key_fields).length > 0 && (
                  <div className="mt-2 text-sm">
                    <p className="font-medium">Detected Fields:</p>
                    <ul className="list-disc list-inside">
                      {Object.entries(uploadResult.key_fields).map(([key, value]) => (
                        <li key={key}>
                          {key}: {value}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </AlertDescription>
            </Alert>
          )}

          {/* Submit Button */}
          <Button 
            type="submit" 
            className="w-full" 
            disabled={uploading || !templateFile}
          >
            {uploading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Processing...
              </>
            ) : (
              <>
                <Upload className="mr-2 h-4 w-4" />
                Upload Template
              </>
            )}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
};

export default TemplateUpload;
