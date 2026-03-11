import React, { useState } from 'react';
import { NavLink } from 'react-router-dom';
import {
  Activity, Search, FileText, Brain, HelpCircle,
  BarChart2, Users, Stethoscope, ChevronRight, Database
} from 'lucide-react';
import './Sidebar.css';

const navItems = [
  { path: '/', label: 'Dashboard', icon: BarChart2, color: '#00d4ff' },
  { path: '/analyzer', label: 'Text Analyzer', icon: FileText, color: '#f59e0b' },
  { path: '/predictor', label: 'Disease Predictor', icon: Activity, color: '#f43f5e' },
  { path: '/search', label: 'Doc Search', icon: Search, color: '#8b5cf6' },
  { path: '/summarizer', label: 'Summarizer', icon: Brain, color: '#10b981' },
  { path: '/assistant', label: 'Research Q&A', icon: HelpCircle, color: '#3b82f6' },
  { path: '/patients', label: 'Patients', icon: Users, color: '#f97316' },
];

export default function Sidebar() {
  const [collapsed, setCollapsed] = useState(false);

  return (
    <aside className={`sidebar ${collapsed ? 'collapsed' : ''}`}>
      <div className="sidebar-header">
        <div className="sidebar-logo">
          <Stethoscope size={22} color="#00d4ff" />
          {!collapsed && <span>HealthAI</span>}
        </div>
        <button className="collapse-btn" onClick={() => setCollapsed(!collapsed)}>
          <ChevronRight size={16} style={{ transform: collapsed ? 'rotate(0deg)' : 'rotate(180deg)', transition: '0.3s' }} />
        </button>
      </div>

      {!collapsed && (
        <div className="sidebar-section-label">NAVIGATION</div>
      )}

      <nav className="sidebar-nav">
        {navItems.map(({ path, label, icon: Icon, color }) => (
          <NavLink
            key={path}
            to={path}
            className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
            title={collapsed ? label : ''}
          >
            <div className="nav-icon" style={{ '--item-color': color }}>
              <Icon size={18} />
            </div>
            {!collapsed && <span className="nav-label">{label}</span>}
            {!collapsed && <ChevronRight size={14} className="nav-arrow" />}
          </NavLink>
        ))}
      </nav>

      {!collapsed && (
        <div className="sidebar-footer">
          <div className="sidebar-db-badge">
            <Database size={13} />
            <span>SQLite • 4 Tables</span>
          </div>
          <div className="sidebar-version">v1.0.0</div>
        </div>
      )}
    </aside>
  );
}
