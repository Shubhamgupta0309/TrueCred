import React from 'react';
import { Link } from 'react-router-dom';

export default function ProfileCard({ student, currentUser, onEditRequest }) {
  if (!student) {
    return (
      <div className="bg-white p-4 rounded-lg shadow">
        <p className="text-gray-500">No profile selected</p>
      </div>
    );
  }

  const isSelf = currentUser && (String(currentUser.id) === String(student.id) || String(currentUser.truecred_id) === String(student.truecred_id));

  return (
    <div className="bg-white p-6 rounded-lg shadow">
      <div className="flex items-start gap-4">
        <div className="w-16 h-16 rounded-full bg-blue-600 text-white flex items-center justify-center text-2xl font-bold">{(student.name || student.username || 'U').charAt(0)}</div>
        <div className="flex-1">
          <h3 className="text-xl font-semibold">{student.name || student.username}</h3>
          <p className="text-sm text-gray-600">{student.email}</p>
          <p className="text-xs font-mono text-blue-700 mt-1">TrueCred ID: {student.truecred_id}</p>
        </div>
        <div>
          {isSelf ? (
            <Link to="/profile" className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm">Edit profile</Link>
          ) : (
            <button onClick={() => onEditRequest && onEditRequest(student)} className="px-4 py-2 bg-green-600 text-white rounded-lg text-sm">Request edit</button>
          )}
        </div>
      </div>

      {student.education && student.education.length > 0 && (
        <div className="mt-4">
          <h4 className="text-sm font-semibold text-gray-700">Education</h4>
          <ul className="mt-2 space-y-2">
            {student.education.map((edu, idx) => (
              <li key={idx} className="text-sm text-gray-700">
                <div className="font-medium">{edu.degree} — {edu.institution}</div>
                <div className="text-xs text-gray-500">{edu.start_date} {edu.current ? ' - Present' : ` - ${edu.end_date}`}</div>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
