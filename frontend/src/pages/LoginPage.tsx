import React, { useState } from 'react';
import { useDispatch } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { authApi } from '../services/api';
import { setCredentials } from '../slices/authSlice';

const LoginPage: React.FC = () => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const [badgeNumber, setBadgeNumber] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const { data: tokenData } = await authApi.login(badgeNumber, password);
      const { data: userData } = await authApi.me();
      // Temporarily set token for me() call
      localStorage.setItem('access_token', tokenData.access_token);
      dispatch(setCredentials({
        user: userData,
        accessToken: tokenData.access_token,
        refreshToken: tokenData.refresh_token,
      }));
      navigate('/dashboard');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Authentication failed. Please check your credentials.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      background: 'var(--color-bg)',
      padding: '24px',
    }}>
      <div style={{ width: '100%', maxWidth: '400px' }}>
        {/* Logo */}
        <div style={{ textAlign: 'center', marginBottom: '40px' }}>
          <h1 style={{ fontSize: '3rem', color: 'var(--color-accent)', letterSpacing: '0.2em' }}>
            DRISHTI
          </h1>
          <p style={{ color: 'var(--color-text-muted)', fontSize: '0.75rem', letterSpacing: '0.1em' }}>
            DISTRIBUTED REAL-TIME INTELLIGENCE SYSTEM
          </p>
          <p style={{ color: 'var(--color-text-muted)', fontSize: '0.7rem', letterSpacing: '0.1em' }}>
            FOR HUMAN IDENTIFICATION & TRAFFICKING INTERCEPTION
          </p>
        </div>

        <div className="card">
          <h2 style={{ marginBottom: '24px', fontSize: '1.25rem' }}>Officer Sign In</h2>

          {error && (
            <div className="alert-banner critical" style={{ marginBottom: '16px' }}>
              ⚠️ {error}
            </div>
          )}

          <form onSubmit={handleLogin}>
            <div className="form-group">
              <label className="form-label">Badge Number</label>
              <input
                type="text"
                className="form-input"
                placeholder="Enter your badge number"
                value={badgeNumber}
                onChange={e => setBadgeNumber(e.target.value)}
                required
              />
            </div>

            <div className="form-group">
              <label className="form-label">Password</label>
              <input
                type="password"
                className="form-input"
                placeholder="Enter your password"
                value={password}
                onChange={e => setPassword(e.target.value)}
                required
              />
            </div>

            <button
              type="submit"
              className="btn btn-primary"
              style={{ width: '100%', justifyContent: 'center', marginTop: '8px' }}
              disabled={loading}
            >
              {loading ? '⏳ Authenticating...' : '🔐 Sign In Securely'}
            </button>
          </form>
        </div>

        <p style={{
          textAlign: 'center',
          color: 'var(--color-text-muted)',
          fontSize: '0.7rem',
          marginTop: '24px',
          lineHeight: '1.8',
        }}>
          🔒 This system is restricted to authorized law enforcement officers.<br/>
          All access is logged and audited. DPDP Act 2023 compliant.
        </p>
      </div>
    </div>
  );
};

export default LoginPage;
