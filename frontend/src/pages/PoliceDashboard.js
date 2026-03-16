import React, { useState } from 'react';
import Dashboard from '../components/Dashboard';
import MissingPersonForm from '../components/MissingPersonForm';
import AlertsList from '../components/AlertsList';
import SearchResults from '../components/SearchResults';
import CaseManager from '../components/CaseManager';
import HeatMap from '../components/HeatMap';

const TABS = [
  { id: 'overview', label: '📊 Overview' },
  { id: 'cases', label: '📁 Cases' },
  { id: 'report', label: '📋 Report Missing' },
  { id: 'search', label: '🔍 Face Search' },
  { id: 'alerts', label: '🚨 Alerts' },
  { id: 'map', label: '🗺️ Heatmap' },
];

function PoliceDashboard() {
  const [activeTab, setActiveTab] = useState('overview');

  return (
    <div>
      <div className="page-header">
        <h1>🚔 Police Dashboard</h1>
        <p>DRISHTI Anti-Trafficking Intelligence System — Law Enforcement Portal</p>
      </div>

      {/* Tabs */}
      <div style={{ display: 'flex', gap: 4, marginBottom: 24, flexWrap: 'wrap' }}>
        {TABS.map((tab) => (
          <button
            key={tab.id}
            className={`btn ${activeTab === tab.id ? 'btn-primary' : 'btn-outline'} btn-sm`}
            onClick={() => setActiveTab(tab.id)}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {activeTab === 'overview' && <Dashboard />}
      {activeTab === 'cases' && <CaseManager />}
      {activeTab === 'report' && <MissingPersonForm />}
      {activeTab === 'search' && <SearchResults />}
      {activeTab === 'alerts' && <AlertsList />}
      {activeTab === 'map' && <HeatMap />}
    </div>
  );
}

export default PoliceDashboard;
