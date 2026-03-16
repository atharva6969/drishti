import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { casesApi, alertsApi } from '../services/api';

const StatCard: React.FC<{ title: string; value: string | number; icon: string; color?: string }> = ({
  title, value, icon, color = 'var(--color-accent)',
}) => (
  <div className="card">
    <div className="flex items-center justify-between mb-4">
      <span className="card-title">{title}</span>
      <span style={{ fontSize: '1.5rem' }}>{icon}</span>
    </div>
    <div className="card-value" style={{ color }}>{value}</div>
  </div>
);

const DashboardPage: React.FC = () => {
  const { data: casesData } = useQuery({
    queryKey: ['cases', 'active'],
    queryFn: () => casesApi.list({ status: 'active', page_size: 5 }),
  });

  const { data: alertsData } = useQuery({
    queryKey: ['alerts', 'recent'],
    queryFn: () => alertsApi.list({ limit: 5 }),
  });

  const activeCases = casesData?.data?.total ?? '—';
  const recentAlerts = alertsData?.data?.length ?? '—';

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 style={{ fontSize: '1.75rem', marginBottom: '4px' }}>Command Dashboard</h1>
          <p className="text-muted text-sm">Real-time overview of active cases and alerts</p>
        </div>
        <Link to="/cases/new" className="btn btn-primary">
          + Register Missing Person
        </Link>
      </div>

      {/* Stats */}
      <div className="stats-grid">
        <StatCard title="Active Cases" value={activeCases} icon="👤" color="#ef5350" />
        <StatCard title="Sightings (24h)" value="—" icon="👁️" color="#ff7043" />
        <StatCard title="Alerts Pending" value={recentAlerts} icon="🚨" color="#ffa726" />
        <StatCard title="Community Reporters" value="—" icon="👥" color="#66bb6a" />
        <StatCard title="Corridors Active" value="—" icon="🗺️" color="#42a5f5" />
        <StatCard title="Verified Sightings" value="—" icon="✅" color="#26a69a" />
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px' }}>
        {/* Recent Cases */}
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h2 style={{ fontSize: '1rem' }}>Recent Active Cases</h2>
            <Link to="/cases" className="text-sm" style={{ color: 'var(--color-accent)' }}>
              View all →
            </Link>
          </div>
          {casesData?.data?.items?.length ? (
            <table className="table">
              <thead>
                <tr>
                  <th>Case #</th>
                  <th>Name</th>
                  <th>Priority</th>
                  <th>Days Missing</th>
                </tr>
              </thead>
              <tbody>
                {casesData.data.items.map((c: any) => (
                  <tr key={c.id} onClick={() => window.location.href = `/cases/${c.id}`}>
                    <td style={{ fontFamily: 'monospace', fontSize: '0.75rem' }}>{c.case_number}</td>
                    <td>{c.full_name}</td>
                    <td><span className={`badge badge-${c.priority}`}>{c.priority}</span></td>
                    <td className="text-muted">
                      {Math.floor((Date.now() - new Date(c.date_missing).getTime()) / 86400000)}d
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <p className="text-muted text-sm">No active cases found.</p>
          )}
        </div>

        {/* Recent Alerts */}
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h2 style={{ fontSize: '1rem' }}>Recent Alerts</h2>
            <Link to="/alerts" className="text-sm" style={{ color: 'var(--color-accent)' }}>
              View all →
            </Link>
          </div>
          {alertsData?.data?.length ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {alertsData.data.map((a: any) => (
                <div key={a.id} className={`alert-banner ${a.severity === 'critical' ? 'critical' : 'info'}`}>
                  <div>
                    <div style={{ fontWeight: 600, fontSize: '0.875rem' }}>{a.title}</div>
                    <div className="text-xs text-muted">{a.alert_type} · {a.status}</div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-muted text-sm">No recent alerts.</p>
          )}
        </div>
      </div>

      {/* Quick Actions */}
      <div className="card" style={{ marginTop: '24px' }}>
        <h2 style={{ fontSize: '1rem', marginBottom: '16px' }}>Quick Actions</h2>
        <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
          <Link to="/cases/new" className="btn btn-primary">📋 Register Case</Link>
          <Link to="/search" className="btn btn-secondary">🔍 Face Search</Link>
          <Link to="/alerts" className="btn btn-secondary">🚨 View Alerts</Link>
          <Link to="/map" className="btn btn-secondary">🗺️ Live Map</Link>
          <Link to="/community" className="btn btn-secondary">📢 Broadcast Alert</Link>
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;
