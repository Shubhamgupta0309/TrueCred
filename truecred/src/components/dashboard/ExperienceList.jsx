import React from 'react';
import { motion } from 'framer-motion';
import { Briefcase, Edit, Eye } from 'lucide-react';

export default function ExperienceList({ experiences }) {
  return (
    <div className="bg-white rounded-2xl shadow-lg shadow-purple-500/10 p-6">
      <h3 className="text-lg font-bold text-gray-800 mb-4 flex items-center gap-2">
        <Briefcase className="w-5 h-5 text-purple-600" />
        My Experiences
      </h3>
      <div className="space-y-4 max-h-80 overflow-y-auto pr-2">
        {experiences.map((exp, index) => (
          <motion.div
            key={exp.id}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.3, delay: index * 0.1 }}
            className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 hover:shadow-md transition-all duration-200"
          >
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2">
              <div>
                <p className="font-semibold text-gray-800">{exp.title}</p>
                <p className="text-sm text-gray-500">{exp.company} &bull; {exp.duration}</p>
              </div>
              <div className="flex items-center gap-2 mt-2 sm:mt-0">
                <motion.button
                  whileHover={{ scale: 1.1 }}
                  whileTap={{ scale: 0.9 }}
                  className="p-2 text-gray-500 hover:text-blue-600 hover:bg-blue-100 rounded-full"
                  title="View Details"
                >
                  <Eye className="w-5 h-5" />
                </motion.button>
                <motion.button
                  whileHover={{ scale: 1.1 }}
                  whileTap={{ scale: 0.9 }}
                  className="p-2 text-gray-500 hover:text-green-600 hover:bg-green-100 rounded-full"
                  title="Edit"
                >
                  <Edit className="w-5 h-5" />
                </motion.button>
              </div>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
}