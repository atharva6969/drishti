import React, { useState, useEffect } from 'react';
import { missingPersonsAPI, alertsAPI } from '../services/api';

function Dashboard() {
  const [stats, setStats] = useState({ active: 0, found: 0, closed: 0, alerts: 0 });
  const [recentAlerts, setRecentAlerts] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [activeRes, foundRes, alertsRes] = await Promise.all([
          missingPersonsAPI.list({ status: 'active' }),
          missingPersonsAPI.list({ status: 'found' }),
          alertsAPI.list({ limit: 5 }),
        ]);
        setStats({
          active: activeRes.data.length,
          found: foundRes.data.length,
          closed: 0,
          alerts: alertsRes.data.length,
        });
        setRecentAlerts(alertsRes.data);
      } catch {
        // API not available - show placeholder stats
        setStats({ active: 0, found: 0, closed: 0, alerts: 0 });
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const handleSearch = (e) => {
    e.preventDefault();
    alert(`Searching for: ${searchQuery}\n(Connect to backend for live search)`);
  };

  if (loading) {
    return (
      <div className="loading">
        <div className="spinner"></div>
        <p style={{ marginTop: 12 }}>Loading dashboard...</p>
      </div>
    );
  }

  return (
    <div>
      {/* Stats */}
      <div className="stats-grid">
        <div className="stat-card danger">
          <div className="stat-number">{stats.active}</div>
          <div className="stat-label">🔴 Active Cases</div>
        </div>
        <div className="stat-card success">
          <div className="stat-number">{stats.found}</div>
          <div className="stat-label">✅ Persons Found</div>
        </div>
        <div className="stat-card warning">
          <div className="stat-number">{stats.alerts}</div>
          <div className="stat-label">⚠️ Pending Alerts</div>
        </div>
        <div className="stat-card info">
          <div className="stat-number">6</div>
          <div className="stat-label">🤖 AI Modules Active</div>
        </div>
      </div>

      {/* Quick Search */}
      <div className="card section">
        <div className="card-header">
          <span className="card-title">🔍 Quick Face Search</span>
        </div>
        <form onSubmit={handleSearch} className="search-bar">
          <input
            type="text"
            className="form-input"
            placeholder="Enter case number, name, or upload a face image..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
          <button type="submit" className="btn btn-primary">Search</button>
          <button type="button" className="btn btn-outline">📷 Upload Image</button>
        </form>
      </div>

      <div className="dashboard-grid">
        {/* Recent Alerts */}
        <div className="card">
          <div className="card-header">
            <span className="card-title">🚨 Recent Alerts</span>
            <span className="badge badge-active">{recentAlerts.length} alerts</span>
          </div>
          {recentAlerts.length === 0 ? (
            <div className="empty-state">
              <div className="empty-icon">✅</div>
              <p>No pending alerts</p>
            </div>
          ) : (
            <div className="alerts-list">
              {recentAlerts.map((alert) => (
                <div key={alert.id} className={`alert-item ${getAlertPriority(alert.confidence_score)}`}>
                  <div className="alert-header">
                    <span className="alert-type">{formatAlertType(alert.alert_type)}</span>
                    <span className={`badge badge-${alert.status}`}>{alert.status}</span>
                  </div>
                  <div className="alert-meta">📍 {alert.location}</div>
                  <div className="alert-meta">
                    Confidence: {Math.round(alert.confidence_score * 100)}%
                    <div className="confidence-bar">
                      <div
                        className={`confidence-fill ${getAlertPriority(alert.confidence_score)}`}
                        style={{ width: `${alert.confidence_score * 100}%` }}
                      />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Map Placeholder */}
        <div className="card">
          <div className="card-header">
            <span className="card-title">🗺️ Heatmap</span>
          </div>
          <div className="map-placeholder">
            <div className="map-icon">🗺️</div>
            <strong>Location Probability Heatmap</strong>
            <p>Google Maps integration</p>
            <p style={{ marginTop: 8, fontSize: 13 }}>Configure REACT_APP_MAPS_KEY</p>
          </div>
        </div>
      </div>
    </div>
  );
}

function getAlertPriority(confidence) {
  if (confidence >= 0.8) return 'high';
  if (confidence >= 0.6) return 'medium';
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

export default Dashboard;
