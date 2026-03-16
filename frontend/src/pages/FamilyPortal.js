import React, { useState } from 'react';
import { reportsAPI, missingPersonsAPI } from '../services/api';

function FamilyPortal() {
  const [activeTab, setActiveTab] = useState('report_missing');
  const [sightingForm, setSightingForm] = useState({
    reporter_name: '',
    reporter_phone: '',
    case_number: '',
    location: '',
    description: '',
    confidence: 0.5,
  });
  const [sightingResult, setSightingResult] = useState(null);
  const [caseSearch, setCaseSearch] = useState('');
  const [foundCase, setFoundCase] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSightingSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const response = await reportsAPI.submitSighting(sightingForm);
      setSightingResult(response.data);
    } catch (err) {
      setSightingResult({ status: 'error', message: 'Failed to submit. Try again.' });
    } finally {
      setLoading(false);
    }
  };

  const handleCaseSearch = async (e) => {
    e.preventDefault();
    try {
      const response = await missingPersonsAPI.list({ status: '' });
      const match = response.data.find(
        (p) =>
          p.case_number?.includes(caseSearch) ||
          p.name?.toLowerCase().includes(caseSearch.toLowerCase())
      );
      setFoundCase(match || null);
    } catch {
      setFoundCase(null);
    }
  };

  return (
    <div>
      <div className="page-header">
        <h1>👨‍👩‍👧 Family Portal</h1>
        <p>Report sightings, track case status, and get help</p>
      </div>

      <div className="alert-banner info" style={{ marginBottom: 20 }}>
        🆘 Emergency? Call <strong>100</strong> (Police) or <strong>1098</strong> (Childline) immediately.
      </div>

      <div style={{ display: 'flex', gap: 4, marginBottom: 24 }}>
        <button className={`btn ${activeTab === 'report_missing' ? 'btn-primary' : 'btn-outline'} btn-sm`} onClick={() => setActiveTab('report_missing')}>
          📋 Report Missing Person
        </button>
        <button className={`btn ${activeTab === 'sighting' ? 'btn-primary' : 'btn-outline'} btn-sm`} onClick={() => setActiveTab('sighting')}>
          👁️ Report Sighting
        </button>
        <button className={`btn ${activeTab === 'track' ? 'btn-primary' : 'btn-outline'} btn-sm`} onClick={() => setActiveTab('track')}>
          🔎 Track Case Status
        </button>
      </div>

      {activeTab === 'report_missing' && (
        <div>
          <div className="alert-banner info">
            Report a missing person directly to DRISHTI. Your report is automatically shared with police and AHTU.
          </div>
          <div style={{ marginTop: 16 }}>
            {/* Simplified form for families */}
            <div className="card">
              <div className="card-header"><span className="card-title">📋 Report Missing Person</span></div>
              <p style={{ color: '#757575', marginBottom: 16, fontSize: 14 }}>
                Fill in as many details as possible. Even partial information can help locate your loved one.
              </p>
              <a href="/" className="btn btn-primary">Use Full Reporting Form</a>
              <p style={{ marginTop: 12, fontSize: 13, color: '#757575' }}>
                Or call the nearest police station. Always dial <strong>100</strong> first in emergencies.
              </p>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'sighting' && (
        <div className="card">
          <div className="card-header"><span className="card-title">👁️ Report a Sighting</span></div>
          <p style={{ color: '#757575', marginBottom: 16, fontSize: 14 }}>
            If you've seen someone who matches a missing person's description, please report it here immediately.
          </p>

          {sightingResult ? (
            <div>
              {sightingResult.status === 'received' ? (
                <div className="alert-banner success">
                  ✅ Report received! Report ID: <strong>{sightingResult.report?.report_id}</strong>
                  <ul style={{ marginTop: 8, paddingLeft: 20, fontSize: 13 }}>
                    {sightingResult.next_steps?.map((step, i) => <li key={i}>{step}</li>)}
                  </ul>
                </div>
              ) : (
                <div className="alert-banner error">{sightingResult.message || 'Error submitting report.'}</div>
              )}
              <button className="btn btn-outline btn-sm" style={{ marginTop: 12 }} onClick={() => setSightingResult(null)}>
                Submit Another Report
              </button>
            </div>
          ) : (
            <form onSubmit={handleSightingSubmit}>
              <div className="form-row">
                <div className="form-group">
                  <label className="form-label">Your Name *</label>
                  <input className="form-input" value={sightingForm.reporter_name} onChange={(e) => setSightingForm({ ...sightingForm, reporter_name: e.target.value })} required />
                </div>
                <div className="form-group">
                  <label className="form-label">Your Phone</label>
                  <input className="form-input" value={sightingForm.reporter_phone} onChange={(e) => setSightingForm({ ...sightingForm, reporter_phone: e.target.value })} placeholder="+91-XXXXXXXXXX" />
                </div>
              </div>
              <div className="form-group">
                <label className="form-label">Case Number (if known)</label>
                <input className="form-input" value={sightingForm.case_number} onChange={(e) => setSightingForm({ ...sightingForm, case_number: e.target.value })} placeholder="DRISHTI-WB-..." />
              </div>
              <div className="form-group">
                <label className="form-label">Location Where Sighted *</label>
                <input className="form-input" value={sightingForm.location} onChange={(e) => setSightingForm({ ...sightingForm, location: e.target.value })} placeholder="Platform, street, building..." required />
              </div>
              <div className="form-group">
                <label className="form-label">Description *</label>
                <textarea className="form-textarea" value={sightingForm.description} onChange={(e) => setSightingForm({ ...sightingForm, description: e.target.value })} placeholder="Describe what you saw in detail..." required />
              </div>
              <button type="submit" className="btn btn-primary btn-full" disabled={loading}>
                {loading ? '⏳ Submitting...' : '📤 Submit Sighting Report'}
              </button>
            </form>
          )}
        </div>
      )}

      {activeTab === 'track' && (
        <div className="card">
          <div className="card-header"><span className="card-title">🔎 Track Case Status</span></div>
          <form onSubmit={handleCaseSearch}>
            <div className="search-bar">
              <input
                className="form-input"
                placeholder="Enter case number or name..."
                value={caseSearch}
                onChange={(e) => setCaseSearch(e.target.value)}
              />
              <button type="submit" className="btn btn-primary">Search</button>
            </div>
          </form>

          {foundCase && (
            <div style={{ marginTop: 16, padding: 16, background: '#f8f9ff', borderRadius: 8 }}>
              <h3 style={{ color: '#1a237e', marginBottom: 12 }}>{foundCase.name}</h3>
              <p><strong>Case Number:</strong> <code>{foundCase.case_number}</code></p>
              <p><strong>Status:</strong> <span className={`badge badge-${foundCase.status}`}>{foundCase.status}</span></p>
              <p><strong>Last Seen:</strong> {foundCase.last_seen_location || 'Unknown'}</p>
              <p><strong>State:</strong> {foundCase.state || 'Unknown'}</p>
              <p style={{ marginTop: 12, fontSize: 13, color: '#757575' }}>
                For updates, contact your local police station with case number <strong>{foundCase.case_number}</strong>.
              </p>
            </div>
          )}

          {caseSearch && foundCase === null && (
            <div className="empty-state">
              <div className="empty-icon">🔍</div>
              <p>No case found. Please check the case number or contact local police.</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default FamilyPortal;
