import React, { useState, useEffect } from 'react';
import { alertsAPI } from '../services/api';

function AlertsList() {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('pending');

  useEffect(() => {
    const fetchAlerts = async () => {
      setLoading(true);
      try {
        const params = filter ? { status: filter } : {};
        const response = await alertsAPI.list(params);
        setAlerts(response.data);
      } catch {
        setAlerts([]);
      } finally {
        setLoading(false);
      }
    };
    fetchAlerts();
  }, [filter]);

  const handleVerify = async (alertId, verdict) => {
    const officerId = prompt('Enter your Officer ID:');
    if (!officerId) return;

    try {
      await alertsAPI.verify(alertId, { officer_id: officerId, verdict });
      setAlerts((prev) =>
        prev.map((a) => (a.id === alertId ? { ...a, status: verdict } : a))
      );
    } catch (err) {
      alert('Failed to verify alert. Please try again.');
    }
  };

  return (
    <div className="card">
      <div className="card-header">
        <span className="card-title">🚨 Alerts</span>
        <select
          className="form-select"
          style={{ width: 'auto', padding: '6px 12px' }}
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
        >
          <option value="">All Alerts</option>
          <option value="pending">Pending</option>
          <option value="verified">Verified</option>
          <option value="false_positive">False Positive</option>
        </select>
      </div>

      {loading ? (
        <div className="loading"><div className="spinner"></div></div>
      ) : alerts.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">✅</div>
          <p>No alerts found</p>
        </div>
      ) : (
        <div className="alerts-list">
          {alerts.map((alert) => (
            <div key={alert.id} className={`alert-item ${getConfidenceLevel(alert.confidence_score)}`}>
              <div className="alert-header">
                <span className="alert-type">{formatAlertType(alert.alert_type)}</span>
                <span className={`badge badge-${alert.status}`}>{alert.status.replace('_', ' ')}</span>
              </div>
              <div className="alert-meta">📍 {alert.location}</div>
              {alert.description && (
                <div className="alert-meta" style={{ marginTop: 4 }}>{alert.description}</div>
              )}
              <div className="alert-meta" style={{ marginTop: 6 }}>
                Confidence: {Math.round(alert.confidence_score * 100)}%
                <div className="confidence-bar">
                  <div
                    className={`confidence-fill ${getConfidenceLevel(alert.confidence_score)}`}
                    style={{ width: `${alert.confidence_score * 100}%` }}
                  />
                </div>
              </div>
              <div className="alert-meta" style={{ fontSize: 12 }}>
                Source: {alert.source || 'Unknown'} | {formatDate(alert.created_at)}
              </div>
              {alert.status === 'pending' && (
                <div className="alert-actions">
                  <button
                    className="btn btn-success btn-sm"
                    onClick={() => handleVerify(alert.id, 'verified')}
                  >
                    ✓ Verify
                  </button>
                  <button
                    className="btn btn-danger btn-sm"
                    onClick={() => handleVerify(alert.id, 'false_positive')}
                  >
                    ✗ False Positive
                  </button>
                </div>
              )}
              {alert.status === 'verified' && alert.verified_by && (
                <div className="alert-meta" style={{ color: '#2e7d32', marginTop: 6 }}>
                  ✅ Verified by officer | {formatDate(alert.verified_at)}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function getConfidenceLevel(score) {
  if (score >= 0.8) return 'high';
  if (score >= 0.6) return 'medium';
  return 'low';
}

function formatAlertType(type) {
  const labels = {
    face_match: '👤 Face Match',
    gait_match: '🚶 Gait Match',
    clothing_match: '👕 Clothing Match',
    sighting: '👁️ Community Sighting',
  };
  return labels[type] || type;
}

function formatDate(dateStr) {
  if (!dateStr) return '';
  return new Date(dateStr).toLocaleString('en-IN');
}

export default AlertsList;
