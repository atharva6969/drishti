import React, { useRef, useState } from 'react';
import { searchApi } from '../services/api';

const SearchPage: React.FC = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<any>(null);
  const [useClothing, setUseClothing] = useState(true);
  const [useBody, setUseBody] = useState(true);
  const fileRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      setPreview(URL.createObjectURL(file));
      setResults(null);
    }
  };

  const handleSearch = async () => {
    if (!selectedFile) return;
    setLoading(true);
    try {
      const formData = new FormData();
      formData.append('image', selectedFile);
      formData.append('use_clothing', String(useClothing));
      formData.append('use_body', String(useBody));
      const { data } = await searchApi.multimodal(formData);
      setResults(data);
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Search failed. Please check API connection.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h1 style={{ fontSize: '1.75rem', marginBottom: '4px' }}>AI-Powered Identity Search</h1>
      <p className="text-muted text-sm mb-6">Multimodal matching — face, clothing, body proportions</p>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px' }}>
        {/* Upload panel */}
        <div className="card">
          <h2 style={{ fontSize: '1rem', marginBottom: '16px' }}>Upload Query Image</h2>

          {/* Drop zone */}
          <div
            style={{
              border: '2px dashed var(--color-border)',
              borderRadius: '8px',
              padding: '40px',
              textAlign: 'center',
              cursor: 'pointer',
              marginBottom: '16px',
              transition: 'border-color 0.2s',
            }}
            onClick={() => fileRef.current?.click()}
          >
            {preview ? (
              <img src={preview} alt="Query" style={{ maxHeight: '200px', maxWidth: '100%', borderRadius: '4px' }} />
            ) : (
              <>
                <div style={{ fontSize: '3rem', marginBottom: '12px' }}>📷</div>
                <p style={{ color: 'var(--color-text-muted)' }}>Click to upload or drag & drop</p>
                <p className="text-xs text-muted">JPEG, PNG, WebP — max 10MB</p>
              </>
            )}
          </div>
          <input ref={fileRef} type="file" accept="image/*" style={{ display: 'none' }} onChange={handleFileChange} />

          {/* Signal toggles */}
          <div style={{ marginBottom: '16px' }}>
            <h3 style={{ fontSize: '0.875rem', marginBottom: '12px', color: 'var(--color-text-muted)' }}>
              Active Identity Signals
            </h3>
            {[
              { label: '🧠 Face Recognition (ArcFace)', key: 'face', enabled: true, fixed: true },
              { label: '🎽 Clothing Detection (CLIP)', key: 'clothing', enabled: useClothing, onChange: setUseClothing },
              { label: '📐 Body Biometrics (MediaPipe)', key: 'body', enabled: useBody, onChange: setUseBody },
            ].map(signal => (
              <div key={signal.key} style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 0', borderBottom: '1px solid var(--color-border)' }}>
                <span className="text-sm">{signal.label}</span>
                <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: signal.fixed ? 'default' : 'pointer' }}>
                  <input
                    type="checkbox"
                    checked={signal.enabled}
                    disabled={signal.fixed}
                    onChange={e => signal.onChange?.(e.target.checked)}
                  />
                  <span className="text-xs text-muted">{signal.enabled ? 'ON' : 'OFF'}</span>
                </label>
              </div>
            ))}
          </div>

          <button
            className="btn btn-primary"
            style={{ width: '100%', justifyContent: 'center' }}
            onClick={handleSearch}
            disabled={!selectedFile || loading}
          >
            {loading ? '⏳ Searching...' : '🔍 Search Missing Persons Database'}
          </button>
        </div>

        {/* Results panel */}
        <div className="card">
          <h2 style={{ fontSize: '1rem', marginBottom: '16px' }}>Search Results</h2>

          {!results && !loading && (
            <div style={{ textAlign: 'center', padding: '60px 20px' }}>
              <div style={{ fontSize: '3rem', marginBottom: '12px' }}>🔍</div>
              <p className="text-muted text-sm">Upload an image and run search to see matches</p>
            </div>
          )}

          {loading && (
            <div style={{ textAlign: 'center', padding: '60px 20px' }}>
              <div className="spinner" style={{ margin: '0 auto 16px' }}></div>
              <p className="text-muted text-sm">Running multimodal AI analysis...</p>
            </div>
          )}

          {results && (
            <div>
              <div className="flex items-center gap-2 mb-4">
                <span className="badge badge-normal">
                  Signals Used: Face{results.signals_used?.clothing ? ', Clothing' : ''}{results.signals_used?.body ? ', Body' : ''}
                </span>
              </div>

              {results.matches?.length === 0 ? (
                <div style={{ textAlign: 'center', padding: '40px' }}>
                  <div style={{ fontSize: '2rem', marginBottom: '8px' }}>✅</div>
                  <p className="text-muted">No matches found above confidence threshold.</p>
                  <p className="text-xs text-muted">If you believe there should be a match, try adjusting the threshold.</p>
                </div>
              ) : (
                results.matches?.map((match: any, i: number) => (
                  <div key={i} style={{ padding: '12px', border: '1px solid var(--color-border)', borderRadius: '6px', marginBottom: '8px' }}>
                    <div className="flex items-center justify-between mb-2">
                      <span style={{ fontWeight: 600 }}>{match.full_name}</span>
                      <span className={`badge ${match.combined_score >= 0.75 ? 'badge-critical' : 'badge-high'}`}>
                        {Math.round(match.combined_score * 100)}% Match
                      </span>
                    </div>
                    <div className="text-xs text-muted">{match.case_number}</div>
                    <div className="confidence-bar" style={{ marginTop: '8px' }}>
                      <div
                        className={`confidence-fill ${match.combined_score >= 0.75 ? 'high' : 'medium'}`}
                        style={{ width: `${match.combined_score * 100}%` }}
                      />
                    </div>
                  </div>
                ))
              )}

              {results.note && (
                <p className="text-xs text-muted" style={{ marginTop: '16px', padding: '8px', background: 'rgba(255,255,255,0.05)', borderRadius: '4px' }}>
                  ℹ️ {results.note}
                </p>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default SearchPage;
