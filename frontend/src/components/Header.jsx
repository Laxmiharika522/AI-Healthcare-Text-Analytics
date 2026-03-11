import React from 'react';
import { Bell, RefreshCw, Wifi } from 'lucide-react';
import './Header.css';

export default function Header({ title, subtitle }) {
  return (
    <header className="app-header">
      <div className="header-left">
        <h2 className="header-title">{title}</h2>
        {subtitle && <p className="header-subtitle">{subtitle}</p>}
      </div>
      <div className="header-right">
        <div className="header-status">
          <Wifi size={13} color="#10b981" />
          <span>Backend Connected</span>
        </div>
        <div className="header-badge">
          <Bell size={16} />
        </div>
      </div>
    </header>
  );
}
