import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { api } from '../services/api';
import { useAuth } from '../context/AuthContext';
import ProfileCompletion from '../components/profile/ProfileCompletion';

export default function StudentProfile() {
  const { truecredId } = useParams();
  const { user: currentUser } = useAuth();
  const [student, setStudent] = useState(null);
  const [editMode, setEditMode] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let mounted = true;
    const fetchStudent = async () => {
      setLoading(true);
      try {
        let resp;
        // If viewing own profile, fetch via profile endpoint to ensure editable fields
        const isSelf = currentUser && (String(currentUser.id) === String(truecredId) || String(currentUser.truecred_id) === String(truecredId));
        if (isSelf) {
          resp = await api.get('/api/user/profile');
          if (mounted) {
            if (resp.data && resp.data.success) {
              setStudent(resp.data.user || resp.data.user || resp.data);
              setError(null);
            } else {
              setError(resp.data?.message || 'Failed to load student');
            }
          }
        } else {
          resp = await api.get(`/api/organization/student/${truecredId}`);
          if (mounted) {
            if (resp.data && resp.data.success) {
              setStudent(resp.data.student || resp.data.data?.student || resp.data.data);
              setError(null);
            } else {
              setError(resp.data?.message || 'Failed to load student');
            }
          }
        }
      } catch (err) {
        setError(err.response?.data?.message || err.message || 'Network error');
      } finally {
        if (mounted) setLoading(false);
      }
    };

    fetchStudent();
    return () => { mounted = false; };
  }, [truecredId, currentUser]);

  if (loading) return <div>Loading student profile...</div>;
  if (error) return <div className="text-red-600">{error}</div>;
  if (!student) return <div>No student data found.</div>;

  const isSelf = currentUser && (String(currentUser.id) === String(student.id) || String(currentUser.truecred_id) === String(student.truecred_id));

  return (
    <div className="p-4">
      <h2 className="text-2xl font-semibold">{student.name || student.username}</h2>
      <p className="text-sm text-gray-600">TrueCred ID: {student.truecred_id}</p>
      <p className="mt-2">Email: {student.email}</p>

      <section className="mt-4">
        <h3 className="font-medium">Education</h3>
        {student.education && student.education.length > 0 ? (
          <ul className="list-disc pl-6">
            {student.education.map((e, idx) => (
              <li key={idx}>
                <strong>{e.degree}</strong> in {e.field_of_study} — {e.institution} ({e.start_date} — {e.current ? 'Present' : e.end_date})
              </li>
            ))}
          </ul>
        ) : (
          <p>No education entries.</p>
        )}
      </section>

      {isSelf ? (
        <div className="mt-4">
          {!editMode ? (
            <button onClick={() => setEditMode(true)} className="px-3 py-1 bg-blue-600 text-white rounded">Edit your profile</button>
          ) : (
            <div>
              <ProfileCompletion onComplete={async () => {
                // After editing, refetch profile and exit edit mode
                setEditMode(false);
                setLoading(true);
                try {
                  const resp = await api.get('/api/user/profile');
                  if (resp.data && resp.data.success) {
                    setStudent(resp.data.user || resp.data.user || resp.data);
                  }
                } catch (err) {
                  console.warn('Failed refreshing profile after edit', err);
                } finally {
                  setLoading(false);
                }
              }} />
            </div>
          )}
        </div>
      ) : null}
    </div>
  );
}
