import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { casesApi } from '../services/api';

const CasesPage: React.FC = () => {
  const [page, setPage] = useState(1);
  const [status, setStatus] = useState('');
  const [priority, setPriority] = useState('');
  const [caseType, setCaseType] = useState('');

  const { data, isLoading } = useQuery({
    queryKey: ['cases', page, status, priority, caseType],
    queryFn: () => casesApi.list({
      page,
      page_size: 20,
      ...(status && { status }),
      ...(priority && { priority }),
      ...(caseType && { case_type: caseType }),
    }),
  });

  const cases = data?.data?.items || [];
  const total = data?.data?.total || 0;
  const totalPages = Math.ceil(total / 20);

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 style={{ fontSize: '1.75rem', marginBottom: '4px' }}>Missing Persons Cases</h1>
          <p className="text-muted text-sm">{total} total cases in database</p>
        </div>
        <Link to="/cases/new" className="btn btn-primary">+ Register New Case</Link>
      </div>

      {/* Filters */}
      <div className="card mb-6">
        <div style={{ display: 'flex', gap: '16px', flexWrap: 'wrap' }}>
          <div style={{ flex: 1, minWidth: '120px' }}>
            <label className="form-label">Status</label>
            <select className="form-select" value={status} onChange={e => { setStatus(e.target.value); setPage(1); }}>
              <option value="">All</option>
              <option value="active">Active</option>
              <option value="found">Found</option>
              <option value="closed">Closed</option>
              <option value="cold_case">Cold Case</option>
            </select>
          </div>
          <div style={{ flex: 1, minWidth: '120px' }}>
            <label className="form-label">Priority</label>
            <select className="form-select" value={priority} onChange={e => { setPriority(e.target.value); setPage(1); }}>
              <option value="">All</option>
              <option value="critical">Critical</option>
              <option value="high">High</option>
              <option value="normal">Normal</option>
              <option value="low">Low</option>
            </select>
          </div>
          <div style={{ flex: 1, minWidth: '120px' }}>
            <label className="form-label">Case Type</label>
            <select className="form-select" value={caseType} onChange={e => { setCaseType(e.target.value); setPage(1); }}>
              <option value="">All</option>
              <option value="missing">Missing</option>
              <option value="trafficking">Trafficking</option>
              <option value="abduction">Abduction</option>
              <option value="runaway">Runaway</option>
            </select>
          </div>
        </div>
      </div>

      {/* Table */}
      <div className="card">
        {isLoading ? (
          <div style={{ textAlign: 'center', padding: '40px' }}>
            <div className="spinner" style={{ margin: '0 auto' }}></div>
          </div>
        ) : (
          <>
            <table className="table">
              <thead>
                <tr>
                  <th>Case Number</th>
                  <th>Name</th>
                  <th>Age</th>
                  <th>Date Missing</th>
                  <th>Last Seen</th>
                  <th>Type</th>
                  <th>Priority</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {cases.map((c: any) => (
                  <tr key={c.id} onClick={() => window.location.href = `/cases/${c.id}`}>
                    <td style={{ fontFamily: 'monospace', fontSize: '0.75rem' }}>{c.case_number}</td>
                    <td style={{ fontWeight: 600 }}>{c.full_name}</td>
                    <td className="text-muted">{c.age_at_disappearance ?? '—'}</td>
                    <td className="text-sm">
                      {new Date(c.date_missing).toLocaleDateString('en-IN')}
                    </td>
                    <td className="text-sm text-muted">{c.last_seen_location || '—'}</td>
                    <td><span className="badge badge-normal">{c.case_type}</span></td>
                    <td><span className={`badge badge-${c.priority}`}>{c.priority}</span></td>
                    <td><span className={`badge badge-${c.status}`}>{c.status}</span></td>
                  </tr>
                ))}
              </tbody>
            </table>

            {cases.length === 0 && (
              <p className="text-muted text-sm" style={{ textAlign: 'center', padding: '24px' }}>
                No cases found matching the selected filters.
              </p>
            )}

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="flex items-center justify-between" style={{ marginTop: '16px', paddingTop: '16px', borderTop: '1px solid var(--color-border)' }}>
                <p className="text-sm text-muted">Page {page} of {totalPages}</p>
                <div className="flex gap-2">
                  <button className="btn btn-secondary" onClick={() => setPage(p => p - 1)} disabled={page === 1}>
                    ← Prev
                  </button>
                  <button className="btn btn-secondary" onClick={() => setPage(p => p + 1)} disabled={page === totalPages}>
                    Next →
                  </button>
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};

export default CasesPage;
