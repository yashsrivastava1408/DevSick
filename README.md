# Devsick — AI-Driven Application Support & Operations Platform

An enterprise-grade **AI incident reasoning platform** that sits on top of monitoring tools, ingests operational signals, correlates related events, and uses AI to identify root causes and recommend remediation actions — all with human-in-the-loop governance.

> **This is NOT a chatbot.** Devsick is a structured incident reasoning pipeline.

---

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    Observability Sources                      │
│         (Simulated logs, alerts, operational signals)         │
└──────────────────┬───────────────────────────────────────────┘
                   ▼
┌──────────────────────────────┐
│   Log & Event Ingestion API  │  POST /api/ingest
└──────────────────┬───────────┘
                   ▼
┌──────────────────────────────┐
│  Event Correlation Engine    │  Rule-based grouping
│  + Service Dependency Graph  │  Cascading failure detection
└──────────────────┬───────────┘
                   ▼
┌──────────────────────────────┐
│   AI Incident Reasoning      │  Groq API + Llama3-8B
│   (Structured RCA prompts)   │  JSON output schema
└──────────────────┬───────────┘
                   ▼
┌──────────────────────────────┐
│  Root Cause Analysis Output  │  Summary, timeline, reasoning
│  + Recommendation Engine     │  Remediation playbooks
└──────────────────┬───────────┘
                   ▼
┌──────────────────────────────┐
│  Human-in-the-Loop Governance│  Approve / Reject / Rollback
└──────────────────┬───────────┘
                   ▼
┌──────────────────────────────┐
│      Dashboard Interface     │  React dark-themed UI
└──────────────────────────────┘
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python FastAPI |
| Frontend | React 18 |
| AI Model | Llama3-8B via Groq API |
| Deployment | Docker + docker-compose |
| Data | In-memory (JSON sample data) |

---

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- (Optional) Groq API key for live AI reasoning

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

API docs: http://localhost:8000/docs

### Frontend

```bash
cd frontend
npm install
npm start
```

Dashboard: http://localhost:3000

### Docker

```bash
# Optional: set Groq API key
export GROQ_API_KEY=your_key_here

docker-compose up --build
```

---

## Demo

1. Open `http://localhost:3000`
2. Click **"🚀 Simulate Incidents"** to run all 3 demo scenarios
3. Click any incident to see:
   - **Event Timeline** — chronological error events
   - **AI Root Cause Analysis** — reasoning chain and confidence score
   - **Recommended Actions** — with approve/reject buttons
4. Use **Approve** / **Reject** to exercise the governance workflow

### Demo Scenarios

| Scenario | Root Cause | Cascade Path |
|----------|-----------|--------------|
| Vault Auth Failure | Vault sealed/unreachable | Vault → ESO → Database → Auth → API |
| Database JWT Missing | JWT signing key lease expired | Vault → Auth → User Service → API |
| API Auth Cascade | TLS certificate expired | Cert Manager → API Gateway → Auth → User Service |

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check |
| POST | `/api/ingest` | Ingest log event |
| POST | `/api/ingest/batch` | Batch ingest |
| GET | `/api/incidents` | List incidents |
| GET | `/api/incidents/{id}` | Incident detail |
| POST | `/api/incidents/{id}/analyze` | Trigger AI analysis |
| GET | `/api/incidents/{id}/actions` | Get remediation actions |
| POST | `/api/actions/{id}/approve` | Approve action |
| POST | `/api/actions/{id}/reject` | Reject action |
| GET | `/api/graph` | Service dependency graph |
| POST | `/api/simulate` | Run demo scenario |
| POST | `/api/reset` | Reset all data |
| GET | `/api/stats` | Dashboard statistics |

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GROQ_API_KEY` | No | Groq API key for live AI reasoning. Falls back to mock responses if missing. |

---

## Project Structure

```
Devsick/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI entry point
│   │   ├── config.py            # Configuration
│   │   ├── models/              # Pydantic data models
│   │   ├── ingestion/           # Log ingestion layer
│   │   ├── correlation/         # Event correlation engine
│   │   ├── knowledge/           # Service dependency graph
│   │   ├── reasoning/           # AI engine + prompts
│   │   ├── recommendations/     # Remediation playbooks
│   │   ├── governance/          # Human-in-the-loop approval
│   │   ├── routes/              # API endpoints
│   │   └── data/                # Sample data
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── api/                 # API client
│   │   ├── components/          # Shared UI components
│   │   └── pages/               # Dashboard + Incident views
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```
