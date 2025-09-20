import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Plus, Edit, Trash2, Eye, EyeOff, Save, X, MessageSquare, Bell, Mail } from 'lucide-react';
import { useAuth } from '../context/AuthContext.jsx';
import { api } from '../services/api';

export default function NotificationTemplates() {
  const { user } = useAuth();
  const [templates, setTemplates] = useState([]);
  const [templateTypes, setTemplateTypes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [editingTemplate, setEditingTemplate] = useState(null);
  const [previewTemplate, setPreviewTemplate] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    type: '',
    title_template: '',
    message_template: '',
    channels: ['websocket'],
    variables: [],
    is_active: true
  });
  const [previewVariables, setPreviewVariables] = useState({});

  // Available channels
  const availableChannels = [
    { id: 'websocket', label: 'Real-time', icon: MessageSquare },
    { id: 'push', label: 'Push Notification', icon: Bell },
    { id: 'email', label: 'Email', icon: Mail }
  ];

  // Load templates and types
  useEffect(() => {
    loadTemplates();
    loadTemplateTypes();
  }, []);

  const loadTemplates = async () => {
    try {
      const response = await api.get('/api/notification-templates');
      setTemplates(response.data.data);
    } catch (error) {
      console.error('Error loading templates:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadTemplateTypes = async () => {
    try {
      const response = await api.get('/api/notification-templates/types');
      setTemplateTypes(response.data.data);
    } catch (error) {
      console.error('Error loading template types:', error);
    }
  };

  // Handle form input changes
  const handleInputChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  // Handle channel toggle
  const handleChannelToggle = (channelId) => {
    setFormData(prev => ({
      ...prev,
      channels: prev.channels.includes(channelId)
        ? prev.channels.filter(c => c !== channelId)
        : [...prev.channels, channelId]
    }));
  };

  // Handle variable input
  const handleVariableChange = (index, value) => {
    const newVariables = [...formData.variables];
    newVariables[index] = value;
    setFormData(prev => ({ ...prev, variables: newVariables }));
  };

  // Add variable
  const addVariable = () => {
    setFormData(prev => ({ ...prev, variables: [...prev.variables, ''] }));
  };

  // Remove variable
  const removeVariable = (index) => {
    setFormData(prev => ({
      ...prev,
      variables: prev.variables.filter((_, i) => i !== index)
    }));
  };

  // Create template
  const createTemplate = async () => {
    try {
      const response = await api.post('/api/notification-templates', formData);
      setTemplates(prev => [...prev, response.data.data]);
      resetForm();
      setShowCreateForm(false);
    } catch (error) {
      console.error('Error creating template:', error);
    }
  };

  // Update template
  const updateTemplate = async () => {
    try {
      const response = await api.put(`/api/notification-templates/${editingTemplate.id}`, formData);
      setTemplates(prev => prev.map(t => t.id === editingTemplate.id ? response.data.data : t));
      resetForm();
      setEditingTemplate(null);
    } catch (error) {
      console.error('Error updating template:', error);
    }
  };

  // Delete template
  const deleteTemplate = async (templateId) => {
    if (!confirm('Are you sure you want to delete this template?')) return;

    try {
      await api.delete(`/api/notification-templates/${templateId}`);
      setTemplates(prev => prev.filter(t => t.id !== templateId));
    } catch (error) {
      console.error('Error deleting template:', error);
    }
  };

  // Toggle template active status
  const toggleTemplateStatus = async (templateId, currentStatus) => {
    try {
      await api.put(`/api/notification-templates/${templateId}`, {
        is_active: !currentStatus
      });
      setTemplates(prev => prev.map(t =>
        t.id === templateId ? { ...t, is_active: !currentStatus } : t
      ));
    } catch (error) {
      console.error('Error toggling template status:', error);
    }
  };

  // Preview template
  const previewTemplateRender = async (template) => {
    try {
      const response = await api.post(`/api/notification-templates/${template.type}/render`, {
        variables: previewVariables
      });
      setPreviewTemplate({
        ...template,
        rendered: response.data.data
      });
    } catch (error) {
      console.error('Error previewing template:', error);
    }
  };

  // Reset form
  const resetForm = () => {
    setFormData({
      name: '',
      type: '',
      title_template: '',
      message_template: '',
      channels: ['websocket'],
      variables: [],
      is_active: true
    });
    setPreviewVariables({});
  };

  // Start editing
  const startEditing = (template) => {
    setFormData({
      name: template.name,
      type: template.type,
      title_template: template.title_template,
      message_template: template.message_template,
      channels: template.channels,
      variables: template.variables || [],
      is_active: template.is_active
    });
    setEditingTemplate(template);
    setShowCreateForm(false);
  };

  // Cancel editing
  const cancelEditing = () => {
    resetForm();
    setEditingTemplate(null);
    setShowCreateForm(false);
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-6xl mx-auto px-4 py-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex justify-between items-center mb-8"
        >
          <div>
            <h1 className="text-3xl font-bold text-gray-800 mb-2">Notification Templates</h1>
            <p className="text-gray-600">Manage notification templates for different event types</p>
          </div>
          <button
            onClick={() => setShowCreateForm(true)}
            className="flex items-center gap-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
          >
            <Plus className="w-4 h-4" />
            Create Template
          </button>
        </motion.div>

        {/* Templates Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          {templates.map((template) => (
            <motion.div
              key={template.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow"
            >
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="text-lg font-semibold text-gray-800 mb-1">{template.name}</h3>
                  <div className="flex items-center gap-2">
                    <span className={`px-2 py-1 rounded-full text-xs ${
                      template.is_default
                        ? 'bg-blue-100 text-blue-800'
                        : 'bg-green-100 text-green-800'
                    }`}>
                      {template.is_default ? 'Default' : 'Custom'}
                    </span>
                    <span className={`px-2 py-1 rounded-full text-xs ${
                      template.is_active
                        ? 'bg-green-100 text-green-800'
                        : 'bg-gray-100 text-gray-800'
                    }`}>
                      {template.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </div>
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => previewTemplateRender(template)}
                    className="p-1 text-gray-400 hover:text-gray-600"
                    title="Preview"
                  >
                    <Eye className="w-4 h-4" />
                  </button>
                  {!template.is_default && (
                    <>
                      <button
                        onClick={() => startEditing(template)}
                        className="p-1 text-gray-400 hover:text-gray-600"
                        title="Edit"
                      >
                        <Edit className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => toggleTemplateStatus(template.id, template.is_active)}
                        className={`p-1 ${template.is_active ? 'text-green-600' : 'text-gray-400'}`}
                        title={template.is_active ? 'Deactivate' : 'Activate'}
                      >
                        {template.is_active ? <Eye className="w-4 h-4" /> : <EyeOff className="w-4 h-4" />}
                      </button>
                      <button
                        onClick={() => deleteTemplate(template.id)}
                        className="p-1 text-gray-400 hover:text-red-600"
                        title="Delete"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </>
                  )}
                </div>
              </div>

              <div className="mb-4">
                <p className="text-sm text-gray-600 mb-2">Type: {template.type}</p>
                <div className="flex flex-wrap gap-1 mb-2">
                  {template.channels.map(channel => {
                    const channelInfo = availableChannels.find(c => c.id === channel);
                    const Icon = channelInfo?.icon || Bell;
                    return (
                      <span key={channel} className="flex items-center gap-1 px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs">
                        <Icon className="w-3 h-3" />
                        {channelInfo?.label || channel}
                      </span>
                    );
                  })}
                </div>
              </div>

              <div className="text-xs text-gray-500">
                <div className="truncate">Title: {template.title_template}</div>
                <div className="truncate">Message: {template.message_template}</div>
              </div>
            </motion.div>
          ))}
        </div>

        {/* Create/Edit Form */}
        {(showCreateForm || editingTemplate) && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-white rounded-lg shadow-lg p-6 mb-8"
          >
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-xl font-bold text-gray-800">
                {editingTemplate ? 'Edit Template' : 'Create New Template'}
              </h2>
              <button
                onClick={cancelEditing}
                className="p-1 text-gray-400 hover:text-gray-600"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Template Name</label>
                  <input
                    type="text"
                    value={formData.name}
                    onChange={(e) => handleInputChange('name', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                    placeholder="e.g., Custom Credential Issued"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Event Type</label>
                  <select
                    value={formData.type}
                    onChange={(e) => handleInputChange('type', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                  >
                    <option value="">Select event type...</option>
                    {templateTypes.map(type => (
                      <option key={type.type} value={type.type}>{type.name}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Title Template</label>
                  <input
                    type="text"
                    value={formData.title_template}
                    onChange={(e) => handleInputChange('title_template', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                    placeholder="e.g., New Credential: {credential_title}"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Message Template</label>
                  <textarea
                    value={formData.message_template}
                    onChange={(e) => handleInputChange('message_template', e.target.value)}
                    rows={3}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                    placeholder="e.g., Congratulations! Your credential {credential_title} has been issued."
                  />
                </div>
              </div>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Delivery Channels</label>
                  <div className="space-y-2">
                    {availableChannels.map(channel => {
                      const Icon = channel.icon;
                      return (
                        <label key={channel.id} className="flex items-center gap-2">
                          <input
                            type="checkbox"
                            checked={formData.channels.includes(channel.id)}
                            onChange={() => handleChannelToggle(channel.id)}
                            className="w-4 h-4 text-purple-600 rounded focus:ring-purple-500"
                          />
                          <Icon className="w-4 h-4 text-gray-600" />
                          <span className="text-sm text-gray-700">{channel.label}</span>
                        </label>
                      );
                    })}
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Template Variables</label>
                  <div className="space-y-2">
                    {formData.variables.map((variable, index) => (
                      <div key={index} className="flex gap-2">
                        <input
                          type="text"
                          value={variable}
                          onChange={(e) => handleVariableChange(index, e.target.value)}
                          className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                          placeholder="variable_name"
                        />
                        <button
                          onClick={() => removeVariable(index)}
                          className="p-2 text-red-600 hover:text-red-800"
                        >
                          <X className="w-4 h-4" />
                        </button>
                      </div>
                    ))}
                    <button
                      onClick={addVariable}
                      className="flex items-center gap-2 px-3 py-2 text-purple-600 hover:text-purple-800 text-sm"
                    >
                      <Plus className="w-4 h-4" />
                      Add Variable
                    </button>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={formData.is_active}
                    onChange={(e) => handleInputChange('is_active', e.target.checked)}
                    className="w-4 h-4 text-purple-600 rounded focus:ring-purple-500"
                  />
                  <label className="text-sm font-medium text-gray-700">Active</label>
                </div>
              </div>
            </div>

            <div className="flex justify-end gap-4 mt-6">
              <button
                onClick={cancelEditing}
                className="px-4 py-2 text-gray-600 hover:text-gray-800"
              >
                Cancel
              </button>
              <button
                onClick={editingTemplate ? updateTemplate : createTemplate}
                className="flex items-center gap-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
              >
                <Save className="w-4 h-4" />
                {editingTemplate ? 'Update' : 'Create'} Template
              </button>
            </div>
          </motion.div>
        )}

        {/* Preview Modal */}
        {previewTemplate && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"
          >
            <motion.div
              initial={{ scale: 0.9 }}
              animate={{ scale: 1 }}
              className="bg-white rounded-lg shadow-xl max-w-md w-full p-6"
            >
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-bold text-gray-800">Template Preview</h3>
                <button
                  onClick={() => setPreviewTemplate(null)}
                  className="p-1 text-gray-400 hover:text-gray-600"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Variables</label>
                  <div className="space-y-2">
                    {(previewTemplate.variables || []).map(variable => (
                      <div key={variable} className="flex gap-2">
                        <span className="text-sm text-gray-600 w-20">{variable}:</span>
                        <input
                          type="text"
                          value={previewVariables[variable] || ''}
                          onChange={(e) => setPreviewVariables(prev => ({
                            ...prev,
                            [variable]: e.target.value
                          }))}
                          className="flex-1 px-2 py-1 border border-gray-300 rounded text-sm"
                          placeholder={`Enter ${variable}`}
                        />
                      </div>
                    ))}
                  </div>
                  <button
                    onClick={() => previewTemplateRender(previewTemplate)}
                    className="mt-2 px-3 py-1 bg-purple-600 text-white rounded text-sm hover:bg-purple-700"
                  >
                    Preview
                  </button>
                </div>

                {previewTemplate.rendered && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Rendered Output</label>
                    <div className="bg-gray-50 p-3 rounded">
                      <div className="font-semibold text-gray-800 mb-1">
                        {previewTemplate.rendered.title}
                      </div>
                      <div className="text-sm text-gray-600">
                        {previewTemplate.rendered.message}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </motion.div>
          </motion.div>
        )}
      </div>
    </div>
  );
}