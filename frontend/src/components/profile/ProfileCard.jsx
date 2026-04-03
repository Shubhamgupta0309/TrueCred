import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

export default function ProfileCard({ student, currentUser, onEditRequest }) {
  const { isAuthenticated, loading } = useAuth();
  const navigate = useNavigate();

  if (!student) {
    return (
      <div className="bg-cyan-950/30 border border-cyan-500/30 p-4 rounded-lg shadow">
        <p className="text-cyan-200">No profile selected</p>
      </div>
    );
  }

  const isSelf = currentUser && (String(currentUser.id) === String(student.id) || String(currentUser.truecred_id) === String(student.truecred_id));

  const handleEditProfile = () => {
    if (isAuthenticated && !loading) {
      navigate('/profile');
    }
  };

  return (
    <div className="bg-cyan-950/30 border border-cyan-500/30 p-6 rounded-lg shadow">
      <div className="flex items-start gap-4">
        <div className="w-16 h-16 rounded-full bg-cyan-600 text-slate-950 flex items-center justify-center text-2xl font-bold">{(student.name || student.username || 'U').charAt(0)}</div>
        <div className="flex-1">
          <h3 className="text-xl font-semibold text-cyan-100">{student.name || student.username}</h3>
          <p className="text-sm text-cyan-300">{student.email}</p>
          <p className="text-xs font-mono text-cyan-300 mt-1">TrueCred ID: {student.truecred_id}</p>
        </div>
        <div>
          {isSelf ? (
            <button 
              onClick={handleEditProfile}
              disabled={loading || !isAuthenticated}
              className="px-4 py-2 bg-cyan-600 text-slate-950 rounded-lg text-sm disabled:opacity-50 disabled:cursor-not-allowed hover:bg-cyan-500"
            >
              {loading ? 'Loading...' : 'Edit profile'}
            </button>
          ) : (
            <button onClick={() => onEditRequest && onEditRequest(student)} className="px-4 py-2 bg-cyan-950/20 border border-cyan-500/30 text-cyan-100 rounded-lg text-sm hover:bg-cyan-900/30">Request edit</button>
          )}
        </div>
      </div>

      {student.education && student.education.length > 0 && (
        <div className="mt-4">
          <h4 className="text-sm font-semibold text-cyan-200">Education</h4>
          <ul className="mt-2 space-y-2">
            {student.education.map((edu, idx) => (
              <li key={idx} className="text-sm text-cyan-100">
                <div className="font-medium">{edu.degree} — {edu.institution}</div>
                <div className="text-xs text-cyan-300/70">{edu.start_date} {edu.current ? ' - Present' : ` - ${edu.end_date}`}</div>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
