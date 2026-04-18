import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { 
  Upload, CheckCircle, AlertCircle, AlertTriangle,
  FileText, Loader2, Eye, Shield
} from 'lucide-react';
import axios from 'axios';

const rawBaseUrl = (import.meta.env.VITE_API_URL || 'http://localhost:5000').replace(/\/$/, '');
const API_BASE_URL = rawBaseUrl.endsWith('/api') ? rawBaseUrl : `${rawBaseUrl}/api`;
const getAuthToken = () => localStorage.getItem('accessToken') || localStorage.getItem('token') || '';

const OCRVerification = ({ 
  organizationId, 
  organizationType,
  credentialRequestId,
  onVerificationComplete 
}) => {
  const [certificateFile, setCertificateFile] = useState(null);
  const [templateType, setTemplateType] = useState('');
  const [verifying, setVerifying] = useState(false);
  const [verificationResult, setVerificationResult] = useState(null);
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

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      const validTypes = ['image/png', 'image/jpeg', 'image/jpg', 'application/pdf'];
      const fileName = (file.name || '').toLowerCase();
      const hasValidExtension = ['.png', '.jpg', '.jpeg', '.pdf'].some((ext) => fileName.endsWith(ext));

      if (!validTypes.includes(file.type) && !hasValidExtension) {
        setError('Please upload a PNG, JPG, or PDF file');
        return;
      }

      if (file.size > 10 * 1024 * 1024) {
        setError('File size must be less than 10MB');
        return;
      }

      setCertificateFile(file);
      setError(null);
      setVerificationResult(null);
      
      if (previewUrl) {
        URL.revokeObjectURL(previewUrl);
      }

      if ((file.type || '').startsWith('image/')) {
        const url = URL.createObjectURL(file);
        setPreviewUrl(url);
      } else {
        setPreviewUrl(null);
      }
    }
  };

  const handleVerify = async (e) => {
    e.preventDefault();

    if (!certificateFile || !organizationId) {
      setError('Please upload a certificate and select an organization');
      return;
    }

    setVerifying(true);
    setError(null);
    setVerificationResult(null);

    try {
      const formData = new FormData();
      formData.append('credential_file', certificateFile);
      formData.append('organization_id', organizationId);
      if (templateType) {
        formData.append('template_type', templateType);
      }
      if (credentialRequestId) {
        formData.append('credential_request_id', credentialRequestId);
      }

      const token = getAuthToken();
      const response = await axios.post(
        `${API_BASE_URL}/ocr/verify-credential-ocr`,
        formData,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'multipart/form-data'
          }
        }
      );

      if (response.data.success) {
        setVerificationResult(response.data.data);
        
        if (onVerificationComplete) {
          onVerificationComplete(response.data.data);
        }
      }
    } catch (err) {
      console.error('Verification error:', err);
      setError(err.response?.data?.message || 'Verification failed');
    } finally {
      setVerifying(false);
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'verified':
        return <CheckCircle className="h-6 w-6 text-emerald-400" />;
      case 'pending_review':
        return <AlertTriangle className="h-6 w-6 text-amber-400" />;
      case 'rejected':
      case 'no_template':
        return <AlertCircle className="h-6 w-6 text-red-400" />;
      default:
        return <Shield className="h-6 w-6 text-cyan-300" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'verified':
        return 'bg-emerald-950/40 border-emerald-500/30 text-emerald-100';
      case 'pending_review':
        return 'bg-amber-950/30 border-amber-500/30 text-amber-100';
      case 'rejected':
      case 'no_template':
        return 'bg-red-950/30 border-red-500/30 text-red-100';
      default:
        return 'bg-slate-950/60 border-cyan-500/30 text-cyan-100';
    }
  };

  const getConfidenceColor = (score) => {
    if (score > 50) return 'text-emerald-300';  // Auto-approve: >50
    if (score >= 30) return 'text-amber-300';  // Manual review: 30-50
    return 'text-red-300';  // Reject: <30
  };

  return (
    <Card className="w-full max-w-2xl mx-auto bg-cyan-950/30 border border-cyan-500/30 text-cyan-100 shadow-lg shadow-cyan-500/10 backdrop-blur-md">
      <CardHeader className="border-b border-cyan-500/20">
        <CardTitle className="flex items-center gap-2 text-cyan-100">
          <Shield className="h-5 w-5 text-cyan-300" />
          OCR Certificate Verification
        </CardTitle>
        <CardDescription className="text-cyan-200/80">
          Upload your certificate for automatic verification
        </CardDescription>
      </CardHeader>
      <CardContent className="pt-6">
        <form onSubmit={handleVerify} className="space-y-6">
          {/* File Upload */}
          <div className="space-y-2">
            <Label htmlFor="certificate-file" className="text-cyan-200">Certificate *</Label>
            <div className="border-2 border-dashed border-cyan-500/30 rounded-lg p-6 text-center hover:border-cyan-400/60 bg-slate-950/40 transition">
              <Input
                id="certificate-file"
                type="file"
                accept=".png,.jpg,.jpeg,.pdf"
                onChange={handleFileChange}
                className="hidden"
              />
              <label htmlFor="certificate-file" className="cursor-pointer">
                {certificateFile ? (
                  <div className="space-y-2">
                    <FileText className="h-12 w-12 mx-auto text-emerald-400" />
                    <p className="text-sm font-medium text-cyan-100">{certificateFile.name}</p>
                    <p className="text-xs text-cyan-300/70">
                      {(certificateFile.size / 1024).toFixed(2)} KB
                    </p>
                  </div>
                ) : (
                  <div className="space-y-2">
                    <Upload className="h-12 w-12 mx-auto text-cyan-400" />
                    <p className="text-sm text-cyan-100">
                      Click to upload certificate
                    </p>
                    <p className="text-xs text-cyan-300/70">
                      PNG, JPG, or PDF (max 10MB)
                    </p>
                  </div>
                )}
              </label>
            </div>

            {previewUrl && (
              <div className="mt-4 rounded-lg border border-cyan-500/30 bg-slate-950/40 p-3">
                <img 
                  src={previewUrl} 
                  alt="Preview" 
                  className="max-w-full h-auto max-h-64 mx-auto border border-cyan-500/20 rounded"
                />
              </div>
            )}
          </div>

          {/* Template Type (Optional) */}
          <div className="space-y-2">
            <Label htmlFor="template-type" className="text-cyan-200">Certificate Type (Optional)</Label>
            <Select value={templateType} onValueChange={setTemplateType}>
              <SelectTrigger className="bg-slate-900 border-cyan-500/30 text-cyan-100 hover:bg-slate-900/90">
                <SelectValue placeholder="Auto-detect or select type" />
              </SelectTrigger>
              <SelectContent className="bg-slate-950 border-cyan-500/30 text-cyan-100">
                {templateTypes.map((type) => (
                  <SelectItem key={type.value} value={type.value} className="text-cyan-100 focus:bg-cyan-900/40 focus:text-cyan-100">
                    {type.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Error Alert */}
          {error && (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          {/* Verification Result */}
          {verificationResult && (
            <div className={`border rounded-lg p-6 ${getStatusColor(verificationResult.verification_status)}`}>
              <div className="flex items-start gap-4">
                {getStatusIcon(verificationResult.verification_status)}
                <div className="flex-1">
                  <h3 className="font-semibold text-lg mb-2 text-cyan-100">
                    {verificationResult.message}
                  </h3>
                  
                  {/* Confidence Score */}
                  <div className="space-y-2 mb-4">
                    <div className="flex justify-between items-center">
                      <span className="text-sm font-medium text-cyan-200">Confidence Score</span>
                      <span className={`text-lg font-bold ${getConfidenceColor(verificationResult.confidence_score)}`}>
                        {verificationResult.confidence_score}%
                      </span>
                    </div>
                    <Progress 
                      value={verificationResult.confidence_score} 
                      className="h-2 bg-cyan-950/60"
                    />
                  </div>

                  {/* Matched Template */}
                  {verificationResult.matched_template && (
                    <div className="mb-4">
                      <Badge variant="outline" className="mb-2 border-cyan-500/30 text-cyan-100 bg-cyan-950/40">
                        Template: {verificationResult.matched_template}
                      </Badge>
                    </div>
                  )}

                  {/* Extracted Data */}
                  {verificationResult.extracted_data && Object.keys(verificationResult.extracted_data).length > 0 && (
                    <div className="bg-cyan-950/40 border border-cyan-500/20 rounded p-4 mt-4">
                      <p className="font-medium mb-2 text-sm text-cyan-100">Extracted Information:</p>
                      <div className="space-y-1 text-sm">
                        {Object.entries(verificationResult.extracted_data).map(([key, value]) => (
                          <div key={key} className="flex justify-between">
                            <span className="text-cyan-300 capitalize">{key.replace('_', ' ')}:</span>
                            <span className="font-medium text-cyan-100">{String(value)}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Matching Details */}
                  {verificationResult.matching_details && (
                    <details className="mt-4">
                      <summary className="text-sm text-cyan-300 cursor-pointer hover:text-cyan-100">
                        View matching details
                      </summary>
                      <div className="mt-2 text-sm space-y-1 bg-cyan-950/40 border border-cyan-500/20 rounded p-3 text-cyan-100">
                        <div className="flex justify-between">
                          <span>Text Similarity:</span>
                          <span className="font-medium">
                            {verificationResult.matching_details.text_similarity}%
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span>Layout Similarity:</span>
                          <span className="font-medium">
                            {verificationResult.matching_details.layout_similarity}%
                          </span>
                        </div>
                      </div>
                    </details>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Submit Button */}
          <Button 
            type="submit" 
            className="w-full bg-cyan-600 text-slate-950 hover:bg-cyan-500" 
            disabled={verifying || !certificateFile}
          >
            {verifying ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Verifying...
              </>
            ) : (
              <>
                <Shield className="mr-2 h-4 w-4" />
                Verify Certificate
              </>
            )}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
};

export default OCRVerification;
