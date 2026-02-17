<p align="center">
  <h1 align="center">Devsick</h1>
  <p align="center">
    <strong>AI-Driven Application Support & Operations Platform</strong>
  </p>
  <p align="center">
    An enterprise-grade AI incident reasoning engine that correlates operational signals,<br/>
    identifies root causes, and recommends remediation — with human-in-the-loop governance.
  </p>
  <p align="center">
    <img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
    <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI" />
    <img src="https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react&logoColor=black" alt="React" />
    <img src="https://img.shields.io/badge/Groq_AI-Llama_3.1-FF6B35?style=for-the-badge&logo=meta&logoColor=white" alt="Groq" />
    <img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker" />
  </p>
  <p align="center">
    <img src="https://img.shields.io/badge/Status-Prototype_MVP-blueviolet?style=for-the-badge" alt="Status" />
    <img src="https://img.shields.io/badge/Maintenance-Active_Development-yellow?style=for-the-badge" alt="Maintenance" />
  </p>
</p>

---

> **Note: This is NOT a chatbot.** Devsick is a structured incident reasoning pipeline — it ingests logs, correlates events, maps service dependencies, and uses AI to generate root cause analysis with actionable remediation playbooks.

---

## Architecture

```mermaid
graph TD
    subgraph Observability [Observability Layer]
        Logs[Logs / Events]
        Metrics[Metrics]
        Alerts[Alerts]
    end

    subgraph Ingestion [Ingestion Layer]
        API[Log & Event Ingestion API]
    end

    subgraph Intelligence [Intelligence Layer]
        Correlation[Event Correlation Engine]
        Graph[Service Knowledge Graph]
        AI[AI Incident Reasoning<br/>Groq + Llama 3.1]
    end

    subgraph Action [Action Layer]
        RCA[Root Cause Analysis]
        Recs[Recommendation Engine]
    end

    subgraph Governance [Governance Layer]
        Human[Human-in-the-Loop<br/>Governance]
    end

    subgraph UI [Presentation Layer]
        Dash[React Dashboard]
    end

    Logs --> API
    Metrics --> API
    Alerts --> API
    
    API --> Correlation
    Correlation <--> Graph
    Correlation --> AI
    Graph --> AI
    
    AI --> RCA
    AI --> Recs
    
    RCA --> Human
    Recs --> Human
    
    Human --> Dash
    
    classDef layer fill:#0f172a,stroke:#334155,color:#fff,stroke-width:2px;
    classDef component fill:#1e293b,stroke:#475569,color:#e2e8f0;
    class Observability,Ingestion,Intelligence,Action,Governance,UI layer;
    class Logs,Metrics,Alerts,API,Correlation,Graph,AI,RCA,Recs,Human,Dash component;
```

---

## Key Features

| Feature | Description |
|---------|-------------|
| **Event Correlation** | Groups related errors across services using time windows and dependency mapping |
| **AI Root Cause Analysis** | Llama 3.1 via Groq API generates structured RCA with reasoning chains |
| **Confidence Scoring** | Each analysis includes a confidence score (0–100%) |
| **Remediation Playbooks** | Pre-built action plans with `kubectl` commands and rollback procedures |
| **Human Governance** | Approve/reject workflow — AI never auto-executes on production |
| **Dependency Mapping** | Knowledge graph tracks service relationships and cascade paths |
| **Graceful Degradation** | Falls back to mock RCA when Groq API is unavailable |

---

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker (optional)
- Groq API key ([free at console.groq.com](https://console.groq.com))

### Option 1: Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/yashsrivastava1408/DevSick.git
cd DevSick

# Add your Groq API key
echo "GROQ_API_KEY=your_key_here" > .env

# Run
docker compose up --build
```

### Option 2: Manual Setup

```bash
# Backend
cd backend
pip install -r requirements.txt
export GROQ_API_KEY=your_key_here
uvicorn app.main:app --reload --port 8000

# Frontend (separate terminal)
cd frontend
npm install
npm start
```

### Access

| Service | URL |
|---------|-----|
| Dashboard | http://localhost:3000 |
| API Docs (Swagger) | http://localhost:8000/docs |
| Health Check | http://localhost:8000/api/health |

---

## Demo Walkthrough

1. Open `http://localhost:3000`
2. Click **Simulate Incidents** — runs 3 enterprise scenarios
3. Click any incident to see AI reasoning, timeline, and recommendations
4. Use **Approve / Reject** to exercise the governance workflow

### Simulated Scenarios

| Scenario | Root Cause | Cascade Path |
|----------|-----------|--------------|
| **Vault Auth Failure** | Vault sealed/unreachable | Vault → ESO → Database → Auth → API |
| **JWT Key Missing** | JWT signing key lease expired | Vault → Auth → User Service → API |
| **API Auth Cascade** | TLS certificate expired | Cert Manager → API Gateway → Auth → Users |

---

## API Reference

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/health` | Health check + AI status |
| `POST` | `/api/simulate` | Run all demo scenarios |
| `POST` | `/api/reset` | Clear all data |
| `GET` | `/api/stats` | Dashboard statistics |

### Incident Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/incidents` | List all incidents |
| `GET` | `/api/incidents/{id}` | Get incident details + RCA |
| `POST` | `/api/incidents/{id}/analyze` | Trigger AI analysis |

### Governance

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/incidents/{id}/actions` | Get remediation actions |
| `GET` | `/api/actions/pending` | List pending approvals |
| `POST` | `/api/actions/{id}/approve` | Approve an action |
| `POST` | `/api/actions/{id}/reject` | Reject an action |

### Infrastructure

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/ingest` | Ingest a log event |
| `POST` | `/api/ingest/batch` | Batch ingest events |
| `GET` | `/api/graph` | Service dependency graph |
| `GET` | `/api/graph/impact/{id}` | Impact analysis for a service |

---

## Project Structure

```
Devsick/
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI application entry point
│   │   ├── config.py               # Environment & model configuration
│   │   ├── models/                 # Pydantic schemas
│   │   │   ├── events.py           #   Log events, alerts
│   │   │   ├── incidents.py        #   Incidents, RCA, timeline
│   │   │   └── actions.py          #   Remediation actions, approvals
│   │   ├── ingestion/              # Layer 1: Log ingestion
│   │   │   └── log_ingestor.py     #   In-memory event store
│   │   ├── correlation/            # Layer 2: Event correlation
│   │   │   └── engine.py           #   Pattern matching + grouping
│   │   ├── knowledge/              # Layer 3: Service graph
│   │   │   └── dependency_graph.py #   Directed dependency graph
│   │   ├── reasoning/              # Layer 4: AI analysis
│   │   │   ├── ai_engine.py        #   Groq API integration
│   │   │   └── prompts.py          #   Structured SRE prompts
│   │   ├── recommendations/        # Layer 5: Action engine
│   │   │   └── engine.py           #   Remediation playbooks
│   │   ├── governance/             # Layer 6: Human-in-the-loop
│   │   │   └── approval.py         #   Approve/reject state machine
│   │   ├── routes/                 # API endpoints
│   │   └── data/                   # Sample data + service graph
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── api/client.js           # Backend API client
│   │   ├── components/             # Sidebar, StatusBadge
│   │   └── pages/                  # Dashboard, IncidentPage
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
├── .env                            # API keys (gitignored)
└── README.md
```

---

## Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GROQ_API_KEY` | No | — | Groq API key for live AI. Falls back to mock if missing. |
| `REACT_APP_API_URL` | No | `http://localhost:8000` | Backend URL for frontend |

---

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **API** | Python FastAPI | High-performance async API framework |
| **AI** | Groq + Llama 3.1 8B | Sub-second inference for incident reasoning |
| **Frontend** | React 18 | Enterprise dashboard with dark theme |
| **Validation** | Pydantic v2 | Data models and schema validation |
| **Deployment** | Docker Compose | Multi-container orchestration |
| **Data** | In-memory + JSON | Zero-dependency data layer |

---

## How the AI Works

Devsick uses **structured prompting** — not chat. The AI receives:

1. **System prompt**: SRE persona with specific output schema
2. **Incident context**: Correlated events, service graph, timeline
3. **Output format**: Strict JSON with `root_cause`, `reasoning_chain`, `confidence_score`, `impact_description`

The prompt engineering ensures consistent, auditable RCA output rather than free-form text.

---

## License

This project is built as an enterprise prototype for demonstration purposes.

---

<p align="center">
  <strong>Built by Yash Srivastava</strong>
</p>
