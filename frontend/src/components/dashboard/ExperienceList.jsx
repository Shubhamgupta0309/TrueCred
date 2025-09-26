import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Briefcase, Edit, Eye, CheckCircle, Clock, XCircle } from 'lucide-react';

export default function ExperienceList({ experiences }) {
  const [selectedExperience, setSelectedExperience] = useState(null);

  // Filter to show only verified experiences
  const verifiedExperiences = experiences.filter(exp => 
    exp.is_verified === true || exp.verification_status === 'verified'
  );

  const getStatusIcon = (exp) => {
    if (exp.is_verified) {
      return <CheckCircle className="w-5 h-5 text-green-600" />;
    } else if (exp.pending_verification) {
      return <Clock className="w-5 h-5 text-yellow-600" />;
    } else if (exp.verification_status === 'rejected') {
      return <XCircle className="w-5 h-5 text-red-600" />;
    }
    return null;
  };

  const getStatusText = (exp) => {
    if (exp.is_verified) {
      return 'Verified';
    } else if (exp.pending_verification) {
      return 'Pending Verification';
    } else if (exp.verification_status === 'rejected') {
      return 'Rejected';
    }
    return 'Not Verified';
  };

  const getStatusColor = (exp) => {
    if (exp.is_verified) {
      return 'text-green-600 bg-green-100';
    } else if (exp.pending_verification) {
      return 'text-yellow-600 bg-yellow-100';
    } else if (exp.verification_status === 'rejected') {
      return 'text-red-600 bg-red-100';
    }
    return 'text-gray-600 bg-gray-100';
  };

  return (
    <div className="bg-white rounded-2xl shadow-lg shadow-purple-500/10 p-6">
      <h3 className="text-lg font-bold text-gray-800 mb-4 flex items-center gap-2">
        <Briefcase className="w-5 h-5 text-purple-600" />
        My Experiences ({verifiedExperiences.length})
      </h3>
      <div className="space-y-4 max-h-80 overflow-y-auto pr-2">
        {verifiedExperiences.length === 0 ? (
          <div className="text-gray-500 text-center py-8">
            <CheckCircle className="w-12 h-12 mx-auto mb-4 text-gray-300" />
            <p>No verified experiences yet.</p>
            <p className="text-sm mt-2">Your approved experiences will appear here.</p>
          </div>
        ) : (
          verifiedExperiences.map((exp, index) => (
            <motion.div
              key={exp.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.3, delay: index * 0.1 }}
              className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 hover:shadow-md transition-all duration-200 cursor-pointer"
              onClick={() => setSelectedExperience(exp)}
            >
              <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <CheckCircle className="w-5 h-5 text-green-600" />
                    <p className="font-semibold text-gray-800">{exp.title}</p>
                  </div>
                  <p className="text-sm text-gray-500">{exp.organization} &bull; {exp.type}</p>
                  <p className="text-sm text-green-600 font-medium">Verified</p>
                </div>
                <div className="flex items-center gap-2 mt-2 sm:mt-0">
                  <motion.button
                    whileHover={{ scale: 1.1 }}
                    whileTap={{ scale: 0.9 }}
                    className="p-2 text-gray-500 hover:text-blue-600 hover:bg-blue-100 rounded-full"
                    title="View Details"
                    onClick={(e) => {
                      e.stopPropagation();
                      setSelectedExperience(exp);
                    }}
                  >
                    <Eye className="w-5 h-5" />
                  </motion.button>
                </div>
              </div>
            </motion.div>
          ))
        )}
      </div>

      {/* Experience Details Modal */}
      {selectedExperience && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[80vh] overflow-y-auto"
          >
            <div className="p-6">
              <div className="flex justify-between items-start mb-4">
                <h2 className="text-2xl font-bold text-gray-800">{selectedExperience.title}</h2>
                <button
                  onClick={() => setSelectedExperience(null)}
                  className="text-gray-500 hover:text-gray-700 text-2xl"
                >
                  ×
                </button>
              </div>

              <div className="space-y-4">
                <div className="flex items-center gap-2">
                  <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(selectedExperience)}`}>
                    {getStatusText(selectedExperience)}
                  </span>
                  {getStatusIcon(selectedExperience)}
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <h3 className="font-semibold text-gray-700 mb-2">Basic Information</h3>
                    <div className="space-y-2 text-sm">
                      <p><span className="font-medium">Organization:</span> {selectedExperience.organization}</p>
                      <p><span className="font-medium">Type:</span> {selectedExperience.type}</p>
                      <p><span className="font-medium">Location:</span> {selectedExperience.location || 'Not specified'}</p>
                      <p><span className="font-medium">Current:</span> {selectedExperience.is_current ? 'Yes' : 'No'}</p>
                    </div>
                  </div>

                  <div>
                    <h3 className="font-semibold text-gray-700 mb-2">Dates</h3>
                    <div className="space-y-2 text-sm">
                      <p><span className="font-medium">Start Date:</span> {selectedExperience.start_date ? new Date(selectedExperience.start_date).toLocaleDateString() : 'Not specified'}</p>
                      <p><span className="font-medium">End Date:</span> {selectedExperience.end_date ? new Date(selectedExperience.end_date).toLocaleDateString() : 'Present'}</p>
                    </div>
                  </div>
                </div>

                {selectedExperience.description && (
                  <div>
                    <h3 className="font-semibold text-gray-700 mb-2">Description</h3>
                    <p className="text-sm text-gray-600 bg-gray-50 p-3 rounded-lg">{selectedExperience.description}</p>
                  </div>
                )}

                {selectedExperience.skills && selectedExperience.skills.length > 0 && (
                  <div>
                    <h3 className="font-semibold text-gray-700 mb-2">Skills</h3>
                    <div className="flex flex-wrap gap-2">
                      {selectedExperience.skills.map((skill, idx) => (
                        <span key={idx} className="px-2 py-1 bg-purple-100 text-purple-700 rounded-full text-xs">
                          {skill}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {selectedExperience.is_verified && selectedExperience.verified_at && (
                  <div>
                    <h3 className="font-semibold text-gray-700 mb-2">Verification Details</h3>
                    <div className="space-y-2 text-sm">
                      <p><span className="font-medium">Verified At:</span> {new Date(selectedExperience.verified_at).toLocaleString()}</p>
                      {selectedExperience.verified_by && (
                        <p><span className="font-medium">Verified By:</span> {selectedExperience.verified_by}</p>
                      )}
                    </div>
                  </div>
                )}

                {selectedExperience.document_hashes && Object.keys(selectedExperience.document_hashes).length > 0 && (
                  <div>
                    <h3 className="font-semibold text-gray-700 mb-2">Documents</h3>
                    <div className="space-y-2">
                      {Object.entries(selectedExperience.document_hashes).map(([filename, hash]) => (
                        <div key={hash} className="flex items-center gap-2 p-2 bg-gray-50 rounded-lg">
                          <span className="text-sm font-medium">{filename}</span>
                          <a
                            href={`http://localhost:8080/ipfs/${hash}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-blue-600 hover:text-blue-800 text-sm underline"
                          >
                            View Document
                          </a>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {selectedExperience.credentials && selectedExperience.credentials.length > 0 && (
                  <div>
                    <h3 className="font-semibold text-gray-700 mb-2">Related Credentials</h3>
                    <div className="space-y-2">
                      {selectedExperience.credentials.map((credId) => (
                        <div key={credId} className="p-2 bg-blue-50 rounded-lg text-sm">
                          Credential ID: {credId}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </motion.div>
        </div>
      )}
    </div>
  );
}