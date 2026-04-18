import React from 'react';
import { motion } from 'framer-motion';
import { LogOut, Mail } from 'lucide-react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext.jsx';

export default function DashboardHeader({ user }) {
  const navigate = useNavigate();
  const { logout } = useAuth();

  const handleLogout = async () => {
    await logout();
    navigate('/auth');
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="bg-cyan-950/30 border border-cyan-500/30 rounded-2xl shadow-lg shadow-cyan-500/10 p-4 mb-8"
    >
      <div className="flex flex-col md:flex-row items-center justify-between gap-4">
        {/* User Info (non-clickable) */}
        <div className="flex items-center gap-4">
          <div className="w-16 h-16 bg-gradient-to-br from-cyan-500 to-cyan-700 rounded-full flex items-center justify-center text-white text-2xl font-bold select-none">
            {user.name.charAt(0)}
          </div>
          <div>
            <div className="text-xl font-bold text-cyan-100 block select-none">{user.name}</div>
            <p className="text-sm text-cyan-300 flex items-center gap-2">
              <Mail className="w-4 h-4" />
              {user.email}
            </p>
            <div className="mt-1">
              <div className="flex items-center gap-2">
                <span className="bg-cyan-900/40 text-cyan-200 text-xs font-semibold px-2 py-1 rounded-full">{user.role}</span>
                {user.profile_completed ? (
                  <span className="bg-green-900/30 text-green-300 text-xs font-semibold px-2 py-1 rounded-full">Profile complete</span>
                ) : (
                  <span className="bg-amber-900/30 text-amber-300 text-xs font-semibold px-2 py-1 rounded-full">Complete profile</span>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Actions */}
        <div className="flex flex-col sm:flex-row items-center gap-4 w-full md:w-auto">
          <motion.button onClick={handleLogout}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="w-full sm:w-auto flex items-center justify-center gap-2 px-4 py-2 bg-red-500 text-white rounded-lg font-medium hover:bg-red-600 transition-colors duration-200 shadow-md hover:shadow-lg"
          >
            <LogOut className="w-5 h-5" />
            <span>Logout</span>
          </motion.button>
        </div>
      </div>
    </motion.div>
  );
}