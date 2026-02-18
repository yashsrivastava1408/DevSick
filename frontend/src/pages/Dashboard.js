import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import StatusBadge from '../components/StatusBadge';
import { getIncidents, getStats, simulateScenario, resetSimulation, getGovernanceStatus, toggleGovernanceMode } from '../api/client';
import { Activity, AlertTriangle, CheckCircle, Rocket, RefreshCw, Trash2, Search, Zap, ShieldCheck } from '../components/Icons';
import './Dashboard.css';

function Dashboard() {
    const navigate = useNavigate();
    const [incidents, setIncidents] = useState([]);
    const [stats, setStats] = useState(null);
    const [loading, setLoading] = useState(true);
    const [simulating, setSimulating] = useState(false);
    const [autoPilot, setAutoPilot] = useState(false);
    const [governanceMode, setGovernanceMode] = useState('Protocol Alpha');

    const fetchData = useCallback(async () => {
        try {
            const [inc, st, gov] = await Promise.all([
                getIncidents(),
                getStats(),
                getGovernanceStatus()
            ]);
            setIncidents(inc);
            setStats(st);
            setAutoPilot(gov.auto_pilot);
            setGovernanceMode(gov.mode);
        } catch (err) {
            console.error('Failed to fetch data:', err);
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchData();
    }, [fetchData]);

    const handleSimulate = async () => {
        setSimulating(true);
        try {
            await simulateScenario();
            await fetchData();
        } catch (err) {
            console.error('Simulation failed:', err);
        } finally {
            setSimulating(false);
        }
    };

    const handleToggleGovernance = async () => {
        try {
            const res = await toggleGovernanceMode();
            setAutoPilot(res.auto_pilot);
            setGovernanceMode(res.mode);
        } catch (err) {
            console.error('Failed to toggle governance:', err);
        }
    };

    const handleReset = async () => {
        try {
            await resetSimulation();
            await fetchData();
        } catch (err) {
            console.error('Reset failed:', err);
        }
    };

    const formatTime = (ts) => {
        const d = new Date(ts);
        return d.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    };

    if (loading) {
        return (
            <div className="dashboard">
                <div className="loading-container">
                    <div className="spinner"></div>
                    <span>Loading dashboard...</span>
                </div>
            </div>
        );
    }

    const criticalCount = stats?.by_severity?.critical || 0;
    const pendingCount = stats?.by_status?.actions_pending || 0;
    const analyzedCount = stats?.by_status?.analyzed || 0;

    return (
        <div className="dashboard fade-in">
            <div className="dashboard-header">
                <div>
                    <h1>Incident Dashboard</h1>
                    <p>AI-powered incident detection, correlation, and root cause analysis</p>
                </div>
                <div className="header-actions">
                    <div className={`protocol-badge ${autoPilot ? 'omega' : 'alpha'}`} onClick={handleToggleGovernance}>
                        <div className="protocol-icon">
                            {autoPilot ? <Zap size={14} /> : <ShieldCheck size={14} />}
                        </div>
                        <div className="protocol-info">
                            <span className="protocol-label">Governance Mode</span>
                            <span className="protocol-name">{governanceMode}</span>
                        </div>
                        <div className="protocol-toggle">
                            <div className={`toggle-track ${autoPilot ? 'active' : ''}`}>
                                <div className="toggle-thumb"></div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Stats Bar */}
            <div className="stats-bar">
                <div className="stat-card">
                    <div className="stat-label">Total Incidents</div>
                    <div className={`stat-value ${stats?.total_incidents > 0 ? 'info' : ''}`}>
                        {stats?.total_incidents || 0}
                    </div>
                </div>
                <div className="stat-card">
                    <div className="stat-label">Critical</div>
                    <div className={`stat-value ${criticalCount > 0 ? 'critical' : ''}`}>
                        {criticalCount}
                    </div>
                </div>
                <div className="stat-card">
                    <div className="stat-label">Pending Approval</div>
                    <div className={`stat-value ${pendingCount > 0 ? 'warning' : ''}`}>
                        {pendingCount}
                    </div>
                </div>
                <div className="stat-card">
                    <div className="stat-label">Analyzed</div>
                    <div className={`stat-value ${analyzedCount > 0 ? 'success' : ''}`}>
                        {analyzedCount}
                    </div>
                </div>
            </div>

            {/* Actions */}
            <div className="actions-bar">
                <button
                    className="btn btn-primary"
                    onClick={handleSimulate}
                    disabled={simulating}
                >
                    {simulating ? (
                        <><div className="spinner" style={{ width: 14, height: 14, borderWidth: 2 }}></div> Running Pipeline...</>
                    ) : (
                        <><Rocket size={16} /> Simulate Incidents</>
                    )}
                </button>
                <button
                    className="btn btn-secondary"
                    onClick={fetchData}
                >
                    <RefreshCw size={16} /> Refresh
                </button>
                {incidents.length > 0 && (
                    <button
                        className="btn btn-danger"
                        onClick={handleReset}
                    >
                        <Trash2 size={16} /> Reset All
                    </button>
                )}
            </div>

            {/* Incident Table */}
            <div className="incident-table-card">
                <div className="table-header">
                    <h2>Incidents</h2>
                    <span className="table-count">{incidents.length} total</span>
                </div>

                {incidents.length === 0 ? (
                    <div className="empty-state">
                        <div className="empty-icon"><Search size={48} strokeWidth={1} /></div>
                        <h3>No incidents detected</h3>
                        <p>Click "Simulate Incidents" to run demo scenarios through the AI reasoning pipeline.</p>
                    </div>
                ) : (
                    <table className="incident-table">
                        <thead>
                            <tr>
                                <th>Severity</th>
                                <th>Incident</th>
                                <th>Status</th>
                                <th>Services</th>
                                <th>Time</th>
                            </tr>
                        </thead>
                        <tbody>
                            {incidents.map((inc) => (
                                <tr key={inc.id} onClick={() => navigate(`/incidents/${inc.id}`)}>
                                    <td>
                                        <StatusBadge type="severity" value={inc.severity} />
                                    </td>
                                    <td>
                                        <span className="incident-title">{inc.title}</span>
                                    </td>
                                    <td>
                                        <StatusBadge type="status" value={inc.status} />
                                    </td>
                                    <td>
                                        <div className="incident-services">
                                            {inc.affected_services?.slice(0, 3).map((s) => (
                                                <span key={s} className="service-tag">{s}</span>
                                            ))}
                                            {inc.affected_services?.length > 3 && (
                                                <span className="service-tag">+{inc.affected_services.length - 3}</span>
                                            )}
                                        </div>
                                    </td>
                                    <td>
                                        <span className="incident-time">{formatTime(inc.created_at)}</span>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                )}
            </div>
        </div>
    );
}

export default Dashboard;
