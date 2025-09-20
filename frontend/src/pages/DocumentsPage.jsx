import React, { useState, useEffect } from 'react';
import DocumentUpload from '../components/DocumentUpload';
import DocumentVerification from '../components/DocumentVerification';
import { documentService } from '../services/api';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { Badge } from '../components/ui/badge';
import { FileText, Upload, CheckCircle, Eye, Download, ExternalLink } from 'lucide-react';

const DocumentsPage = ({ userRole }) => {
  const [activeTab, setActiveTab] = useState('upload');
  const [userDocuments, setUserDocuments] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadUserDocuments();
  }, []);

  const loadUserDocuments = async () => {
    try {
      setLoading(true);
      // This would need to be updated to get current user's documents
      // For now, we'll show a placeholder
      setUserDocuments([]);
    } catch (error) {
      console.error('Failed to load user documents:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleUploadSuccess = (documentData) => {
    // Refresh user's documents
    loadUserDocuments();
    // Switch to documents tab to show the uploaded document
    setActiveTab('documents');
  };

  const handleViewDocument = async (documentId) => {
    try {
      const response = await documentService.getDocument(documentId);
      const ipfsUrl = response.data.ipfs_url;
      window.open(ipfsUrl, '_blank');
    } catch (error) {
      console.error('Failed to view document:', error);
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
      console.error('Failed to download document:', error);
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getStatusBadge = (status) => {
    const colors = {
      pending: 'bg-yellow-100 text-yellow-800',
      verified: 'bg-green-100 text-green-800',
      rejected: 'bg-red-100 text-red-800',
      completed: 'bg-blue-100 text-blue-800'
    };
    return colors[status] || colors.pending;
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Document Management</h1>
        <p className="text-muted-foreground">
          Upload documents to IPFS, manage verification requests, and track document status.
        </p>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="upload">Upload Document</TabsTrigger>
          <TabsTrigger value="documents">My Documents</TabsTrigger>
          {(userRole === 'college' || userRole === 'company' || userRole === 'admin') && (
            <TabsTrigger value="verification">Verification Queue</TabsTrigger>
          )}
        </TabsList>

        <TabsContent value="upload" className="mt-6">
          <DocumentUpload onUploadSuccess={handleUploadSuccess} />
        </TabsContent>

        <TabsContent value="documents" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FileText className="h-5 w-5" />
                My Documents
              </CardTitle>
              <CardDescription>
                View and manage your uploaded documents.
              </CardDescription>
            </CardHeader>
            <CardContent>
              {loading ? (
                <div className="text-center py-8">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
                  <p className="mt-2 text-muted-foreground">Loading documents...</p>
                </div>
              ) : userDocuments.length === 0 ? (
                <div className="text-center py-8">
                  <FileText className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                  <h3 className="text-lg font-medium mb-2">No Documents Yet</h3>
                  <p className="text-muted-foreground mb-4">
                    You haven't uploaded any documents yet. Upload your first document to get started.
                  </p>
                  <Button onClick={() => setActiveTab('upload')}>
                    <Upload className="h-4 w-4 mr-2" />
                    Upload Document
                  </Button>
                </div>
              ) : (
                <div className="space-y-4">
                  {userDocuments.map((doc) => (
                    <div key={doc.document_id} className="flex items-center justify-between p-4 border rounded-lg">
                      <div className="flex-1">
                        <h4 className="font-medium">{doc.title}</h4>
                        <p className="text-sm text-muted-foreground">{doc.description}</p>
                        <div className="flex items-center gap-2 mt-1">
                          <Badge className={getStatusBadge(doc.verification_status)}>
                            {doc.verification_status}
                          </Badge>
                          <span className="text-xs text-muted-foreground">
                            {formatFileSize(doc.file_size)}
                          </span>
                          <span className="text-xs text-muted-foreground">
                            {new Date(doc.upload_timestamp).toLocaleDateString()}
                          </span>
                        </div>
                      </div>
                      <div className="flex gap-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleViewDocument(doc.document_id)}
                        >
                          <Eye className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleDownloadDocument(doc.document_id, doc.original_filename)}
                        >
                          <Download className="h-4 w-4" />
                        </Button>
                        {doc.ipfs_hash && (
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => window.open(`https://ipfs.io/ipfs/${doc.ipfs_hash}`, '_blank')}
                          >
                            <ExternalLink className="h-4 w-4" />
                          </Button>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {(userRole === 'college' || userRole === 'company' || userRole === 'admin') && (
          <TabsContent value="verification" className="mt-6">
            <DocumentVerification userRole={userRole} />
          </TabsContent>
        )}
      </Tabs>
    </div>
  );
};

export default DocumentsPage;