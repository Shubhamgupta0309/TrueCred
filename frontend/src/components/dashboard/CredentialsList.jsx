import React from 'react';
import { motion } from 'framer-motion';
import StatusBadge from './StatusBadge';
import { FileText, Calendar, Eye } from 'lucide-react';

export default function CredentialsList({ credentials }) {
  return (
    <div className="bg-white rounded-2xl shadow-lg shadow-purple-500/10 p-6">
      <h3 className="text-lg font-bold text-gray-800 mb-4 flex items-center gap-2">
        <FileText className="w-5 h-5 text-purple-600" />
        My Credentials
      </h3>
      <div className="space-y-4 max-h-80 overflow-y-auto pr-2">
        {credentials.map((cred, index) => (
          <motion.div
            key={cred.id}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.3, delay: index * 0.1 }}
            className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 hover:shadow-md transition-all duration-200"
          >
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2">
              <div>
                <p className="font-semibold text-gray-800">{cred.title}</p>
                <p className="text-sm text-gray-500 flex items-center gap-2 mt-1">
                  <Calendar className="w-4 h-4" />
                  Submitted on {cred.date}
                </p>
              </div>
              <div className="flex items-center gap-4 mt-2 sm:mt-0">
                <StatusBadge status={cred.status} />
                <motion.button
                  whileHover={{ scale: 1.1 }}
                  whileTap={{ scale: 0.9 }}
                  className="p-2 text-gray-500 hover:text-purple-600 hover:bg-purple-100 rounded-full"
                  title="View Details"
                >
                  <Eye className="w-5 h-5" />
                </motion.button>
              </div>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
}