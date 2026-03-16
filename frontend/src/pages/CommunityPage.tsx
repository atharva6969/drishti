import React from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { communityApi } from '../services/api';

const CommunityPage: React.FC = () => {
  const { data, isLoading } = useQuery({
    queryKey: ['reporters'],
    queryFn: () => communityApi.reporters(),
  });

  const reporters = data?.data || [];
  const verified = reporters.filter((r: any) => r.is_verified).length;
  const totalSightings = reporters.reduce((sum: number, r: any) => sum + r.total_sightings, 0);
  const validSightings = reporters.reduce((sum: number, r: any) => sum + r.valid_sightings, 0);

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 style={{ fontSize: '1.75rem', marginBottom: '4px' }}>Community Intelligence Network</h1>
          <p className="text-muted text-sm">Verified community reporters and WhatsApp network</p>
        </div>
      </div>

      {/* Stats */}
      <div className="stats-grid mb-6">
        <div className="card">
          <div className="card-title">Total Reporters</div>
          <div className="card-value">{reporters.length}</div>
        </div>
        <div className="card">
          <div className="card-title">Verified Reporters</div>
          <div className="card-value" style={{ color: '#66bb6a' }}>{verified}</div>
        </div>
        <div className="card">
          <div className="card-title">Total Sightings</div>
          <div className="card-value">{totalSightings}</div>
        </div>
        <div className="card">
          <div className="card-title">Valid Sightings</div>
          <div className="card-value" style={{ color: '#42a5f5' }}>{validSightings}</div>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px' }}>
        {/* Reporters list */}
        <div className="card">
          <h2 style={{ fontSize: '1rem', marginBottom: '16px' }}>Community Reporters</h2>
          {isLoading ? (
            <div className="spinner" style={{ margin: '40px auto' }}></div>
          ) : reporters.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '40px' }}>
              <div style={{ fontSize: '3rem', marginBottom: '12px' }}>👥</div>
              <p className="text-muted text-sm">No community reporters registered yet.</p>
              <p className="text-xs text-muted" style={{ marginTop: '8px' }}>
                Reporters sign up via WhatsApp: wa.me/[DRISHTI_NUMBER]
              </p>
            </div>
          ) : (
            <table className="table">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Location</th>
                  <th>Verified</th>
                  <th>Sightings</th>
                  <th>Valid</th>
                </tr>
              </thead>
              <tbody>
                {reporters.map((r: any) => (
                  <tr key={r.id}>
                    <td style={{ fontWeight: 500 }}>{r.name}</td>
                    <td className="text-sm text-muted">{r.district}, {r.state}</td>
                    <td>{r.is_verified ? '✅' : '⏳'}</td>
                    <td>{r.total_sightings}</td>
                    <td style={{ color: '#66bb6a' }}>{r.valid_sightings}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>

        {/* WhatsApp bot info */}
        <div>
          <div className="card mb-6">
            <h2 style={{ fontSize: '1rem', marginBottom: '16px' }}>WhatsApp Bot Status</h2>
            <div style={{ padding: '16px', background: 'var(--color-surface-2)', borderRadius: '8px', marginBottom: '16px' }}>
              <div className="flex items-center gap-2 mb-2">
                <div style={{ width: 8, height: 8, borderRadius: '50%', background: '#66bb6a' }}></div>
                <span style={{ fontWeight: 600, color: '#66bb6a' }}>Bot Operational</span>
              </div>
              <p className="text-sm text-muted">
                Twilio WhatsApp integration active. Community reporters can send sighting photos
                and descriptions directly via WhatsApp.
              </p>
            </div>

            <div style={{ fontSize: '0.875rem', lineHeight: '2' }}>
              <div className="flex items-center gap-2">
                <span>📱</span>
                <span>Report sighting: Send photo + location to DRISHTI WhatsApp number</span>
              </div>
              <div className="flex items-center gap-2">
                <span>📍</span>
                <span>GPS auto-extracted from photo metadata</span>
              </div>
              <div className="flex items-center gap-2">
                <span>🔔</span>
                <span>Alerts sent to reporters within 50km radius</span>
              </div>
              <div className="flex items-center gap-2">
                <span>🌐</span>
                <span>Supports: Hindi, Bengali, Tamil, Telugu, Marathi, English</span>
              </div>
            </div>
          </div>

          <div className="card">
            <h2 style={{ fontSize: '1rem', marginBottom: '16px' }}>Alert Network Channels</h2>
            {[
              { icon: '📱', name: 'WhatsApp (Twilio)', status: 'active', coverage: '10,000+ reporters' },
              { icon: '💬', name: 'SMS Alerts', status: 'active', coverage: 'All registered contacts' },
              { icon: '📻', name: 'Gram Panchayat Network', status: 'planned', coverage: '2.5 lakh villages' },
              { icon: '🚌', name: 'Auto/Truck Driver Network', status: 'planned', coverage: 'Major corridors' },
              { icon: '📺', name: 'Childline 1098 Integration', status: 'active', coverage: 'National' },
            ].map(channel => (
              <div key={channel.name} className="flex items-center justify-between"
                style={{ padding: '10px 0', borderBottom: '1px solid var(--color-border)' }}>
                <div className="flex items-center gap-2">
                  <span>{channel.icon}</span>
                  <div>
                    <div className="text-sm" style={{ fontWeight: 500 }}>{channel.name}</div>
                    <div className="text-xs text-muted">{channel.coverage}</div>
                  </div>
                </div>
                <span className={`badge ${channel.status === 'active' ? 'badge-found' : 'badge-normal'}`}>
                  {channel.status}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default CommunityPage;
