import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import IncidentPage from './pages/IncidentPage';
import LandingPage from './pages/LandingPage';
import './App.css';

function AppContent() {
    const location = useLocation();
    const isLanding = location.pathname === '/landing';

    // Default to /landing if we hit the root
    React.useEffect(() => {
        if (location.pathname === '/') {
            // We can either redirect or just show landing at /
        }
    }, [location.pathname]);

    return (
        <div className="app-container">
            <div className="scanlines" />
            {!isLanding && <Sidebar />}
            <main className={isLanding ? 'landing-main' : 'main-content'}>
                <Routes>
                    <Route path="/" element={<LandingPage />} />
                    <Route path="/landing" element={<LandingPage />} />
                    <Route path="/dashboard" element={<Dashboard />} />
                    <Route path="/incidents/:id" element={<IncidentPage />} />
                </Routes>
            </main>
        </div>
    );
}

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
            <AppContent />
        </Router>
    );
}

export default App;
