import React from 'react';
import { useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { casesApi, alertsApi, sightingsApi, searchApi } from '../services/api';

const CaseDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const caseId = Number(id);

  const { data: caseData, isLoading } = useQuery({
    queryKey: ['case', caseId],
    queryFn: () => casesApi.get(caseId),
    enabled: !!caseId,
  });

  const { data: sightingsData } = useQuery({
    queryKey: ['sightings', caseId],
    queryFn: () => sightingsApi.list({ missing_person_id: caseId }),
    enabled: !!caseId,
  });

  const { data: alertsData } = useQuery({
    queryKey: ['alerts', caseId],
    queryFn: () => alertsApi.list({ missing_person_id: caseId }),
    enabled: !!caseId,
  });

  const handleRoutePredict = async () => {
    try {
      const { data } = await searchApi.predictRoute(caseId);
      alert(`Route prediction complete!\n${data.predicted_routes?.length || 0} routes found.\nCheckpoints alerted: ${data.predicted_routes?.[0]?.checkpoints?.length || 0}`);
    } catch {
      alert('Route prediction failed. Check API connection.');
    }
  };

  if (isLoading) {
    return <div style={{ textAlign: 'center', padding: '80px' }}><div className="spinner" style={{ margin: '0 auto' }}></div></div>;
  }

  const c = caseData?.data;
  if (!c) return <div className="card">Case not found.</div>;

  const daysMissing = Math.floor((Date.now() - new Date(c.date_missing).getTime()) / 86400000);

  return (
    <div>
      <div className="flex items-center gap-4 mb-6">
        <Link to="/cases" className="btn btn-secondary">← Cases</Link>
        <div>
          <h1 style={{ fontSize: '1.5rem', marginBottom: '4px' }}>{c.full_name}</h1>
          <p className="text-muted text-sm" style={{ fontFamily: 'monospace' }}>{c.case_number}</p>
        </div>
        <div style={{ marginLeft: 'auto', display: 'flex', gap: '8px' }}>
          <span className={`badge badge-${c.priority}`}>{c.priority}</span>
          <span className={`badge badge-${c.status}`}>{c.status}</span>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '24px' }}>
        {/* Main details */}
        <div>
          <div className="card mb-6">
            <h2 style={{ fontSize: '1rem', marginBottom: '16px' }}>Case Details</h2>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
              {[
                ['Age', c.age_at_disappearance ?? '—'],
                ['Gender', c.gender ?? '—'],
                ['Case Type', c.case_type],
                ['Days Missing', `${daysMissing} days`],
                ['Last Seen', c.last_seen_location || '—'],
                ['State', c.state || '—'],
                ['Reporting Station', c.reporting_station || '—'],
                ['Date Missing', new Date(c.date_missing).toLocaleString('en-IN')],
              ].map(([label, value]) => (
                <div key={label as string}>
                  <div className="text-xs text-muted" style={{ marginBottom: '2px' }}>{label}</div>
                  <div style={{ fontWeight: 500 }}>{value}</div>
                </div>
              ))}
            </div>
            {c.circumstances && (
              <div style={{ marginTop: '16px', paddingTop: '16px', borderTop: '1px solid var(--color-border)' }}>
                <div className="text-xs text-muted" style={{ marginBottom: '4px' }}>Circumstances</div>
                <p className="text-sm">{c.circumstances}</p>
              </div>
            )}
          </div>

          {/* Sightings */}
          <div className="card mb-6">
            <h2 style={{ fontSize: '1rem', marginBottom: '16px' }}>
              Sightings ({sightingsData?.data?.length || 0})
            </h2>
            {sightingsData?.data?.length ? (
              <table className="table">
                <thead>
                  <tr>
                    <th>Date</th>
                    <th>Location</th>
                    <th>Source</th>
                    <th>Confidence</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {sightingsData.data.map((s: any) => (
                    <tr key={s.id}>
                      <td className="text-sm">{new Date(s.sighted_at).toLocaleDateString('en-IN')}</td>
                      <td>{s.location_name || '—'}</td>
                      <td><span className="badge badge-normal">{s.source}</span></td>
                      <td>
                        {s.confidence_score ? (
                          <div>
                            <div style={{ marginBottom: '4px', fontSize: '0.75rem' }}>
                              {Math.round(s.confidence_score * 100)}%
                            </div>
                            <div className="confidence-bar">
                              <div
                                className={`confidence-fill ${s.confidence_score >= 0.75 ? 'high' : s.confidence_score >= 0.5 ? 'medium' : 'low'}`}
                                style={{ width: `${s.confidence_score * 100}%` }}
                              />
                            </div>
                          </div>
                        ) : '—'}
                      </td>
                      <td><span className={`badge badge-${s.status === 'verified' ? 'found' : 'active'}`}>{s.status}</span></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <p className="text-muted text-sm">No sightings recorded yet.</p>
            )}
          </div>

          {/* Alerts */}
          <div className="card">
            <h2 style={{ fontSize: '1rem', marginBottom: '16px' }}>
              Alerts ({alertsData?.data?.length || 0})
            </h2>
            {alertsData?.data?.length ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                {alertsData.data.map((a: any) => (
                  <div key={a.id} className={`alert-banner ${a.severity === 'critical' ? 'critical' : 'info'}`}>
                    <div style={{ flex: 1 }}>
                      <div style={{ fontWeight: 600, fontSize: '0.875rem' }}>{a.title}</div>
                      <div className="text-xs text-muted">{a.alert_type} · {a.channel} · {a.status}</div>
                    </div>
                    <span className={`badge badge-${a.severity}`}>{a.severity}</span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-muted text-sm">No alerts for this case.</p>
            )}
          </div>
        </div>

        {/* Actions panel */}
        <div>
          <div className="card mb-6">
            <h2 style={{ fontSize: '1rem', marginBottom: '16px' }}>Intelligence Actions</h2>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              <button className="btn btn-primary" style={{ justifyContent: 'center' }} onClick={handleRoutePredict}>
                🗺️ Activate Route Predictor
              </button>
              <Link to="/search" className="btn btn-secondary" style={{ justifyContent: 'center' }}>
                🔍 Face Search
              </Link>
              <button className="btn btn-secondary" style={{ justifyContent: 'center' }}
                onClick={() => alert('Community broadcast would notify reporters in 50km radius')}>
                📢 Community Broadcast
              </button>
              <button className="btn btn-secondary" style={{ justifyContent: 'center' }}
                onClick={() => alert('Age progression would generate projected photos')}>
                🧬 Generate Age Progression
              </button>
            </div>
          </div>

          {c.primary_photo_url && (
            <div className="card">
              <h2 style={{ fontSize: '1rem', marginBottom: '12px' }}>Photo</h2>
              <img
                src={c.primary_photo_url}
                alt={c.full_name}
                style={{ width: '100%', borderRadius: '4px', objectFit: 'cover' }}
              />
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default CaseDetailPage;
