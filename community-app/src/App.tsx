import React, { useState } from 'react';
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

const App: React.FC = () => {
  const [step, setStep] = useState<'intro' | 'report' | 'success'>('intro');
  const [photo, setPhoto] = useState<File | null>(null);
  const [location, setLocation] = useState('');
  const [description, setDescription] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleGetLocation = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (pos) => setLocation(`${pos.coords.latitude},${pos.coords.longitude}`),
        () => setError('Could not get location. Please enter it manually.')
      );
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    if (!photo && !description) {
      setError('Please provide a photo or description.');
      return;
    }
    setLoading(true);
    try {
      const formData = new FormData();
      if (photo) formData.append('photo', photo);
      formData.append('location', location);
      formData.append('description', description);
      formData.append('source', 'community_app');
      await axios.post(`${API_URL}/sightings/community`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setStep('success');
    } catch {
      setError('Submission failed. Please try WhatsApp: wa.me/DRISHTI_NUMBER');
    } finally {
      setLoading(false);
    }
  };

  const styles = {
    container: {
      maxWidth: '480px',
      margin: '0 auto',
      padding: '20px',
      fontFamily: 'sans-serif',
      background: '#fff',
      minHeight: '100vh',
    },
    header: {
      background: '#e53935',
      color: 'white',
      padding: '16px',
      borderRadius: '8px',
      marginBottom: '20px',
      textAlign: 'center' as const,
    },
    title: { fontSize: '1.5rem', fontWeight: 700, margin: 0 },
    subtitle: { fontSize: '0.75rem', margin: '4px 0 0', opacity: 0.9 },
    btn: {
      width: '100%',
      padding: '14px',
      borderRadius: '8px',
      border: 'none',
      fontSize: '1rem',
      fontWeight: 600,
      cursor: 'pointer',
      marginBottom: '12px',
    },
    btnPrimary: { background: '#e53935', color: 'white' },
    btnSecondary: { background: '#f5f5f5', color: '#333' },
    input: {
      width: '100%',
      padding: '12px',
      border: '1px solid #ddd',
      borderRadius: '8px',
      fontSize: '1rem',
      marginBottom: '12px',
      boxSizing: 'border-box' as const,
    },
    label: { fontWeight: 600, fontSize: '0.875rem', color: '#555', display: 'block', marginBottom: '4px' },
    error: { background: '#ffebee', color: '#c62828', padding: '10px', borderRadius: '6px', marginBottom: '12px', fontSize: '0.875rem' },
  };

  if (step === 'success') {
    return (
      <div style={styles.container}>
        <div style={styles.header}>
          <div style={styles.title}>DRISHTI</div>
          <div style={styles.subtitle}>Community Reporter</div>
        </div>
        <div style={{ textAlign: 'center', padding: '40px 20px' }}>
          <div style={{ fontSize: '4rem', marginBottom: '16px' }}>✅</div>
          <h2 style={{ color: '#2e7d32', marginBottom: '8px' }}>Report Submitted!</h2>
          <p style={{ color: '#666', marginBottom: '24px' }}>
            Thank you. Your sighting has been sent to the AHTU team for immediate follow-up.
            You may be contacted for verification.
          </p>
          <button style={{ ...styles.btn, ...styles.btnSecondary }} onClick={() => {
            setStep('intro'); setPhoto(null); setLocation(''); setDescription('');
          }}>
            Submit Another Report
          </button>
        </div>
      </div>
    );
  }

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <div style={styles.title}>दृष्टि · DRISHTI</div>
        <div style={styles.subtitle}>Report Missing Person Sighting</div>
      </div>

      {step === 'intro' && (
        <>
          <p style={{ color: '#555', marginBottom: '20px', lineHeight: 1.6 }}>
            If you have seen a missing person or suspect trafficking activity, report it here.
            Your identity is protected. Every report matters.
          </p>
          <div style={{ background: '#fff8e1', border: '1px solid #ffc107', borderRadius: '8px', padding: '12px', marginBottom: '20px' }}>
            <strong>🚨 Emergency?</strong> Call <a href="tel:1098" style={{ color: '#e53935' }}>1098 (Childline)</a> or{' '}
            <a href="tel:100" style={{ color: '#e53935' }}>100 (Police)</a>
          </div>
          <button style={{ ...styles.btn, ...styles.btnPrimary }} onClick={() => setStep('report')}>
            📷 Report a Sighting
          </button>
          <a href="https://wa.me/911234567890" style={{ ...styles.btn, ...styles.btnSecondary, display: 'block', textAlign: 'center', textDecoration: 'none', color: '#333' }}>
            💬 Report via WhatsApp
          </a>
          <p style={{ fontSize: '0.7rem', color: '#999', textAlign: 'center', marginTop: '20px', lineHeight: 1.6 }}>
            All reports are treated confidentially and reviewed by law enforcement.
            Providing false information is a criminal offense.
          </p>
        </>
      )}

      {step === 'report' && (
        <form onSubmit={handleSubmit}>
          <button type="button" style={{ ...styles.btn, ...styles.btnSecondary, marginBottom: '20px' }} onClick={() => setStep('intro')}>
            ← Back
          </button>

          {error && <div style={styles.error}>{error}</div>}

          <div style={{ marginBottom: '12px' }}>
            <label style={styles.label}>Photo (optional but helpful)</label>
            <input
              type="file"
              accept="image/*"
              capture="environment"
              style={styles.input}
              onChange={e => setPhoto(e.target.files?.[0] || null)}
            />
            {photo && <p style={{ fontSize: '0.8rem', color: '#2e7d32' }}>✅ Photo selected: {photo.name}</p>}
          </div>

          <div style={{ marginBottom: '12px' }}>
            <label style={styles.label}>Location</label>
            <input
              type="text"
              style={styles.input}
              placeholder="e.g. Howrah Station, Platform 7"
              value={location}
              onChange={e => setLocation(e.target.value)}
            />
            <button type="button" style={{ ...styles.btn, ...styles.btnSecondary, padding: '10px', fontSize: '0.875rem' }}
              onClick={handleGetLocation}>
              📍 Use My Current Location
            </button>
          </div>

          <div style={{ marginBottom: '20px' }}>
            <label style={styles.label}>What did you see? *</label>
            <textarea
              style={{ ...styles.input, minHeight: '100px', resize: 'vertical' }}
              placeholder="Describe what you saw — clothing, direction of travel, who they were with..."
              value={description}
              onChange={e => setDescription(e.target.value)}
              required
            />
          </div>

          <button type="submit" style={{ ...styles.btn, ...styles.btnPrimary }} disabled={loading}>
            {loading ? '⏳ Submitting...' : '📤 Submit Report'}
          </button>

          <p style={{ fontSize: '0.7rem', color: '#999', textAlign: 'center', marginTop: '12px' }}>
            Your report is encrypted and only accessible to authorized officers.
          </p>
        </form>
      )}
    </div>
  );
};

export default App;
