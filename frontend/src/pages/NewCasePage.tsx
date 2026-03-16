import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { casesApi } from '../services/api';

const NewCasePage: React.FC = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [form, setForm] = useState({
    full_name: '',
    age_at_disappearance: '',
    gender: '',
    height_cm: '',
    weight_kg: '',
    distinguishing_marks: '',
    date_missing: '',
    last_seen_location: '',
    circumstances: '',
    case_type: 'missing',
    priority: 'normal',
    reporting_station: '',
    state: '',
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    setForm(f => ({ ...f, [e.target.name]: e.target.value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const payload = {
        ...form,
        age_at_disappearance: form.age_at_disappearance ? Number(form.age_at_disappearance) : null,
        height_cm: form.height_cm ? Number(form.height_cm) : null,
        weight_kg: form.weight_kg ? Number(form.weight_kg) : null,
        date_missing: new Date(form.date_missing).toISOString(),
      };
      const { data } = await casesApi.create(payload);
      navigate(`/cases/${data.id}`);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create case. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: '800px' }}>
      <div className="flex items-center gap-4 mb-6">
        <button className="btn btn-secondary" onClick={() => navigate('/cases')}>← Back</button>
        <div>
          <h1 style={{ fontSize: '1.75rem', marginBottom: '4px' }}>Register Missing Person</h1>
          <p className="text-muted text-sm">Complete all available fields for highest search accuracy</p>
        </div>
      </div>

      {error && <div className="alert-banner critical mb-4">⚠️ {error}</div>}

      <form onSubmit={handleSubmit}>
        {/* Personal Information */}
        <div className="card mb-6">
          <h2 style={{ fontSize: '1rem', marginBottom: '16px' }}>Personal Information</h2>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
            <div className="form-group" style={{ gridColumn: '1 / -1' }}>
              <label className="form-label">Full Name *</label>
              <input type="text" name="full_name" className="form-input" value={form.full_name}
                onChange={handleChange} required placeholder="As per official records" />
            </div>
            <div className="form-group">
              <label className="form-label">Age at Disappearance</label>
              <input type="number" name="age_at_disappearance" className="form-input"
                value={form.age_at_disappearance} onChange={handleChange} min="0" max="150" />
            </div>
            <div className="form-group">
              <label className="form-label">Gender</label>
              <select name="gender" className="form-select" value={form.gender} onChange={handleChange}>
                <option value="">Select</option>
                <option value="female">Female</option>
                <option value="male">Male</option>
                <option value="other">Other</option>
              </select>
            </div>
            <div className="form-group">
              <label className="form-label">Height (cm)</label>
              <input type="number" name="height_cm" className="form-input"
                value={form.height_cm} onChange={handleChange} placeholder="e.g. 155" />
            </div>
            <div className="form-group">
              <label className="form-label">Weight (kg)</label>
              <input type="number" name="weight_kg" className="form-input"
                value={form.weight_kg} onChange={handleChange} placeholder="e.g. 45" />
            </div>
            <div className="form-group" style={{ gridColumn: '1 / -1' }}>
              <label className="form-label">Distinguishing Marks / Features</label>
              <textarea name="distinguishing_marks" className="form-textarea" rows={2}
                value={form.distinguishing_marks} onChange={handleChange}
                placeholder="Birthmarks, tattoos, scars, etc." />
            </div>
          </div>
        </div>

        {/* Disappearance Details */}
        <div className="card mb-6">
          <h2 style={{ fontSize: '1rem', marginBottom: '16px' }}>Disappearance Details</h2>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
            <div className="form-group">
              <label className="form-label">Date & Time Missing *</label>
              <input type="datetime-local" name="date_missing" className="form-input"
                value={form.date_missing} onChange={handleChange} required />
            </div>
            <div className="form-group">
              <label className="form-label">State</label>
              <input type="text" name="state" className="form-input" value={form.state}
                onChange={handleChange} placeholder="e.g. West Bengal" />
            </div>
            <div className="form-group" style={{ gridColumn: '1 / -1' }}>
              <label className="form-label">Last Seen Location</label>
              <input type="text" name="last_seen_location" className="form-input"
                value={form.last_seen_location} onChange={handleChange}
                placeholder="Specific location where person was last seen" />
            </div>
            <div className="form-group" style={{ gridColumn: '1 / -1' }}>
              <label className="form-label">Circumstances</label>
              <textarea name="circumstances" className="form-textarea" rows={3}
                value={form.circumstances} onChange={handleChange}
                placeholder="Describe the circumstances of disappearance..." />
            </div>
          </div>
        </div>

        {/* Classification */}
        <div className="card mb-6">
          <h2 style={{ fontSize: '1rem', marginBottom: '16px' }}>Case Classification</h2>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '16px' }}>
            <div className="form-group">
              <label className="form-label">Case Type *</label>
              <select name="case_type" className="form-select" value={form.case_type} onChange={handleChange}>
                <option value="missing">Missing</option>
                <option value="trafficking">Trafficking (Suspected)</option>
                <option value="abduction">Abduction</option>
                <option value="runaway">Runaway</option>
              </select>
            </div>
            <div className="form-group">
              <label className="form-label">Priority *</label>
              <select name="priority" className="form-select" value={form.priority} onChange={handleChange}>
                <option value="critical">🔴 Critical</option>
                <option value="high">🟠 High</option>
                <option value="normal">🟡 Normal</option>
                <option value="low">🟢 Low</option>
              </select>
            </div>
            <div className="form-group">
              <label className="form-label">Reporting Station</label>
              <input type="text" name="reporting_station" className="form-input"
                value={form.reporting_station} onChange={handleChange}
                placeholder="e.g. Murshidabad PS" />
            </div>
          </div>
        </div>

        <div className="flex gap-4">
          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? '⏳ Registering...' : '✅ Register Case & Activate Alerts'}
          </button>
          <button type="button" className="btn btn-secondary" onClick={() => navigate('/cases')}>
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
};

export default NewCasePage;
