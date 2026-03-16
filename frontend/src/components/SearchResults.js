import React, { useState } from 'react';
import { searchAPI } from '../services/api';

function SearchResults() {
  const [officerId, setOfficerId] = useState('');
  const [selectedFile, setSelectedFile] = useState(null);
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleFileChange = (e) => {
    setSelectedFile(e.target.files[0]);
    setResults(null);
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!selectedFile) { setError('Please select an image file.'); return; }
    if (!officerId.trim()) { setError('Officer ID is required for audit logging.'); return; }

    setLoading(true);
    setError(null);

    try {
      const response = await searchAPI.byFace(officerId, selectedFile);
      setResults(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Search failed. Ensure backend is running.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card">
      <div className="card-header">
        <span className="card-title">🔍 Face Match Search</span>
      </div>

      <form onSubmit={handleSearch}>
        <div className="form-row">
          <div className="form-group">
            <label className="form-label">Officer ID (Audit Log)</label>
            <input
              className="form-input"
              placeholder="e.g. OFF-WB-1234"
              value={officerId}
              onChange={(e) => setOfficerId(e.target.value)}
            />
          </div>
          <div className="form-group">
            <label className="form-label">Upload Suspect/Sighting Image</label>
            <input type="file" accept="image/*" onChange={handleFileChange} style={{ fontSize: 14, padding: '8px 0' }} />
          </div>
        </div>

        {error && <div className="alert-banner error">{error}</div>}

        <button type="submit" className="btn btn-primary" disabled={loading}>
          {loading ? '⏳ Searching...' : '🔍 Search Database'}
        </button>
      </form>

      {results && (
        <div style={{ marginTop: 20 }}>
          <div className="section-title">
            Search Results ({results.total_matches} matches)
          </div>
          {results.matches.length === 0 ? (
            <div className="empty-state">
              <div className="empty-icon">🔍</div>
              <p>No matches found in active cases database</p>
            </div>
          ) : (
            <div className="table-container">
              <table>
                <thead>
                  <tr>
                    <th>Case #</th>
                    <th>Name</th>
                    <th>Age</th>
                    <th>Last Seen</th>
                    <th>Confidence</th>
                    <th>Action</th>
                  </tr>
                </thead>
                <tbody>
                  {results.matches.map((match, idx) => (
                    <tr key={idx}>
                      <td><code>{match.case_number}</code></td>
                      <td><strong>{match.name}</strong></td>
                      <td>{match.age || 'Unknown'}</td>
                      <td>{match.last_seen_location || 'Unknown'}</td>
                      <td>
                        <div>{Math.round(match.confidence * 100)}%</div>
                        <div className="confidence-bar" style={{ width: 80 }}>
                          <div
                            className={`confidence-fill ${match.confidence >= 0.8 ? 'high' : match.confidence >= 0.6 ? 'medium' : 'low'}`}
                            style={{ width: `${match.confidence * 100}%` }}
                          />
                        </div>
                      </td>
                      <td>
                        <button className="btn btn-primary btn-sm">View Case</button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {results.query_analysis && (
            <div style={{ marginTop: 16, padding: 12, background: '#f8f9ff', borderRadius: 8, fontSize: 13 }}>
              <strong>Analysis Details:</strong>
              <span style={{ marginLeft: 8 }}>
                Face detected: {results.query_analysis.detected ? '✅' : '❌'} |
                Confidence: {Math.round((results.query_analysis.confidence || 0) * 100)}% |
                Method: {results.query_analysis.method || 'stub'}
              </span>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default SearchResults;
