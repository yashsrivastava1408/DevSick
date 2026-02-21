import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import StatusBadge from '../components/StatusBadge';
import TelemetryGrid from '../components/TelemetryGrid';
import {
    getIncidents,
    getStats,
    simulateScenario,
    resetSimulation,
    getGovernanceStatus,
    toggleGovernanceMode
} from '../api/client';

import {
    RefreshCw,
    Trash2,
    Search
} from '../components/Icons';

import './Dashboard.css';

function Dashboard() {

    const navigate = useNavigate();

    const [incidents, setIncidents] = useState([]);
    const [stats, setStats] = useState(null);
    const [events, setEvents] = useState([]);
    const [loading, setLoading] = useState(true);
    const [simulating, setSimulating] = useState(false);
    const [autoPilot, setAutoPilot] = useState(false);
    const [governanceMode, setGovernanceMode] = useState('Protocol Alpha');

    const fetchData = useCallback(async () => {
        try {
            const [inc, st, gov, ev] = await Promise.all([
                getIncidents(),
                getStats(),
                getGovernanceStatus(),
                fetch('/api/events').then(res => res.json())
            ]);

            setIncidents(inc || []);
            setStats(st);
            setEvents((ev || []).slice(0, 15)); // Last 15 events

            if (gov) {
                setAutoPilot(gov.auto_pilot);
                setGovernanceMode(gov.mode);
            }

        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }

    }, []);

    useEffect(() => {
        fetchData();
    }, [fetchData]);

    const handleSimulate = async () => {
        setSimulating(true);
        await simulateScenario();
        await fetchData();
        setSimulating(false);
    };

    const handleToggleGovernance = async () => {
        const res = await toggleGovernanceMode();
        setAutoPilot(res.auto_pilot);
        setGovernanceMode(res.mode);
    };

    const handleReset = async () => {
        await resetSimulation();
        await fetchData();
    };

    const formatTime = (ts) => {
        if (!ts) return '';
        const d = new Date(ts);
        return d.toLocaleTimeString('en-US');
    };

    if (loading) {
        return (
            <div className="dashboard-loading">
                <div className="loader"></div>
                Loading AI Command Center...
            </div>
        );
    }

    const criticalCount = stats?.by_severity?.critical || 0;
    const pendingCount = stats?.by_status?.actions_pending || 0;
    const analyzedCount = stats?.by_status?.analyzed || 0;

    return (
        <div className="dashboard">
            <div className="noise-overlay" />

            {/* HEADER */}
            <div className="dashboard-top">

                <div className="title-block">
                    <h1>Command Center</h1>
                    <p>SYSTEM_GOVERNANCE_PROTOCOL_v5.0</p>
                </div>

                <div
                    className={`protocol-toggle ${autoPilot ? 'active' : ''}`}
                    onClick={handleToggleGovernance}
                >
                    {governanceMode}
                </div>
            </div>

            <TelemetryGrid />

            {/* STATS */}
            <div className="stats-grid">

                <div className="stat-card">
                    <span>TOTAL_INCIDENTS</span>
                    <h2>{stats?.total_incidents || 0}</h2>
                </div>

                <div className="stat-card critical">
                    <span>CRITICAL_THREATS</span>
                    <h2>{criticalCount}</h2>
                </div>

                <div className="stat-card warning">
                    <span>ACTIONS_PENDING</span>
                    <h2>{pendingCount}</h2>
                </div>

                <div className="stat-card success">
                    <span>THREATS_RESOLVED</span>
                    <h2>{analyzedCount}</h2>
                </div>

            </div>

            {/* ACTION BAR */}

            <div className="action-bar">

                <button className="btn-primary" onClick={handleSimulate}>
                    {simulating ? "RUNNING_PIPELINE..." : "SIMULATE_INCIDENTS"}
                </button>

                <button onClick={fetchData}>
                    <RefreshCw size={16} /> REFRESH_SYSTEM
                </button>

                {incidents.length > 0 &&
                    <button className="danger" onClick={handleReset}>
                        <Trash2 size={16} /> RESET_SIMULATION
                    </button>
                }

            </div>

            <div className="dashboard-main-grid">
                {/* INCIDENT TABLE */}
                <div className="table-card incident-column">
                    <div className="table-head">
                        <h3>INCIDENT_LOGS</h3>
                        <span>{incidents.length}</span>
                    </div>

                    {incidents.length === 0 ? (
                        <div className="empty">
                            <Search size={48} />
                            <h4>NO_INCIDENTS_DETECTED</h4>
                        </div>
                    ) : (
                        <table>
                            <thead>
                                <tr>
                                    <th>SEVERITY</th>
                                    <th>IDENTIFIER</th>
                                    <th>STATUS</th>
                                    <th>AFFECTED</th>
                                    <th>TIME</th>
                                </tr>
                            </thead>
                            <tbody>
                                {incidents.map((inc) => (
                                    <tr key={inc.id} onClick={() => navigate(`/incidents/${inc.id}`)}>
                                        <td><StatusBadge type="severity" value={inc.severity} /></td>
                                        <td className="incident-title">{inc.title}</td>
                                        <td><StatusBadge type="status" value={inc.status} /></td>
                                        <td>
                                            {inc.affected_services?.slice(0, 2).map(s =>
                                                <span key={s} className="tag">{s}</span>
                                            )}
                                        </td>
                                        <td className="time">{formatTime(inc.created_at)}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    )}
                </div>

                {/* LIVE EVENT FEED */}
                <div className="table-card feed-column">
                    <div className="table-head">
                        <h3>LIVE_SENTINEL_FEED</h3>
                        <div className="pulse-icon" />
                    </div>
                    <div className="event-stream">
                        {events.length === 0 ? (
                            <div className="empty-small">NO_LIVE_TRAFFIC</div>
                        ) : (
                            events.map((ev, idx) => (
                                <div key={ev.id || idx} className={`event-row ${ev.severity?.toLowerCase()}`}>
                                    <span className="ev-time">{formatTime(ev.timestamp)}</span>
                                    <span className="ev-service">[{ev.source_service.toUpperCase()}]</span>
                                    <span className="ev-msg">{ev.message}</span>
                                </div>
                            ))
                        )}
                    </div>
                </div>
            </div>

        </div>
    );
}

export default Dashboard;