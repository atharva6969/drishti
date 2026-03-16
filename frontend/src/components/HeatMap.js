import React from 'react';

function HeatMap({ activeCases = [] }) {
  return (
    <div className="card">
      <div className="card-header">
        <span className="card-title">🗺️ Location Probability Heatmap</span>
        <span className="badge badge-active">{activeCases.length} active cases</span>
      </div>

      <div className="map-placeholder" style={{ height: 380 }}>
        <div className="map-icon">🗺️</div>
        <strong>Google Maps Integration</strong>
        <p style={{ marginTop: 8 }}>Set REACT_APP_MAPS_KEY environment variable</p>
        <p style={{ fontSize: 13 }}>Heatmap overlays trafficking corridors + sighting reports</p>
        <div style={{ marginTop: 16, display: 'flex', gap: 16, fontSize: 13 }}>
          <span>🔴 High Risk</span>
          <span>🟠 Medium Risk</span>
          <span>🟡 Low Risk</span>
          <span>📍 Sightings</span>
        </div>
      </div>

      <div style={{ marginTop: 16 }}>
        <div className="section-title" style={{ fontSize: 14 }}>High-Risk Corridors</div>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8, marginTop: 8 }}>
          {CORRIDORS.map((c) => (
            <div key={c.name} style={{ padding: '10px 14px', background: '#fff5f5', borderRadius: 8, border: '1px solid #ffcdd2', fontSize: 13 }}>
              <strong style={{ color: '#c62828' }}>{c.name}</strong>
              <div style={{ color: '#757575', marginTop: 2 }}>{c.route}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

const CORRIDORS = [
  { name: 'Bengal → Delhi', route: 'Murshidabad → Howrah → NDLS' },
  { name: 'Bihar → Mumbai', route: 'Patna → Varanasi → CSTM' },
  { name: 'Jharkhand → Punjab', route: 'Ranchi → Dhanbad → Ludhiana' },
  { name: 'Odisha → Surat', route: 'Bhubaneswar → Kolkata → Surat' },
];

export default HeatMap;
