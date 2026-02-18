import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Rocket, ShieldCheck, Cpu, Terminal } from '../components/Icons';
import './LandingPage.css';

function LandingPage() {
    const navigate = useNavigate();
    const [text, setText] = useState('');
    const [isComplete, setIsComplete] = useState(false);
    const fullText = "SYSTEM.INIT: DEVSICK_CORE_V1.0 ... CONNECTION_ESTABLISHED ... AI_REASONING_SYNCED ... READY_FOR_DEPLOYMENT.";

    useEffect(() => {
        let index = 0;
        const timer = setInterval(() => {
            setText(fullText.slice(0, index));
            index++;
            if (index > fullText.length) {
                clearInterval(timer);
                setIsComplete(true);
            }
        }, 30);
        return () => clearInterval(timer);
    }, []);

    return (
        <div className="landing-page">
            <div className="glitch-overlay" />

            <div className="landing-content">
                <div className="landing-logo-box">
                    <img src="/logo.png" alt="Devsick" className="landing-logo-big" />
                    <div className="logo-glow" />
                </div>

                <div className="mission-briefing">
                    <div className="terminal-header">
                        <Terminal size={14} />
                        <span>MISSION_BRIEFING_X01</span>
                    </div>
                    <div className="terminal-body">
                        <p className="typing-text">{text}<span className="cursor">_</span></p>
                    </div>
                </div>

                <div className={`landing-actions ${isComplete ? 'visible' : ''}`}>
                    <div className="feature-badges">
                        <div className="feat-badge">
                            <ShieldCheck size={14} />
                            <span>PROTOCOL ALPHA</span>
                        </div>
                        <div className="feat-badge">
                            <Cpu size={14} />
                            <span>LLAMA_3.1 ENGINE</span>
                        </div>
                    </div>

                    <button
                        className="btn-boot"
                        onClick={() => navigate('/dashboard')}
                    >
                        <Rocket size={18} />
                        INITIALIZE COMMAND CENTER
                    </button>

                    <p className="landing-footer">OPERATIONAL STATUS: NOMINAL // AUTH: SRE_MASTER</p>
                </div>
            </div>

            <div className="ambient-background">
                <div className="grid-layer" />
                <div className="spotlight" />
            </div>
        </div>
    );
}

export default LandingPage;
