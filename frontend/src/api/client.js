/**
 * Devsick API Client
 * Handles all communication with the FastAPI backend.
 */

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000';

async function request(endpoint, options = {}) {
    const url = `${API_BASE}${endpoint}`;
    const config = {
        headers: { 'Content-Type': 'application/json' },
        ...options,
    };

    const response = await fetch(url, config);
    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Request failed' }));
        throw new Error(error.detail || `HTTP ${response.status}`);
    }
    return response.json();
}

// Health
export const getHealth = () => request('/api/health');

// Incidents
export const getIncidents = () => request('/api/incidents');
export const getIncident = (id) => request(`/api/incidents/${id}`);
export const analyzeIncident = (id) => request(`/api/incidents/${id}/analyze`, { method: 'POST' });
export const getStats = () => request('/api/stats');

// Actions
export const getIncidentActions = (incidentId) => request(`/api/incidents/${incidentId}/actions`);
export const getPendingActions = () => request('/api/actions/pending');
export const approveAction = (id) => request(`/api/actions/${id}/approve`, { method: 'POST' });
export const rejectAction = (id) => request(`/api/actions/${id}/reject`, { method: 'POST' });
export const rollbackAction = (id) => request(`/api/actions/${id}/rollback`, { method: 'POST' });
export const getGovernanceStatus = () => request('/api/governance/status');
export const toggleGovernanceMode = () => request('/api/governance/toggle', { method: 'POST' });

// Graph
export const getGraph = () => request('/api/graph');
export const getImpact = (serviceId) => request(`/api/graph/impact/${serviceId}`);

// Simulation
export const simulateScenario = (scenario) => {
    const query = scenario ? `?scenario=${scenario}` : '';
    return request(`/api/simulate${query}`, { method: 'POST' });
};
export const resetSimulation = () => request('/api/reset', { method: 'POST' });

// Events
export const getEvents = () => request('/api/events');
