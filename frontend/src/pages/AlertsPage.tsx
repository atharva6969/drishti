import React from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { alertsApi } from '../services/api';

const AlertsPage: React.FC = () => {
  const qc = useQueryClient();
  const { data, isLoading } = useQuery({
    queryKey: ['alerts'],
    queryFn: () => alertsApi.list({ limit: 50 }),
  });

  const acknowledge = useMutation({
    mutationFn: (id: number) => alertsApi.acknowledge(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['alerts'] }),
  });

  const alerts = data?.data || [];

  const severityColor: Record<string, string> = {
    critical: 'critical',
    high: 'warning',
    normal: 'info',
    low: 'info',
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 style={{ fontSize: '1.75rem', marginBottom: '4px' }}>Alerts & Notifications</h1>
          <p className="text-muted text-sm">{alerts.length} total alerts</p>
        </div>
      </div>

      {isLoading ? (
        <div style={{ textAlign: 'center', padding: '80px' }}>
          <div className="spinner" style={{ margin: '0 auto' }}></div>
        </div>
      ) : alerts.length === 0 ? (
        <div className="card" style={{ textAlign: 'center', padding: '60px' }}>
          <div style={{ fontSize: '3rem', marginBottom: '16px' }}>✅</div>
          <h2>No Active Alerts</h2>
          <p className="text-muted text-sm">The system is monitoring all active cases.</p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {alerts.map((alert: any) => (
            <div key={alert.id} className={`alert-banner ${severityColor[alert.severity] || 'info'}`}
              style={{ padding: '16px' }}>
              <div style={{ flex: 1 }}>
                <div className="flex items-center gap-2 mb-1">
                  <span style={{ fontWeight: 700, fontSize: '1rem' }}>{alert.title}</span>
                  <span className={`badge badge-${alert.severity}`}>{alert.severity}</span>
                  {alert.status === 'pending' && (
                    <span className="badge" style={{ background: 'rgba(249,168,37,0.2)', color: '#ffa726' }}>PENDING</span>
                  )}
                </div>
                <p className="text-sm" style={{ marginBottom: '8px' }}>{alert.message}</p>
                <div className="text-xs text-muted">
                  Type: {alert.alert_type} · Channel: {alert.channel} ·
                  Created: {new Date(alert.created_at).toLocaleString('en-IN')}
                  {alert.acknowledged_at && ` · Acknowledged: ${new Date(alert.acknowledged_at).toLocaleString('en-IN')}`}
                </div>
              </div>
              {!alert.acknowledged_at && (
                <button
                  className="btn btn-secondary"
                  style={{ minWidth: '120px', justifyContent: 'center' }}
                  onClick={() => acknowledge.mutate(alert.id)}
                  disabled={acknowledge.isPending}
                >
                  ✓ Acknowledge
                </button>
              )}
              {alert.acknowledged_at && (
                <span className="badge badge-found">ACKNOWLEDGED</span>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default AlertsPage;
