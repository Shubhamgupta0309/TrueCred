import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';

const emptyEdu = {
  institution: '',
  degree: '',
  field_of_study: '',
  start_date: '',
  end_date: '',
  current: false
};

const Profile = () => {
  const { user } = useAuth();
  const [education, setEducation] = useState([ { ...emptyEdu } ]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [profileCompleted, setProfileCompleted] = useState(false);

  useEffect(() => {
    // Fetch profile data on mount
    const fetchProfile = async () => {
      setIsLoading(true);
      try {
        const resp = await fetch('/api/user/profile', {
          headers: { 'Authorization': `Bearer ${localStorage.getItem('accessToken')}` }
        });
        const data = await resp.json();
        if (data.success && data.user) {
          setEducation(data.user.education && data.user.education.length > 0 ? data.user.education : [ { ...emptyEdu } ]);
          setProfileCompleted(!!data.user.profile_completed);
        }
      } catch (err) {
        setError('Failed to fetch profile');
      }
      setIsLoading(false);
    };
    fetchProfile();
  }, []);

  const handleEduChange = (idx, field, value) => {
    setEducation(prev => prev.map((e, i) => i === idx ? { ...e, [field]: value } : e));
    setError('');
    setSuccess('');
  };

  const addEducation = () => {
    setEducation(prev => [ ...prev, { ...emptyEdu } ]);
  };

  const removeEducation = idx => {
    setEducation(prev => prev.length > 1 ? prev.filter((_, i) => i !== idx) : prev);
  };

  const validateEdu = edu => {
    if (!edu.institution.trim() || !edu.degree.trim() || !edu.field_of_study.trim() || !edu.start_date.trim()) return false;
    if (!edu.current && !edu.end_date.trim()) return false;
    return true;
  };

  const handleSave = async () => {
    setIsLoading(true);
    setError('');
    setSuccess('');
    // Validate all education entries
    for (let i = 0; i < education.length; i++) {
      if (!validateEdu(education[i])) {
        setError(`Education entry ${i+1} is invalid. All fields except end date (if current) are required.`);
        setIsLoading(false);
        return;
      }
    }
    try {
      const resp = await fetch('/api/user/profile', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('accessToken')}`
        },
        body: JSON.stringify({ education })
      });
      const data = await resp.json();
      if (data.success) {
        setSuccess('Profile saved successfully!');
        setProfileCompleted(true);
      } else {
        setError(data.message || 'Failed to save profile');
      }
    } catch (err) {
      setError('Failed to save profile');
    }
    setIsLoading(false);
  };

  return (
    <div className="max-w-2xl mx-auto p-6 bg-white rounded shadow">
      <h2 className="text-2xl font-bold mb-4">Student Profile</h2>
      {profileCompleted && <span className="inline-block bg-green-100 text-green-800 px-3 py-1 rounded mb-2">Profile Complete</span>}
      {error && <div className="text-red-500 mb-2">{error}</div>}
      {success && <div className="text-green-600 mb-2">{success}</div>}
      <form onSubmit={e => { e.preventDefault(); handleSave(); }}>
        {education.map((edu, idx) => (
          <div key={idx} className="mb-4 p-4 border rounded">
            <div className="mb-2">
              <label className="block font-medium">Institution</label>
              <input type="text" value={edu.institution} onChange={e => handleEduChange(idx, 'institution', e.target.value)} className="w-full border px-2 py-1 rounded" required />
            </div>
            <div className="mb-2">
              <label className="block font-medium">Degree</label>
              <input type="text" value={edu.degree} onChange={e => handleEduChange(idx, 'degree', e.target.value)} className="w-full border px-2 py-1 rounded" required />
            </div>
            <div className="mb-2">
              <label className="block font-medium">Field of Study</label>
              <input type="text" value={edu.field_of_study} onChange={e => handleEduChange(idx, 'field_of_study', e.target.value)} className="w-full border px-2 py-1 rounded" required />
            </div>
            <div className="mb-2">
              <label className="block font-medium">Start Date</label>
              <input type="date" value={edu.start_date} onChange={e => handleEduChange(idx, 'start_date', e.target.value)} className="w-full border px-2 py-1 rounded" required />
            </div>
            <div className="mb-2">
              <label className="block font-medium">Current</label>
              <input type="checkbox" checked={edu.current} onChange={e => handleEduChange(idx, 'current', e.target.checked)} />
            </div>
            {!edu.current && (
              <div className="mb-2">
                <label className="block font-medium">End Date</label>
                <input type="date" value={edu.end_date} onChange={e => handleEduChange(idx, 'end_date', e.target.value)} className="w-full border px-2 py-1 rounded" required />
              </div>
            )}
            <button type="button" className="text-red-500 mt-2" onClick={() => removeEducation(idx)} disabled={education.length === 1}>Remove</button>
          </div>
        ))}
        <button type="button" className="bg-blue-500 text-white px-3 py-1 rounded mr-2" onClick={addEducation}>Add Education</button>
        <button type="submit" className="bg-green-600 text-white px-4 py-2 rounded" disabled={isLoading}>{isLoading ? 'Saving...' : 'Save Profile'}</button>
      </form>
    </div>
  );
};

export default Profile;
