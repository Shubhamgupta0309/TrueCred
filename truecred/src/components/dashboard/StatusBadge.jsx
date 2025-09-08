import React from 'react';
import { motion } from 'framer-motion';
import { CheckCircle2, Clock, XCircle } from 'lucide-react';

const statusConfig = {
  Verified: {
    icon: <CheckCircle2 className="w-4 h-4" />,
    style: "bg-green-100 text-green-700 border-green-200",
  },
  Pending: {
    icon: <Clock className="w-4 h-4" />,
    style: "bg-yellow-100 text-yellow-700 border-yellow-200",
  },
  Rejected: {
    icon: <XCircle className="w-4 h-4" />,
    style: "bg-red-100 text-red-700 border-red-200",
  },
};

export default function StatusBadge({ status }) {
  const config = statusConfig[status] || statusConfig.Pending;

  return (
    <motion.div
      whileHover={{ scale: 1.05 }}
      className={`inline-flex items-center gap-2 px-3 py-1 rounded-full text-sm font-medium border ${config.style}`}
    >
      {config.icon}
      <span>{status}</span>
    </motion.div>
  );
}