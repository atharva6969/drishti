import React, { useState } from 'react';
import { missingPersonsAPI } from '../services/api';

const INITIAL_FORM = {
  name: '',
  age: '',
  gender: '',
  height_cm: '',
  weight_kg: '',
  last_seen_location: '',
  last_seen_date: '',
  reported_by: '',
  contact_number: '',
  state: '',
  district: '',
  physical_description: '',
  clothing_description: '',
};

const INDIAN_STATES = [
  'Andhra Pradesh', 'Assam', 'Bihar', 'Chhattisgarh', 'Delhi',
  'Goa', 'Gujarat', 'Haryana', 'Himachal Pradesh', 'Jharkhand',
  'Karnataka', 'Kerala', 'Madhya Pradesh', 'Maharashtra', 'Manipur',
  'Meghalaya', 'Mizoram', 'Nagaland', 'Odisha', 'Punjab',
  'Rajasthan', 'Sikkim', 'Tamil Nadu', 'Telangana', 'Tripura',
  'Uttar Pradesh', 'Uttarakhand', 'West Bengal',
];

function MissingPersonForm({ onSuccess }) {
  const [form, setForm] = useState(INITIAL_FORM);
  const [photo, setPhoto] = useState(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState(null);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handlePhotoChange = (e) => {
    setPhoto(e.target.files[0]);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!form.name.trim()) {
      setMessage({ type: 'error', text: 'Name is required.' });
      return;
    }

    setLoading(true);
    setMessage(null);

    try {
      const payload = { ...form };
      if (payload.age) payload.age = parseInt(payload.age);
      if (payload.height_cm) payload.height_cm = parseFloat(payload.height_cm);
      if (payload.weight_kg) payload.weight_kg = parseFloat(payload.weight_kg);
      if (payload.last_seen_date) payload.last_seen_date = new Date(payload.last_seen_date).toISOString();

      // Remove empty strings
      Object.keys(payload).forEach((k) => {
        if (payload[k] === '') delete payload[k];
      });

      const response = await missingPersonsAPI.create(payload);
      const personId = response.data.id;

      // Upload photo if provided
      if (photo && personId) {
        const formData = new FormData();
        formData.append('file', photo);
        await missingPersonsAPI.uploadPhoto(personId, formData);
      }

      setMessage({
        type: 'success',
        text: `Case registered! Case Number: ${response.data.case_number}`,
      });
      setForm(INITIAL_FORM);
      setPhoto(null);
      if (onSuccess) onSuccess(response.data);
    } catch (err) {
      setMessage({
        type: 'error',
        text: err.response?.data?.detail || 'Failed to submit. Check backend connection.',
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card">
      <div className="card-header">
        <span className="card-title">📋 Report Missing Person</span>
      </div>

      {message && (
        <div className={`alert-banner ${message.type}`}>{message.text}</div>
      )}

      <form onSubmit={handleSubmit}>
        <div className="form-row">
          <div className="form-group">
            <label className="form-label">Full Name *</label>
            <input className="form-input" name="name" value={form.name} onChange={handleChange} placeholder="Full name" required />
          </div>
          <div className="form-group">
            <label className="form-label">Age</label>
            <input className="form-input" name="age" type="number" value={form.age} onChange={handleChange} placeholder="Age in years" min="0" max="120" />
          </div>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label className="form-label">Gender</label>
            <select className="form-select" name="gender" value={form.gender} onChange={handleChange}>
              <option value="">Select gender</option>
              <option>Female</option>
              <option>Male</option>
              <option>Other</option>
            </select>
          </div>
          <div className="form-group">
            <label className="form-label">Contact Number</label>
            <input className="form-input" name="contact_number" value={form.contact_number} onChange={handleChange} placeholder="+91-XXXXXXXXXX" />
          </div>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label className="form-label">Height (cm)</label>
            <input className="form-input" name="height_cm" type="number" value={form.height_cm} onChange={handleChange} placeholder="e.g. 155" />
          </div>
          <div className="form-group">
            <label className="form-label">Weight (kg)</label>
            <input className="form-input" name="weight_kg" type="number" value={form.weight_kg} onChange={handleChange} placeholder="e.g. 50" />
          </div>
        </div>

        <div className="form-group">
          <label className="form-label">Last Seen Location</label>
          <input className="form-input" name="last_seen_location" value={form.last_seen_location} onChange={handleChange} placeholder="e.g. Murshidabad Railway Station, Platform 3" />
        </div>

        <div className="form-row">
          <div className="form-group">
            <label className="form-label">Last Seen Date &amp; Time</label>
            <input className="form-input" name="last_seen_date" type="datetime-local" value={form.last_seen_date} onChange={handleChange} />
          </div>
          <div className="form-group">
            <label className="form-label">State</label>
            <select className="form-select" name="state" value={form.state} onChange={handleChange}>
              <option value="">Select state</option>
              {INDIAN_STATES.map((s) => <option key={s}>{s}</option>)}
            </select>
          </div>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label className="form-label">District</label>
            <input className="form-input" name="district" value={form.district} onChange={handleChange} placeholder="District name" />
          </div>
          <div className="form-group">
            <label className="form-label">Reported By</label>
            <input className="form-input" name="reported_by" value={form.reported_by} onChange={handleChange} placeholder="Name of reporter" />
          </div>
        </div>

        <div className="form-group">
          <label className="form-label">Physical Description</label>
          <textarea className="form-textarea" name="physical_description" value={form.physical_description} onChange={handleChange} placeholder="Hair color, eye color, distinguishing marks, scars, tattoos..." />
        </div>

        <div className="form-group">
          <label className="form-label">Clothing Description</label>
          <textarea className="form-textarea" name="clothing_description" value={form.clothing_description} onChange={handleChange} placeholder="Color, type of clothing worn when last seen..." />
        </div>

        <div className="form-group">
          <label className="form-label">📸 Photo Upload</label>
          <input type="file" accept="image/*" onChange={handlePhotoChange} style={{ fontSize: 14 }} />
          {photo && <p style={{ fontSize: 13, color: '#2e7d32', marginTop: 4 }}>✓ {photo.name}</p>}
        </div>

        <button type="submit" className="btn btn-primary btn-full" disabled={loading}>
          {loading ? '⏳ Submitting...' : '🚨 Submit Missing Person Report'}
        </button>
      </form>
    </div>
  );
}

export default MissingPersonForm;
