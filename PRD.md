# Phase 2: Deep Observability & Real-Time Intelligence
## Implementation Task File

This document outlines the specific code and infrastructure changes required to transition Devsick from a static prototype to a real-time autonomous SRE engine.

### 1. Infrastructure Layer: Log Aggregation (Loki)
- [x] **Docker Upgrade**: Add `loki` and `promtail` services to `docker-compose.yml`.
- [x] **Log Routing**: Configure Promtail to scrape logs from the backend and frontend containers.
- [x] **Loki DataSource**: Add Loki as a provisioned datasource in `infrastructure/grafana/provisioning/datasources/datasource.yml`.

### 2. Backend Layer: Real-Time Event Triggering
- [x] **Alertmanager Integration**: Deploy Alertmanager and configure it to send webhooks to a new backend endpoint `/api/alerts/webhook`.
- [x] **Live Ingestor**: Update `backend/app/ingestion/log_ingestor.py` to handle high-velocity log streams from Loki.
- [x] **Async Reasoning Trigger**: Modify the alert webhook to automatically trigger `analyze_incident()` whenever a "Critical" alert is received, removing the need for manual simulation.

### 3. Intelligence Layer: Advanced Reasoning
- [x] **Metric-Log Correlation**: Update the AI prompt to accept both log lines and metric thresholds (e.g., "CPU > 90%").
- [x] **Dynamic Dependency Mapping**: Update `backend/app/knowledge/dependency_graph.py` to populate service relationships from live OpenTelemetry data.

### 4. Frontend Layer: Cinematic Telemetry HUD
- [x] **Live Metrics Widget**: Create a `TelemetryGrid.jsx` component that polls Prometheus every 2 seconds for core system metrics.
- [x] **Real-Time Feed**: Replace the static incident list with a "Live Sentinel Feed" that scrolls new events as they are ingested.
- [x] **HUD Aesthetic**: Implement "Neural Phosphor" glows on metric values that exceed critical thresholds.

### 5. Persistence Layer: Enterprise DB
- [x] **PostgreSQL Migration**: Replace SQLite with PostgreSQL in `backend/app/database.py`.
- [x] **Migration Scripts**: Create Alembic migrations to preserve incident history.

---
**Status**: Initializing Execution...
**Engine**: Llama 3.3 70B
**Protocol**: Alpha -> Omega (Transitioning)
