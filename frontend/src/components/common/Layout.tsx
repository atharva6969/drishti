import React from 'react';
import { Outlet, NavLink, useNavigate } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { RootState } from '../../store';
import { logout } from '../../slices/authSlice';

const NAV_ITEMS = [
  { path: '/dashboard', icon: '📊', label: 'Dashboard' },
  { path: '/cases', icon: '📋', label: 'Cases' },
  { path: '/search', icon: '🔍', label: 'AI Search' },
  { path: '/alerts', icon: '🚨', label: 'Alerts' },
  { path: '/map', icon: '🗺️', label: 'Live Map' },
  { path: '/community', icon: '👥', label: 'Community' },
];

const Layout: React.FC = () => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const user = useSelector((state: RootState) => state.auth.user);
  const unreadAlerts = useSelector((state: RootState) => state.alerts.unreadCount);

  const handleLogout = () => {
    dispatch(logout());
    navigate('/login');
  };

  return (
    <div className="layout">
      {/* Sidebar */}
      <nav className="sidebar">
        <div className="sidebar-logo">
          <h1>DRISHTI</h1>
          <p>MISSING PERSONS INTELLIGENCE</p>
        </div>

        <div style={{ padding: '16px 0' }}>
          {NAV_ITEMS.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
            >
              <span>{item.icon}</span>
              <span>{item.label}</span>
              {item.path === '/alerts' && unreadAlerts > 0 && (
                <span style={{
                  marginLeft: 'auto',
                  background: '#e53935',
                  color: 'white',
                  borderRadius: '10px',
                  padding: '2px 8px',
                  fontSize: '0.7rem',
                  fontWeight: 700,
                }}>
                  {unreadAlerts}
                </span>
              )}
            </NavLink>
          ))}
        </div>

        {/* User info */}
        <div style={{
          position: 'absolute',
          bottom: 0,
          left: 0,
          right: 0,
          padding: '16px 20px',
          borderTop: '1px solid var(--color-border)',
          background: 'var(--color-surface)',
        }}>
          <div style={{ marginBottom: '8px' }}>
            <div style={{ fontWeight: 600, fontSize: '0.875rem' }}>
              {user?.full_name || 'Officer'}
            </div>
            <div className="text-xs text-muted">
              {user?.badge_number} · {user?.role?.toUpperCase()}
            </div>
          </div>
          <button className="btn btn-secondary" style={{ width: '100%' }} onClick={handleLogout}>
            🚪 Sign Out
          </button>
        </div>
      </nav>

      {/* Main */}
      <main className="main-content">
        <header className="header">
          <div className="flex items-center gap-4" style={{ width: '100%' }}>
            <div style={{ fontWeight: 700, fontSize: '1rem', color: 'var(--color-accent)' }}>
              🔴 LIVE
            </div>
            <div className="text-sm text-muted">
              Anti-Human Trafficking Intelligence System
            </div>
            <div style={{ marginLeft: 'auto' }} className="text-sm text-muted">
              {new Date().toLocaleDateString('en-IN', {
                weekday: 'long',
                year: 'numeric',
                month: 'long',
                day: 'numeric',
              })}
            </div>
          </div>
        </header>

        <div className="page-content">
          <Outlet />
        </div>
      </main>
    </div>
  );
};

export default Layout;
