import React, { useState, useEffect } from 'react';
import { missingPersonsAPI } from '../services/api';

function CaseManager() {
  const [cases, setCases] = useState([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState('active');
  const [selectedCase, setSelectedCase] = useState(null);
  const [updating, setUpdating] = useState(false);

  useEffect(() => {
    const fetchCases = async () => {
      setLoading(true);
      try {
        const params = statusFilter ? { status: statusFilter } : {};
        const response = await missingPersonsAPI.list(params);
        setCases(response.data);
      } catch {
        setCases([]);
      } finally {
        setLoading(false);
      }
    };
    fetchCases();
  }, [statusFilter]);

  const handleStatusUpdate = async (caseId, newStatus) => {
    setUpdating(true);
    try {
      await missingPersonsAPI.updateStatus(caseId, { status: newStatus });
      setCases((prev) =>
        prev.map((c) => (c.id === caseId ? { ...c, status: newStatus } : c))
      );
      if (selectedCase?.id === caseId) {
        setSelectedCase((prev) => ({ ...prev, status: newStatus }));
      }
    } catch (err) {
      alert('Failed to update status.');
    } finally {
      setUpdating(false);
    }
  };

  return (
    <div>
      <div className="card">
        <div className="card-header">
          <span className="card-title">📁 Case Manager</span>
          <select
            className="form-select"
            style={{ width: 'auto', padding: '6px 12px' }}
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
          >
            <option value="">All Cases</option>
            <option value="active">Active</option>
            <option value="found">Found</option>
            <option value="closed">Closed</option>
          </select>
        </div>

        {loading ? (
          <div className="loading"><div className="spinner"></div></div>
        ) : cases.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">📁</div>
            <p>No cases found</p>
          </div>
        ) : (
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Case #</th>
                  <th>Name</th>
                  <th>Age</th>
                  <th>State</th>
                  <th>Last Seen</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {cases.map((c) => (
                  <tr
                    key={c.id}
                    onClick={() => setSelectedCase(c)}
                    style={{ cursor: 'pointer' }}
                  >
                    <td><code style={{ fontSize: 12 }}>{c.case_number}</code></td>
                    <td><strong>{c.name}</strong></td>
                    <td>{c.age || '—'}</td>
                    <td>{c.state || '—'}</td>
                    <td style={{ maxWidth: 200, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                      {c.last_seen_location || '—'}
                    </td>
                    <td><span className={`badge badge-${c.status}`}>{c.status}</span></td>
                    <td>
                      {c.status === 'active' && (
                        <button
                          className="btn btn-success btn-sm"
                          onClick={(e) => { e.stopPropagation(); handleStatusUpdate(c.id, 'found'); }}
                          disabled={updating}
                        >
                          ✅ Mark Found
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Case Detail Panel */}
      {selectedCase && (
        <div className="card" style={{ marginTop: 20 }}>
          <div className="card-header">
            <span className="card-title">Case Details: {selectedCase.name}</span>
            <button className="btn btn-outline btn-sm" onClick={() => setSelectedCase(null)}>✕ Close</button>
          </div>
          <div className="form-row">
            <div>
              <p><strong>Case Number:</strong> <code>{selectedCase.case_number}</code></p>
              <p><strong>Name:</strong> {selectedCase.name}</p>
              <p><strong>Age:</strong> {selectedCase.age || 'Unknown'}</p>
              <p><strong>Gender:</strong> {selectedCase.gender || 'Unknown'}</p>
              <p><strong>Status:</strong> <span className={`badge badge-${selectedCase.status}`}>{selectedCase.status}</span></p>
              <p><strong>State:</strong> {selectedCase.state || 'Unknown'}</p>
              <p><strong>District:</strong> {selectedCase.district || 'Unknown'}</p>
            </div>
            <div>
              <p><strong>Last Seen:</strong> {selectedCase.last_seen_location || 'Unknown'}</p>
              <p><strong>Reported By:</strong> {selectedCase.reported_by || 'Unknown'}</p>
              <p><strong>Contact:</strong> {selectedCase.contact_number || 'Unknown'}</p>
              <p><strong>Physical Description:</strong> {selectedCase.physical_description || 'N/A'}</p>
              <p><strong>Clothing:</strong> {selectedCase.clothing_description || 'N/A'}</p>
              <p><strong>Created:</strong> {selectedCase.created_at ? new Date(selectedCase.created_at).toLocaleString('en-IN') : '—'}</p>
            </div>
          </div>
          <div style={{ marginTop: 16, display: 'flex', gap: 8 }}>
            {selectedCase.status === 'active' && (
              <>
                <button className="btn btn-success btn-sm" onClick={() => handleStatusUpdate(selectedCase.id, 'found')} disabled={updating}>
                  ✅ Mark Found
                </button>
                <button className="btn btn-outline btn-sm" onClick={() => handleStatusUpdate(selectedCase.id, 'closed')} disabled={updating}>
                  📁 Close Case
                </button>
              </>
            )}
            <button className="btn btn-primary btn-sm">🗺️ View Routes</button>
          </div>
        </div>
      )}
    </div>
  );
}

export default CaseManager;
