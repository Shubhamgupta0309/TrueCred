import React, { useState, useRef } from 'react';
import { documentService } from '../../services/api';
import { Input } from '../ui/input';
import { Button } from '../ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Alert, AlertDescription } from '../ui/alert';
import { Progress } from '../ui/progress';
import { Upload, FileText, CheckCircle, XCircle, AlertCircle } from 'lucide-react';

const DocumentUpload = ({ onUploadSuccess }) => {
  const [file, setFile] = useState(null);
  const [documentType, setDocumentType] = useState('general');
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [isPublic, setIsPublic] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [message, setMessage] = useState('');
  const [messageType, setMessageType] = useState(''); // 'success', 'error', 'info'
  const fileInputRef = useRef(null);

  const allowedTypes = ['pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png', 'txt'];
  const maxFileSize = 10 * 1024 * 1024; // 10MB

  const handleFileSelect = (event) => {
    const selectedFile = event.target.files[0];
    if (!selectedFile) return;

    // Validate file type
    const fileExtension = selectedFile.name.split('.').pop().toLowerCase();
    if (!allowedTypes.includes(fileExtension)) {
      setMessage(`Invalid file type. Allowed types: ${allowedTypes.join(', ')}`);
      setMessageType('error');
      return;
    }

    // Validate file size
    if (selectedFile.size > maxFileSize) {
      setMessage(`File size exceeds maximum limit of ${maxFileSize / (1024 * 1024)}MB`);
      setMessageType('error');
      return;
    }

    setFile(selectedFile);
    if (!title) {
      setTitle(selectedFile.name);
    }
    setMessage('');
    setMessageType('');
  };

  const handleUpload = async () => {
    if (!file) {
      setMessage('Please select a file to upload');
      setMessageType('error');
      return;
    }

    if (!title.trim()) {
      setMessage('Please provide a title for the document');
      setMessageType('error');
      return;
    }

    setUploading(true);
    setUploadProgress(0);
    setMessage('');

    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('document_type', documentType);
      formData.append('title', title.trim());
      formData.append('description', description.trim());
      formData.append('is_public', isPublic.toString());

      // Simulate progress for better UX
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return 90;
          }
          return prev + 10;
        });
      }, 200);

      const response = await documentService.uploadDocument(formData);

      clearInterval(progressInterval);
      setUploadProgress(100);

      setMessage('Document uploaded successfully!');
      setMessageType('success');

      // Reset form
      setFile(null);
      setTitle('');
      setDescription('');
      setIsPublic(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }

      // Notify parent component
      if (onUploadSuccess) {
        onUploadSuccess(response.data);
      }

    } catch (error) {
      setMessage(error.response?.data?.message || 'Failed to upload document');
      setMessageType('error');
    } finally {
      setUploading(false);
      setTimeout(() => setUploadProgress(0), 1000);
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getFileIcon = (fileType) => {
    if (fileType === 'pdf') return '📄';
    if (['doc', 'docx'].includes(fileType)) return '📝';
    if (['jpg', 'jpeg', 'png'].includes(fileType)) return '🖼️';
    return '📄';
  };

  return (
    <Card className="w-full max-w-2xl mx-auto">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Upload className="h-5 w-5" />
          Upload Document
        </CardTitle>
        <CardDescription>
          Upload documents to IPFS and optionally store them on the blockchain for verification.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* File Selection */}
        <div className="space-y-2">
          <label className="text-sm font-medium">Document File</label>
          <div className="flex items-center gap-4">
            <Input
              ref={fileInputRef}
              type="file"
              accept={allowedTypes.map(type => `.${type}`).join(',')}
              onChange={handleFileSelect}
              disabled={uploading}
              className="flex-1"
            />
            <Button
              type="button"
              variant="outline"
              onClick={() => fileInputRef.current?.click()}
              disabled={uploading}
            >
              Choose File
            </Button>
          </div>
          {file && (
            <div className="flex items-center gap-2 p-2 bg-muted rounded-md">
              <span className="text-lg">{getFileIcon(file.name.split('.').pop().toLowerCase())}</span>
              <div className="flex-1">
                <p className="text-sm font-medium">{file.name}</p>
                <p className="text-xs text-muted-foreground">{formatFileSize(file.size)}</p>
              </div>
            </div>
          )}
        </div>

        {/* Document Type */}
        <div className="space-y-2">
          <label className="text-sm font-medium">Document Type</label>
          <select
            value={documentType}
            onChange={(e) => setDocumentType(e.target.value)}
            disabled={uploading}
            className="w-full h-9 px-3 py-1 text-sm border border-input bg-background rounded-md"
          >
            <option value="general">General Document</option>
            <option value="degree">Degree Certificate</option>
            <option value="transcript">Academic Transcript</option>
            <option value="certificate">Professional Certificate</option>
            <option value="diploma">Diploma</option>
            <option value="license">Professional License</option>
            <option value="award">Award/Certificate</option>
          </select>
        </div>

        {/* Title */}
        <div className="space-y-2">
          <label className="text-sm font-medium">Title</label>
          <Input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Enter document title"
            disabled={uploading}
            maxLength={200}
          />
        </div>

        {/* Description */}
        <div className="space-y-2">
          <label className="text-sm font-medium">Description (Optional)</label>
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Enter document description"
            disabled={uploading}
            maxLength={500}
            rows={3}
            className="w-full px-3 py-2 text-sm border border-input bg-background rounded-md resize-none"
          />
        </div>

        {/* Public Access */}
        <div className="flex items-center space-x-2">
          <input
            type="checkbox"
            id="isPublic"
            checked={isPublic}
            onChange={(e) => setIsPublic(e.target.checked)}
            disabled={uploading}
            className="h-4 w-4"
          />
          <label htmlFor="isPublic" className="text-sm font-medium">
            Make document publicly accessible
          </label>
        </div>

        {/* Upload Progress */}
        {uploading && (
          <div className="space-y-2">
            <div className="flex items-center justify-between text-sm">
              <span>Uploading...</span>
              <span>{uploadProgress}%</span>
            </div>
            <Progress value={uploadProgress} className="w-full" />
          </div>
        )}

        {/* Message */}
        {message && (
          <Alert className={`${
            messageType === 'success' ? 'border-green-200 bg-green-50' :
            messageType === 'error' ? 'border-red-200 bg-red-50' :
            'border-blue-200 bg-blue-50'
          }`}>
            <div className="flex items-center gap-2">
              {messageType === 'success' && <CheckCircle className="h-4 w-4 text-green-600" />}
              {messageType === 'error' && <XCircle className="h-4 w-4 text-red-600" />}
              {messageType === 'info' && <AlertCircle className="h-4 w-4 text-blue-600" />}
              <AlertDescription className={
                messageType === 'success' ? 'text-green-800' :
                messageType === 'error' ? 'text-red-800' :
                'text-blue-800'
              }>
                {message}
              </AlertDescription>
            </div>
          </Alert>
        )}

        {/* Upload Button */}
        <Button
          onClick={handleUpload}
          disabled={!file || uploading}
          className="w-full"
        >
          {uploading ? 'Uploading...' : 'Upload Document'}
        </Button>

        {/* File Requirements */}
        <div className="text-xs text-muted-foreground space-y-1">
          <p><strong>Supported formats:</strong> PDF, DOC, DOCX, JPG, JPEG, PNG, TXT</p>
          <p><strong>Maximum file size:</strong> 10MB</p>
          <p><strong>Note:</strong> Documents will be stored on IPFS and optionally on the blockchain for verification.</p>
        </div>
      </CardContent>
    </Card>
  );
};

export default DocumentUpload;