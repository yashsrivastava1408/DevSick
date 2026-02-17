import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { getHealth } from '../api/client';
import './Sidebar.css';

function Sidebar() {
    const location = useLocation();
    const [health, setHealth] = useState(null);

    useEffect(() => {
        getHealth()
            .then(setHealth)
            .catch(() => setHealth(null));

        const interval = setInterval(() => {
            getHealth()
                .then(setHealth)
                .catch(() => setHealth(null));
        }, 30000);
        return () => clearInterval(interval);
    }, []);

    return (
        <nav className="sidebar">
            <div className="sidebar-header">
                <Link to="/" className="sidebar-logo">
                    <div className="logo-icon">D</div>
                    <div className="logo-text">
                        <h1>Devsick</h1>
                        <span>Incident Intelligence</span>
                    </div>
                </Link>
            </div>

            <div className="sidebar-nav">
                <div className="nav-section-label">Operations</div>
                <Link
                    to="/"
                    className={`nav-item ${location.pathname === '/' ? 'active' : ''}`}
                >
                    <span className="nav-icon">📊</span>
                    Dashboard
                </Link>

                <div className="nav-section-label">Platform</div>
                <div className="nav-item" style={{ opacity: 0.5, cursor: 'default' }}>
                    <span className="nav-icon">🔗</span>
                    Service Map
                </div>
                <div className="nav-item" style={{ opacity: 0.5, cursor: 'default' }}>
                    <span className="nav-icon">📋</span>
                    Runbooks
                </div>
                <div className="nav-item" style={{ opacity: 0.5, cursor: 'default' }}>
                    <span className="nav-icon">⚙️</span>
                    Settings
                </div>
            </div>

            <div className="sidebar-footer">
                <div className="system-status">
                    <span className={`status-dot ${health ? '' : 'offline'}`}></span>
                    <span>
                        {health
                            ? `System Online${health.groq_configured ? ' • AI Active' : ' • AI Offline'}`
                            : 'Connecting...'}
                    </span>
                </div>
            </div>
        </nav>
    );
}

export default Sidebar;
