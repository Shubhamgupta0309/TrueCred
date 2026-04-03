import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { FileText, Trash2, Eye, CheckCircle, XCircle, Loader2, TrendingUp } from 'lucide-react';
import axios from 'axios';
import TemplateUpload from './TemplateUpload';

const rawBaseUrl = (import.meta.env.VITE_API_URL || 'http://localhost:5000').replace(/\/$/, '');
const API_BASE_URL = rawBaseUrl.endsWith('/api') ? rawBaseUrl : `${rawBaseUrl}/api`;
const getAuthToken = () => localStorage.getItem('accessToken') || localStorage.getItem('token') || '';

const TemplateManager = ({ organizationId, organizationName, organizationType }) => {
  const [templates, setTemplates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showUpload, setShowUpload] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState(null);
  const [statistics, setStatistics] = useState(null);

  useEffect(() => {
    fetchTemplates();
  }, [organizationId]);

  const fetchTemplates = async () => {
    try {
      setLoading(true);
      const token = getAuthToken();
      const response = await axios.get(
        `${API_BASE_URL}/templates/organization/${organizationId}`,
        {
          headers: { 'Authorization': `Bearer ${token}` }
        }
      );

      if (response.data.success) {
        setTemplates(response.data.data.templates);
      }
    } catch (err) {
      console.error('Fetch templates error:', err);
      setError(err.response?.data?.message || 'Failed to load templates');
    } finally {
      setLoading(false);
    }
  };

  const fetchTemplateStatistics = async (templateId) => {
    try {
      const token = getAuthToken();
      const response = await axios.get(
        `${API_BASE_URL}/templates/${templateId}/statistics`,
        {
          headers: { 'Authorization': `Bearer ${token}` }
        }
      );

      if (response.data.success) {
        setStatistics(response.data.data);
      }
    } catch (err) {
      console.error('Fetch statistics error:', err);
    }
  };

  const handleDeactivate = async (templateId) => {
    if (!confirm('Are you sure you want to deactivate this template?')) {
      return;
    }

    try {
      const token = getAuthToken();
      await axios.post(
        `${API_BASE_URL}/templates/${templateId}/deactivate`,
        {},
        {
          headers: { 'Authorization': `Bearer ${token}` }
        }
      );

      // Refresh templates
      fetchTemplates();
    } catch (err) {
      console.error('Deactivate error:', err);
      alert(err.response?.data?.message || 'Failed to deactivate template');
    }
  };

  const handleViewDetails = async (template) => {
    setSelectedTemplate(template);
    await fetchTemplateStatistics(template.id);
  };

  if (showUpload) {
    return (
      <div className="space-y-4">
        <Button variant="outline" className="border-cyan-500/30 text-cyan-100 bg-cyan-950/20 hover:bg-cyan-900/30" onClick={() => setShowUpload(false)}>
          ← Back to Templates
        </Button>
        <TemplateUpload
          organizationId={organizationId}
          organizationName={organizationName}
          organizationType={organizationType}
        />
      </div>
    );
  }

  if (selectedTemplate) {
    return (
      <div className="space-y-4">
        <Button variant="outline" className="border-cyan-500/30 text-cyan-100 bg-cyan-950/20 hover:bg-cyan-900/30" onClick={() => {
          setSelectedTemplate(null);
          setStatistics(null);
        }}>
          ← Back to Templates
        </Button>
        
        <Card className="bg-cyan-950/30 border-cyan-500/30 text-cyan-100">
          <CardHeader>
            <CardTitle>{selectedTemplate.template_name}</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-cyan-300/70">Type</p>
                <p className="font-medium capitalize">
                  {selectedTemplate.template_type.replace('_', ' ')}
                </p>
              </div>
              <div>
                <p className="text-sm text-cyan-300/70">Status</p>
                <Badge variant={selectedTemplate.is_active ? 'success' : 'secondary'}>
                  {selectedTemplate.is_active ? 'Active' : 'Inactive'}
                </Badge>
              </div>
            </div>

            {statistics && (
              <div className="border-t pt-4 mt-4">
                <h3 className="font-semibold mb-3 flex items-center gap-2">
                  <TrendingUp className="h-4 w-4" />
                  Verification Statistics
                </h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="text-center p-4 bg-slate-900/70 border border-cyan-500/20 rounded-lg">
                    <p className="text-2xl font-bold text-cyan-300">
                      {statistics.total_verifications}
                    </p>
                    <p className="text-xs text-cyan-300/70">Total Verifications</p>
                  </div>
                  <div className="text-center p-4 bg-slate-900/70 border border-cyan-500/20 rounded-lg">
                    <p className="text-2xl font-bold text-cyan-300">
                      {statistics.successful_matches}
                    </p>
                    <p className="text-xs text-cyan-300/70">Successful</p>
                  </div>
                  <div className="text-center p-4 bg-slate-900/70 border border-cyan-500/20 rounded-lg">
                    <p className="text-2xl font-bold text-cyan-300">
                      {statistics.success_rate}%
                    </p>
                    <p className="text-xs text-cyan-300/70">Success Rate</p>
                  </div>
                  <div className="text-center p-4 bg-slate-900/70 border border-cyan-500/20 rounded-lg">
                    <p className="text-2xl font-bold text-cyan-300">
                      {statistics.average_confidence}%
                    </p>
                    <p className="text-xs text-cyan-300/70">Avg Confidence</p>
                  </div>
                </div>
              </div>
            )}

            {selectedTemplate.required_fields && selectedTemplate.required_fields.length > 0 && (
              <div>
                <p className="text-sm font-medium text-cyan-200 mb-2">Required Fields:</p>
                <div className="flex flex-wrap gap-2">
                  {selectedTemplate.required_fields.map((field, idx) => (
                    <Badge key={idx} variant="outline">{field}</Badge>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-cyan-100">Certificate Templates</h2>
        <Button onClick={() => setShowUpload(true)} className="bg-cyan-600 text-slate-950 hover:bg-cyan-500">
          <FileText className="mr-2 h-4 w-4" />
          Upload New Template
        </Button>
      </div>

      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {loading ? (
        <div className="flex justify-center items-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-cyan-300" />
        </div>
      ) : templates.length === 0 ? (
        <Card className="bg-cyan-950/30 border-cyan-500/30 text-cyan-100">
          <CardContent className="py-12 text-center">
            <FileText className="h-12 w-12 mx-auto text-cyan-300 mb-4" />
            <p className="text-cyan-300/70 mb-4">No templates uploaded yet</p>
            <Button onClick={() => setShowUpload(true)} className="bg-cyan-600 text-slate-950 hover:bg-cyan-500">
              Upload Your First Template
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {templates.map((template) => (
            <Card key={template.id} className="bg-cyan-950/30 border-cyan-500/30 text-cyan-100 hover:shadow-lg transition">
              <CardContent className="p-6">
                <div className="flex justify-between items-start mb-4">
                  <div className="flex-1">
                    <h3 className="font-semibold text-lg mb-1">
                      {template.template_name}
                    </h3>
                    <p className="text-sm text-cyan-300/70 capitalize">
                      {template.template_type.replace('_', ' ')}
                    </p>
                  </div>
                  <Badge variant={template.is_active ? 'success' : 'secondary'}>
                    {template.is_active ? (
                      <><CheckCircle className="h-3 w-3 mr-1" /> Active</>
                    ) : (
                      <><XCircle className="h-3 w-3 mr-1" /> Inactive</>
                    )}
                  </Badge>
                </div>

                <div className="space-y-2 text-sm mb-4">
                  <div className="flex justify-between">
                    <span className="text-cyan-300/70">Verifications:</span>
                    <span className="font-medium">{template.total_verifications}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-cyan-300/70">Success Rate:</span>
                    <span className="font-medium">
                      {template.total_verifications > 0
                        ? Math.round((template.successful_matches / template.total_verifications) * 100)
                        : 0}%
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-cyan-300/70">Avg Confidence:</span>
                    <span className="font-medium">{template.average_confidence}%</span>
                  </div>
                </div>

                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                      className="flex-1 border-cyan-500/30 text-cyan-100 bg-cyan-950/20 hover:bg-cyan-900/30"
                    onClick={() => handleViewDetails(template)}
                  >
                    <Eye className="h-4 w-4 mr-1" />
                    View
                  </Button>
                  {template.is_active && (
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleDeactivate(template.id)}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
};

export default TemplateManager;
