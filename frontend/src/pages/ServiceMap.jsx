import React, { useState, useEffect } from 'react';
import { getGraph, getImpact } from '../api/client';
import './ServiceMap.css';

const ServiceMap = () => {

    const [graph, setGraph] = useState({ services: [], dependencies: [] });
    const [loading, setLoading] = useState(true);
    const [selectedService, setSelectedService] = useState(null);
    const [impactPath, setImpactPath] = useState([]);

    useEffect(() => {
        loadGraph();
    }, []);

    const loadGraph = async () => {
        setLoading(true);
        const data = await getGraph();
        setGraph(data);
        setLoading(false);
    };

    const handleServiceClick = async (serviceId) => {

        if (selectedService === serviceId) {
            setSelectedService(null);
            setImpactPath([]);
            return;
        }

        setSelectedService(serviceId);

        const impactData = await getImpact(serviceId);
        setImpactPath(impactData.impact_path);
    };

    /* ===== POSITION LOGIC (unchanged) ===== */

    const tierOrder = { infrastructure: 0, data: 1, application: 2 };
    const tierNodes = {};

    graph.services.forEach(s => {
        const tier = s.tier.toLowerCase();
        if (!tierNodes[tier]) tierNodes[tier] = [];
        tierNodes[tier].push(s);
    });

    const nodePositions = {};
    const width = 1200;
    const height = 700;
    const paddingX = 200;
    const paddingY = 120;

    const tiers = Object.keys(tierNodes).sort((a, b) =>
        (tierOrder[a] ?? 99) - (tierOrder[b] ?? 99)
    );

    const tierSpacing = tiers.length > 1
        ? (width - 2 * paddingX) / (tiers.length - 1)
        : 0;

    tiers.forEach((tier, tierIdx) => {
        const nodes = tierNodes[tier];
        const nodeSpacing = (height - 2 * paddingY) / (nodes.length || 1);
        const x = paddingX + tierIdx * tierSpacing;

        nodes.forEach((node, nodeIdx) => {
            const y = paddingY + (nodeIdx + .5) * nodeSpacing;
            nodePositions[node.id] = { x, y };
        });
    });

    return (
        <div className="clean-map">

            <div className="clean-map-header">
                <h1>Infrastructure Map</h1>
                <p>Service dependency visualization</p>
            </div>

            <div className="clean-map-container">

                {loading ? (
                    <div className="loading">Loading graph…</div>
                ) : (

                    <svg viewBox={`0 0 ${width} ${height}`}>

                        {/* EDGES */}

                        {graph.dependencies.map((dep, i) => {

                            const start = nodePositions[dep.from];
                            const end = nodePositions[dep.to];
                            if (!start || !end) return null;

                            const isActive =
                                selectedService === dep.from &&
                                impactPath.includes(dep.to);

                            return (
                                <path
                                    key={i}
                                    d={`M ${start.x} ${start.y} L ${end.x} ${end.y}`}
                                    className={`edge ${isActive ? 'active' : ''}`}
                                />
                            );

                        })}

                        {/* NODES */}

                        {graph.services.map(service => {

                            const pos = nodePositions[service.id];
                            if (!pos) return null;

                            const isRoot = selectedService === service.id;
                            const isAffected = impactPath.includes(service.id);

                            return (
                                <g
                                    key={service.id}
                                    className={`node ${isRoot ? 'root' : ''} ${isAffected && !isRoot ? 'affected' : ''}`}
                                    transform={`translate(${pos.x},${pos.y})`}
                                    onClick={() => handleServiceClick(service.id)}
                                >
                                    <rect
                                        x="-70"
                                        y="-25"
                                        width="140"
                                        height="50"
                                        rx="14"
                                        className="node-card"
                                    />

                                    <text textAnchor="middle" y="5">
                                        {service.name}
                                    </text>

                                </g>
                            );

                        })}

                    </svg>

                )}

            </div>
        </div>
    );
};

export default ServiceMap;