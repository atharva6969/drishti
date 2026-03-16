import React from 'react';
import { BrowserRouter as Router, Routes, Route, NavLink } from 'react-router-dom';
import PoliceDashboard from './pages/PoliceDashboard';
import FamilyPortal from './pages/FamilyPortal';
import NGODashboard from './pages/NGODashboard';
import './styles/App.css';

function App() {
  return (
    <Router>
      <div className="app">
        <nav className="navbar">
          <div className="nav-brand">
            <span className="nav-logo">👁</span>
            <span className="nav-title">DRISHTI</span>
            <span className="nav-subtitle">Anti-Trafficking Intelligence</span>
          </div>
          <ul className="nav-links">
            <li><NavLink to="/" end>Police Dashboard</NavLink></li>
            <li><NavLink to="/family">Family Portal</NavLink></li>
            <li><NavLink to="/ngo">NGO Dashboard</NavLink></li>
          </ul>
        </nav>

        <main className="main-content">
          <Routes>
            <Route path="/" element={<PoliceDashboard />} />
            <Route path="/family" element={<FamilyPortal />} />
            <Route path="/ngo" element={<NGODashboard />} />
          </Routes>
        </main>

        <footer className="footer">
          <p>DRISHTI System v1.0 | In partnership with AHTU, NCPCR &amp; Childline India Foundation</p>
          <p>Emergency: 100 (Police) | 1098 (Childline) | 1800-419-0600 (AHTU)</p>
        </footer>
      </div>
    </Router>
  );
}

export default App;
