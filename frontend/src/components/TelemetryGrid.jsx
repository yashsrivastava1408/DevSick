import React, { useState, useEffect } from 'react';
import { Activity, Zap, ShieldAlert, Cpu } from './Icons';
import './TelemetryGrid.css';

const TelemetryGrid = () => {
    const [metrics, setMetrics] = useState({
        backend_up: 0,
        requests_per_second: 0,
        error_rate_per_second: 0,
        p95_latency_seconds: 0,
        healthy: false
    });
    const [loading, setLoading] = useState(true);

    const fetchMetrics = async () => {
        try {
            const response = await fetch('/api/observability/summary');
            const data = await response.json();
            setMetrics(data);
            setLoading(false);
        } catch (error) {
            console.error('Error fetching telemetry:', error);
        }
    };

    useEffect(() => {
        fetchMetrics();
        const interval = setInterval(fetchMetrics, 2000); // 2s refresh
        return () => clearInterval(interval);
    }, []);

    const formatLatency = (l) => {
        if (l === null) return '0ms';
        return (l * 1000).toFixed(2) + 'ms';
    };

    const isCritical = (key, val) => {
        if (key === 'error_rate' && val > 0.05) return true;
        if (key === 'latency' && val > 0.5) return true;
        return false;
    };

    return (
        <div className="telemetry-grid">
            <div className={`telemetry-card ${metrics.healthy ? 'status-ok' : 'status-fail'}`}>
                <div className="card-header">
                    <Activity size={14} />
                    <span>SYSTEM_AVAILABILITY</span>
                </div>
                <div className="card-value">
                    {metrics.backend_up ? 'ACTIVE' : 'DEGRADED'}
                </div>
                <div className="card-subtext">CORE_ENGINE_v5.0</div>
            </div>

            <div className="telemetry-card">
                <div className="card-header">
                    <Zap size={14} />
                    <span>THROUGHPUT</span>
                </div>
                <div className="card-value">
                    {metrics.requests_per_second?.toFixed(2) || '0.00'}<span className="unit">rps</span>
                </div>
                <div className="card-subtext">5M_WINDOW_AVG</div>
            </div>

            <div className={`telemetry-card ${metrics.error_rate_per_second > 0 ? 'critical' : ''}`}>
                <div className="card-header">
                    <ShieldAlert size={14} />
                    <span>ERROR_RATE</span>
                </div>
                <div className="card-value">
                    {((metrics.error_rate_per_second || 0) * 100).toFixed(2)}<span className="unit">%</span>
                </div>
                <div className="card-subtext">P0_SLA_THRESHOLD</div>
                {metrics.error_rate_per_second > 0 && <div className="glitch-line" />}
            </div>

            <div className="telemetry-card">
                <div className="card-header">
                    <Cpu size={14} />
                    <span>P95_LATENCY</span>
                </div>
                <div className="card-value">
                    {formatLatency(metrics.p95_latency_seconds)}
                </div>
                <div className="card-subtext">0.42MS_TARGET</div>
            </div>
        </div>
    );
};

export default TelemetryGrid;
