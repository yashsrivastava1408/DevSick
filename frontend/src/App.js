import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import IncidentPage from './pages/IncidentPage';
import './App.css';

function App() {
    React.useEffect(() => {
        const handleMouseMove = (e) => {
            document.body.style.setProperty('--mouse-x', `${e.clientX}px`);
            document.body.style.setProperty('--mouse-y', `${e.clientY}px`);
        };

        window.addEventListener('mousemove', handleMouseMove);
        return () => window.removeEventListener('mousemove', handleMouseMove);
    }, []);

    return (
        <Router>
            <div className="app-container">
                <div className="scanlines" />
                <Sidebar />
                <main className="main-content">
                    <Routes>
                        <Route path="/" element={<Dashboard />} />
                        <Route path="/incidents/:id" element={<IncidentPage />} />
                    </Routes>
                </main>
            </div>
        </Router>
    );
}

export default App;
