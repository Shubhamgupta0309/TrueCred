import React from 'react';
import { motion } from 'framer-motion';
import StatusBadge from '../dashboard/StatusBadge';
import { History, Calendar } from 'lucide-react';

export default function ExperienceHistory({ history }) {
  return (
    <div className="bg-cyan-950/30 border border-cyan-500/30 rounded-2xl shadow-lg shadow-cyan-500/10 p-6">
      <h3 className="text-lg font-bold text-cyan-100 mb-4 flex items-center gap-2">
        <History className="w-5 h-5 text-cyan-400" />
        Experience Verification History
      </h3>
      <div className="space-y-3 max-h-72 overflow-y-auto pr-2">
        {history.slice().reverse().map((item, index) => (
          <motion.div
            key={item.id}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.3, delay: index * 0.1 }}
            className="border border-cyan-500/20 bg-cyan-950/20 rounded-lg p-3"
          >
            <div className="flex justify-between items-center">
              <div>
                <p className="font-medium text-sm text-cyan-100">{item.experienceTitle}</p>
                <p className="text-xs text-cyan-300">Student: {item.studentName}</p>
              </div>
              <div className="text-right">
                <StatusBadge status={item.status} />
                <p className="text-xs text-cyan-300/70 mt-1 flex items-center justify-end gap-1">
                    <Calendar className="w-3 h-3"/> {item.actionDate}
                </p>
              </div>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
}