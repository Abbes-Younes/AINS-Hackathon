import React from 'react';
import { NavLink } from 'react-router-dom';

export const Sidebar = () => {
  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <h2>AINS Engine</h2>
      </div>
      <nav className="sidebar-nav">
        <NavLink to="/" end className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
          <span className="nav-icon">🏠</span>
          <span className="nav-label">Dashboard</span>
        </NavLink>
        <NavLink to="/diagnostic" end className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
          <span className="nav-icon">📋</span>
          <span className="nav-label">Diagnostic</span>
        </NavLink>
        <NavLink to="/scoring" end className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
          <span className="nav-icon">📊</span>
          <span className="nav-label">Scoring</span>
        </NavLink>
        <NavLink to="/roadmap" end className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
          <span className="nav-icon">🗺️</span>
          <span className="nav-label">Roadmap</span>
        </NavLink>
        <NavLink to="/resources" end className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
          <span className="nav-icon">🔍</span>
          <span className="nav-label">Resources</span>
        </NavLink>
        <NavLink to="/assistant" end className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
          <span className="nav-icon">💬</span>
          <span className="nav-label">Assistant</span>
        </NavLink>
      </nav>
      <div className="footer">
        <p>AINS Hackathon 2026</p>
        <p>Powered by AI</p>
      </div>
    </aside>
  );
};