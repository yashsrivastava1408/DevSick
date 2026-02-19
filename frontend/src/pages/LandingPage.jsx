import React, { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import "./LandingPage.css";

export default function LandingPage() {
    const navigate = useNavigate();
    const [isTransitioning, setIsTransitioning] = useState(false);
    const [mousePos, setMousePos] = useState({ x: 0.5, y: 0.5 });
    const sectionRef = useRef(null);

    useEffect(() => {
        const handleMouseMove = (e) => {
            if (!sectionRef.current) return;
            const { innerWidth, innerHeight } = window;
            setMousePos({
                x: e.clientX / innerWidth,
                y: e.clientY / innerHeight
            });
        };
        window.addEventListener("mousemove", handleMouseMove);
        return () => window.removeEventListener("mousemove", handleMouseMove);
    }, []);

    const handleInitialize = () => {
        setIsTransitioning(true);
        setTimeout(() => {
            navigate("/dashboard");
        }, 1200);
    };

    // Number of pillars
    const pillars = Array.from({ length: 12 });

    return (
        <div
            className={`landing-cobalt ${isTransitioning ? "system-warping" : ""}`}
            ref={sectionRef}
            style={{
                "--m-x": mousePos.x,
                "--m-y": mousePos.y,
                "--tilt-x": (mousePos.y - 0.5) * 8 + "deg",
                "--tilt-y": (mousePos.x - 0.5) * -8 + "deg"
            }}
        >
            {/* 🎬 CINEMATIC VIDEO BACKGROUND */}
            <div className="video-background-container">
                <video
                    className="bg-video"
                    autoPlay
                    loop
                    muted
                    playsInline
                    preload="auto"
                >
                    <source
                        src="/background-loop.mp4"
                        type="video/mp4"
                    />
                </video>
                <div className="video-overlay" />
            </div>

            {/* 🌌 COBALT FLARE GRID */}
            <div className="flare-grid">
                {Array.from({ length: 20 }).map((_, i) => (
                    <div key={i} className="grid-node" style={{ "--i": i }}>
                        <div className="node-pulse" />
                    </div>
                ))}
            </div>

            {/* 💎 LUXE CENTERED CONTENT */}
            <div className="landing-content-centered">

                <div className="hero-center">
                    <div className="protocol-badge">AI COMMAND CENTER_v5.0</div>

                    <div className="brand-layer">
                        <div className="brand-3d-container">
                            <h1 className="brutal-headline">DEVSICK</h1>
                        </div>
                    </div>

                    <div className="tagline-stack">
                        <p className="primary-tagline">
                            <span className="accent-flare">INTELLIGENCE</span> AI
                        </p>
                        <p className="secondary-tagline">
                            Devsick automatically discovers, correlates, and resolves
                            system failures before they impact your users.
                        </p>
                    </div>

                    <div className="action-hub">
                        <button className="btn-flare-primary" onClick={handleInitialize}>
                            <span className="btn-label">LAUNCH COMMAND CENTER</span>
                            <div className="flare-sweep" />
                        </button>
                    </div>

                    <div className="system-ready-indicator">
                        <div className="dot" /> SYSTEM_ACTIVE_STABLE
                    </div>
                </div>

            </div>

            {/* 📡 HUD TELEMETRY */}
            <div className="hud-corner top-right">
                <div className="data-shroud">
                    <div className="shroud-line">MONITORING_SERVICES... [STABLE]</div>
                    <div className="shroud-line">ANALYZING_PATTERNS... [DONE]</div>
                    <div className="shroud-line">AI_ENGINE_STATE... [READY]</div>
                </div>
            </div>

            <div className="hud-corner bottom-left">
                <div className="data-shroud">
                    <div className="shroud-line">SENTINEL_STREAM... [CONNECTED]</div>
                    <div className="shroud-line">LATENCY_CORE... [0.42ms]</div>
                    <div className="shroud-line">UPTIME_NODE... [99.99%]</div>
                </div>
            </div>

            <div className="hud-corner top-left">
                <div className="hud-label">S_LATENCY</div>
                <div className="hud-value">0.42ms</div>
            </div>

            <div className="hud-corner bottom-right">
                <div className="hud-label">ACTIVE_NODES</div>
                <div className="hud-value">12,842</div>
            </div>

            <div className="brutal-scanline" />
            <div className="noise-overlay" />
            <div className="premium-spotlight" />
        </div>
    );
}