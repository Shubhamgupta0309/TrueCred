import React from 'react';
import { motion } from 'framer-motion';
import { Upload, PlusCircle } from 'lucide-react';

export default function ActionButtons() {
  return (
    <div className="bg-white rounded-2xl shadow-lg shadow-purple-500/10 p-6 h-full flex flex-col justify-center">
      <h3 className="text-lg font-bold text-gray-800 mb-4">Quick Actions</h3>
      <div className="space-y-4">
        <motion.button
          whileHover={{ scale: 1.03 }}
          whileTap={{ scale: 0.97 }}
          className="w-full flex items-center justify-center gap-3 px-4 py-3 bg-gradient-to-r from-purple-600 to-purple-700 text-white rounded-lg font-semibold hover:from-purple-700 hover:to-purple-800 focus:ring-4 focus:ring-purple-300 focus:outline-none transition-all duration-200 shadow-lg hover:shadow-purple-500/30"
        >
          <Upload className="w-5 h-5" />
          <span>Upload New Credential</span>
        </motion.button>
        <motion.button
          whileHover={{ scale: 1.03 }}
          whileTap={{ scale: 0.97 }}
          className="w-full flex items-center justify-center gap-3 px-4 py-3 bg-gradient-to-r from-indigo-500 to-blue-500 text-white rounded-lg font-semibold hover:from-indigo-600 hover:to-blue-600 focus:ring-4 focus:ring-indigo-300 focus:outline-none transition-all duration-200 shadow-lg hover:shadow-indigo-500/30"
        >
          <PlusCircle className="w-5 h-5" />
          <span>Add New Experience</span>
        </motion.button>
      </div>
    </div>
  );
}