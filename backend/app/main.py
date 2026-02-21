import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .routes import ingest, incidents, actions, graph, simulate, alerts, observability
from .ingestion.loki_poller import loki_poller
from prometheus_fastapi_instrumentator import Instrumentator
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=settings.APP_DESCRIPTION,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instrument the app for Prometheus
resource = Resource.create({"service.name": settings.APP_NAME})
provider = TracerProvider(resource=resource)
trace.set_tracer_provider(provider)

# OTLP exporter — send to the collector (container name: otel-collector)
otlp_exporter = OTLPSpanExporter(endpoint="http://otel-collector:4317", insecure=True)
provider.add_span_processor(BatchSpanProcessor(otlp_exporter))

# Instrument FastAPI and outgoing requests
FastAPIInstrumentor().instrument_app(app)
RequestsInstrumentor().instrument()

Instrumentator().instrument(app).expose(app)

# Register routes
app.include_router(ingest.router)
app.include_router(incidents.router)
app.include_router(actions.router)
app.include_router(graph.router)
app.include_router(simulate.router)
app.include_router(alerts.router)
app.include_router(observability.router)

@app.on_event("startup")
async def startup_event():
    """Run on startup."""
    # Use create_task to run in background
    asyncio.create_task(loki_poller.poll())

@app.on_event("shutdown")
async def shutdown_event():
    """Run on shutdown."""
    loki_poller.stop()


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "groq_configured": bool(settings.GROQ_API_KEY),
    }


@app.get("/")
async def root():
    """Root endpoint — redirect to docs."""
    return {
        "message": f"Welcome to {settings.APP_NAME} v{settings.APP_VERSION}",
        "docs": "/docs",
        "health": "/api/health",
    }
