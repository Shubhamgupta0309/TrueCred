import React, { useState, useEffect } from 'react';
import { documentService } from '../../services/api';
import { Button } from '../ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Alert, AlertDescription } from '../ui/alert';
import { Badge } from '../ui/badge';
import { CheckCircle, XCircle, Eye, Download, ExternalLink, AlertCircle, Clock } from 'lucide-react';

const DocumentVerification = ({ userRole }) => {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [verifying, setVerifying] = useState(null);
  const [message, setMessage] = useState('');
  const [messageType, setMessageType] = useState('');
  const [stats, setStats] = useState({
    pending: 0,
    verified: 0,
    rejected: 0
  });

  useEffect(() => {
    if (userRole === 'college' || userRole === 'company' || userRole === 'admin') {
      loadPendingDocuments();
      loadStats();
    }
  }, [userRole]);

  const loadPendingDocuments = async () => {
    try {
      setLoading(true);
      const response = await documentService.getPendingVerifications();
      setDocuments(response.data.documents || []);
    } catch (error) {
      setMessage('Failed to load pending documents');
      setMessageType('error');
    } finally {
      setLoading(false);
    }
  };

  const loadStats = async () => {
    try {
      const response = await documentService.getVerificationStats();
      setStats({
        pending: response.data.overall_stats.pending,
        verified: response.data.overall_stats.verified,
        rejected: response.data.overall_stats.rejected
      });
    } catch (error) {
      console.error('Failed to load verification stats:', error);
    }
  };

  const handleVerification = async (documentId, action, comments = '') => {
    setVerifying(documentId);
    setMessage('');

    try {
      await documentService.verifyDocument(documentId, {
        verification_status: action,
        comments: comments,
        verified_by: 'Issuer' // This would come from user context
      });

      setMessage(`Document ${action}ed successfully`);
      setMessageType('success');

      // Reload documents and stats
      await loadPendingDocuments();
      await loadStats();

    } catch (error) {
      setMessage(error.response?.data?.message || `Failed to ${action} document`);
      setMessageType('error');
    } finally {
      setVerifying(null);
    }
  };

  const handleViewDocument = async (documentId) => {
    try {
      const response = await documentService.getDocument(documentId);
      const ipfsUrl = response.data.ipfs_url;
      window.open(ipfsUrl, '_blank');
    } catch (error) {
      setMessage('Failed to open document');
      setMessageType('error');
    }
  };

  const handleDownloadDocument = async (documentId, filename) => {
    try {
      const response = await documentService.downloadDocument(documentId);
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      setMessage('Failed to download document');
      setMessageType('error');
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getDocumentTypeBadge = (type) => {
    const colors = {
      degree: 'bg-blue-100 text-blue-800',
      transcript: 'bg-green-100 text-green-800',
      certificate: 'bg-purple-100 text-purple-800',
      diploma: 'bg-orange-100 text-orange-800',
      license: 'bg-red-100 text-red-800',
      general: 'bg-gray-100 text-gray-800'
    };
    return colors[type] || colors.general;
  };

  if (userRole !== 'college' && userRole !== 'company' && userRole !== 'admin') {
    return (
      <Alert>
        <AlertCircle className="h-4 w-4" />
        <AlertDescription>
          You don't have permission to access document verification.
        </AlertDescription>
      </Alert>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">Document Verification</h2>
        <div className="flex gap-4">
          <Badge variant="outline" className="flex items-center gap-1">
            <Clock className="h-3 w-3" />
            Pending: {stats.pending}
          </Badge>
          <Badge variant="outline" className="flex items-center gap-1 bg-green-50">
            <CheckCircle className="h-3 w-3 text-green-600" />
            Verified: {stats.verified}
          </Badge>
          <Badge variant="outline" className="flex items-center gap-1 bg-red-50">
            <XCircle className="h-3 w-3 text-red-600" />
            Rejected: {stats.rejected}
          </Badge>
        </div>
      </div>

      {/* Message */}
      {message && (
        <Alert className={`${
          messageType === 'success' ? 'border-green-200 bg-green-50' :
          messageType === 'error' ? 'border-red-200 bg-red-50' :
          'border-blue-200 bg-blue-50'
        }`}>
          <AlertDescription className={
            messageType === 'success' ? 'text-green-800' :
            messageType === 'error' ? 'text-red-800' :
            'text-blue-800'
          }>
            {message}
          </AlertDescription>
        </Alert>
      )}

      {/* Documents List */}
      {loading ? (
        <div className="text-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
          <p className="mt-2 text-muted-foreground">Loading documents...</p>
        </div>
      ) : documents.length === 0 ? (
        <Card>
          <CardContent className="text-center py-8">
            <FileText className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
            <h3 className="text-lg font-medium mb-2">No Pending Documents</h3>
            <p className="text-muted-foreground">
              All documents have been reviewed. Check back later for new submissions.
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-4">
          {documents.map((doc) => (
            <Card key={doc.document_id}>
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <CardTitle className="text-lg">{doc.title}</CardTitle>
                    <CardDescription className="mt-1">
                      {doc.description || 'No description provided'}
                    </CardDescription>
                    <div className="flex items-center gap-2 mt-2">
                      <Badge className={getDocumentTypeBadge(doc.document_type)}>
                        {doc.document_type}
                      </Badge>
                      <span className="text-sm text-muted-foreground">
                        {formatFileSize(doc.file_size)}
                      </span>
                      <span className="text-sm text-muted-foreground">
                        Uploaded: {new Date(doc.upload_timestamp).toLocaleDateString()}
                      </span>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-medium">{doc.user_info?.name || 'Unknown User'}</p>
                    <p className="text-xs text-muted-foreground">{doc.user_info?.email || 'No email'}</p>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="flex items-center justify-between">
                  <div className="flex gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleViewDocument(doc.document_id)}
                    >
                      <Eye className="h-4 w-4 mr-1" />
                      View
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleDownloadDocument(doc.document_id, doc.original_filename)}
                    >
                      <Download className="h-4 w-4 mr-1" />
                      Download
                    </Button>
                  </div>
                  <div className="flex gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => {
                        const comments = prompt('Enter verification comments (optional):');
                        handleVerification(doc.document_id, 'verified', comments || '');
                      }}
                      disabled={verifying === doc.document_id}
                      className="bg-green-50 hover:bg-green-100 border-green-200 text-green-700"
                    >
                      <CheckCircle className="h-4 w-4 mr-1" />
                      {verifying === doc.document_id ? 'Verifying...' : 'Verify'}
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => {
                        const comments = prompt('Enter rejection reason (required):');
                        if (comments && comments.trim()) {
                          handleVerification(doc.document_id, 'rejected', comments.trim());
                        }
                      }}
                      disabled={verifying === doc.document_id}
                      className="bg-red-50 hover:bg-red-100 border-red-200 text-red-700"
                    >
                      <XCircle className="h-4 w-4 mr-1" />
                      {verifying === doc.document_id ? 'Rejecting...' : 'Reject'}
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
};

export default DocumentVerification;