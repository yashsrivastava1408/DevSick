import React, { useState, useEffect, useCallback } from 'react';
import { useParams, Link } from 'react-router-dom';
import StatusBadge from '../components/StatusBadge';
import {
    getIncident,
    getIncidentActions,
    approveAction,
    rejectAction,
} from '../api/client';
import {
    Key,
    Database,
    Network,
    ShieldCheck,
    ShieldAlert,
    Zap,
    Server,
    AlertTriangle,
    CheckCircle,
    Activity
} from '../components/Icons';
import './IncidentPage.css';

const getServiceIcon = (serviceName) => {
    switch (serviceName) {
        case 'vault': return <Key size={16} />;
        case 'eso': return <Key size={16} />;
        case 'database': return <Database size={16} />;
        case 'api_gateway': return <Network size={16} />;
        case 'auth_service': return <ShieldCheck size={16} />;
        case 'user_service': return <ShieldAlert size={16} />;
        case 'cert_manager': return <ShieldCheck size={16} />;
        default: return <Server size={16} />;
    }
};

function IncidentPage() {
    const { id } = useParams();
    const [incident, setIncident] = useState(null);
    const [actions, setActions] = useState([]);
    const [loading, setLoading] = useState(true);

    const fetchData = useCallback(async () => {
        try {
            const [inc, acts] = await Promise.all([
                getIncident(id),
                getIncidentActions(id),
            ]);
            setIncident(inc);
            setActions(acts);
        } catch (err) {
            console.error('Failed to fetch incident:', err);
        } finally {
            setLoading(false);
        }
    }, [id]);

    useEffect(() => {
        fetchData();
    }, [fetchData]);

    const handleApprove = async (actionId) => {
        try {
            await approveAction(actionId);
            await fetchData();
        } catch (err) {
            console.error('Approval failed:', err);
        }
    };

    const handleReject = async (actionId) => {
        try {
            await rejectAction(actionId);
            await fetchData();
        } catch (err) {
            console.error('Rejection failed:', err);
        }
    };

    const formatTime = (ts) => {
        const d = new Date(ts);
        return d.toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
        });
    };

    if (loading) {
        return (
            <div className="incident-page">
                <div className="loading-container">
                    <div className="spinner"></div>
                    <span>Loading incident details...</span>
                </div>
            </div>
        );
    }

    if (!incident) {
        return (
            <div className="incident-page">
                <Link to="/" className="back-link">← Back to Dashboard</Link>
                <div className="empty-state">
                    <div className="empty-icon"><AlertTriangle size={48} strokeWidth={1} /></div>
                    <h3>Incident not found</h3>
                </div>
            </div>
        );
    }

    const rca = incident.root_cause_analysis;
    const confidenceColor = rca?.confidence_score >= 0.8
        ? '#10b981'
        : rca?.confidence_score >= 0.5
            ? '#f59e0b'
            : '#ef4444';

    return (
        <div className="incident-page fade-in">
            <Link to="/" className="back-link">← Back to Dashboard</Link>

            {/* Header */}
            <div className="incident-header">
                <div className="incident-header-top">
                    <h1>{incident.title}</h1>
                </div>
                <div className="incident-meta">
                    <StatusBadge type="severity" value={incident.severity} />
                    <StatusBadge type="status" value={incident.status} />
                    <span className="meta-item">ID: {incident.id.slice(0, 8)}</span>
                    <span className="meta-item">{formatTime(incident.created_at)}</span>
                </div>
            </div>

            {/* Root Cause Analysis */}
            {rca && (
                <div className="section">
                    <div className="section-header">
                        <h2><Zap size={18} /> AI Root Cause Analysis</h2>
                        <StatusBadge type="status" value="analyzed" />
                    </div>
                    <div className="section-content">
                        {/* Root Cause */}
                        <div className="rca-root-cause">
                            <div className="rca-root-cause-label">Root Cause Identified</div>
                            <div className="rca-root-cause-text">{rca.root_cause}</div>
                        </div>

                        {/* Summary */}
                        <div className="rca-summary">{rca.summary}</div>

                        {/* Reasoning Chain */}
                        <div className="reasoning-chain">
                            <h3 style={{ fontSize: 13, fontWeight: 600, marginBottom: 12, color: 'var(--text-muted)' }}>
                                Reasoning Chain
                            </h3>
                            {rca.reasoning_chain?.map((step, i) => (
                                <div key={i} className="reasoning-step">{step}</div>
                            ))}
                        </div>

                        {/* Confidence */}
                        <div className="confidence-bar">
                            <span className="confidence-label">Confidence</span>
                            <div className="confidence-track">
                                <div
                                    className="confidence-fill"
                                    style={{
                                        width: `${(rca.confidence_score || 0) * 100}%`,
                                        background: confidenceColor,
                                    }}
                                />
                            </div>
                            <span className="confidence-value" style={{ color: confidenceColor }}>
                                {((rca.confidence_score || 0) * 100).toFixed(0)}%
                            </span>
                        </div>

                        {/* Impact */}
                        {rca.impact_description && (
                            <div className="impact-text">
                                <strong>Impact: </strong>{rca.impact_description}
                            </div>
                        )}
                    </div>
                </div>
            )}

            {/* Event Timeline */}
            <div className="section">
                <div className="section-header">
                    <h2><Activity size={18} /> Event Timeline</h2>
                    <span className="table-count">{incident.timeline?.length || 0} events</span>
                </div>
                <div className="section-content">
                    <div className="timeline">
                        {incident.timeline?.map((entry, i) => (
                            <div key={i} className="timeline-entry">
                                <div className={`timeline-dot ${entry.severity}`}></div>
                                <div className="timeline-time">{formatTime(entry.timestamp)}</div>
                                <div className="timeline-service">{entry.source_service}</div>
                                <div className="timeline-message">{entry.event}</div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            {/* Remediation Actions */}
            {actions.length > 0 && (
                <div className="section">
                    <div className="section-header">
                        <h2><CheckCircle size={18} /> Recommended Actions</h2>
                        <span className="table-count">
                            {actions.filter(a => a.approval_status === 'pending').length} pending
                        </span>
                    </div>
                    <div className="section-content">
                        {actions.map((action) => (
                            <div key={action.id} className="action-card">
                                <div className="action-card-header">
                                    <div className="action-card-title">
                                        {action.title}
                                        <span className={`risk-tag ${action.risk_level}`}>
                                            {action.risk_level} risk
                                        </span>
                                    </div>
                                    <StatusBadge type="approval" value={action.approval_status} />
                                </div>
                                <div className="action-card-body">
                                    <div className="action-description">{action.description}</div>
                                    {action.command_hint && (
                                        <div className="action-command">{action.command_hint}</div>
                                    )}
                                    {action.rollback_description && (
                                        <div className="action-rollback">
                                            Rollback: {action.rollback_description}
                                        </div>
                                    )}
                                    {action.approval_status === 'pending' && (
                                        <div className="action-buttons">
                                            <button
                                                className="btn btn-sm btn-approve"
                                                onClick={() => handleApprove(action.id)}
                                            >
                                                Approve
                                            </button>
                                            <button
                                                className="btn btn-sm btn-reject"
                                                onClick={() => handleReject(action.id)}
                                            >
                                                Reject
                                            </button>
                                        </div>
                                    )}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Affected Services */}
            <div className="section">
                <div className="section-header">
                    <h2><Network size={18} /> Affected Services</h2>
                </div>
                <div className="section-content">
                    <div className="services-grid">
                        {incident.affected_services?.map((svc) => (
                            <div key={svc} className="service-chip">
                                <span className="service-chip-icon">
                                    {getServiceIcon(svc)}
                                </span>
                                {svc}
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
}

export default IncidentPage;
