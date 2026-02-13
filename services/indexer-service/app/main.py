from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse

from .metrics import IndexerMetrics
from .models import IndexResponse, TelemetryEvent
from .safety import SafetyAlertEngine
from .sinks import build_stores


app = FastAPI(title="Safety Indexer", version="1.0.0")
timeline_store, search_store, docs_store = build_stores()
app.state.timeline_store = timeline_store
app.state.search_store = search_store
app.state.docs_store = docs_store
app.state.metrics = IndexerMetrics()
app.state.safety_engine = SafetyAlertEngine()


@app.get("/health")
def health(request: Request) -> dict:
    return {
        "status": "ok",
        "timeline_backend": type(request.app.state.timeline_store).__name__,
        "search_backend": type(request.app.state.search_store).__name__,
        "docs_backend": type(request.app.state.docs_store).__name__,
    }


@app.post("/index", response_model=IndexResponse)
def index_event(event: TelemetryEvent, request: Request) -> IndexResponse:
    request.app.state.timeline_store.write(event)
    request.app.state.search_store.index(event)
    request.app.state.docs_store.upsert(event)
    emitted_alerts = request.app.state.safety_engine.ingest(event)
    request.app.state.metrics.indexed_total += 1
    request.app.state.metrics.alerts_emitted_total += len(emitted_alerts)
    return IndexResponse(indexed=True, event_id=event.event_id)


@app.get("/patients/{patient_id}/timeline")
def timeline(patient_id: str, request: Request) -> list[dict]:
    request.app.state.metrics.timeline_queries_total += 1
    return request.app.state.timeline_store.by_patient(patient_id)


@app.get("/search")
def search(q: str, request: Request) -> list[dict]:
    request.app.state.metrics.search_queries_total += 1
    return request.app.state.search_store.query(q)


@app.get("/alerts/recent")
def alerts_recent(request: Request, limit: int = 20, min_level: str = "low") -> list[dict]:
    request.app.state.metrics.alert_queries_total += 1
    safe_limit = max(1, min(200, limit))
    return request.app.state.safety_engine.recent_alerts(limit=safe_limit, min_level=min_level)


@app.get("/patients/{patient_id}/risk-summary")
def patient_risk_summary(patient_id: str, request: Request) -> dict:
    request.app.state.metrics.risk_summary_queries_total += 1
    return request.app.state.safety_engine.patient_summary(patient_id)


@app.get("/procedures/{procedure_id}/risk-summary")
def procedure_risk_summary(procedure_id: str, request: Request) -> dict:
    request.app.state.metrics.procedure_summary_queries_total += 1
    return request.app.state.safety_engine.procedure_summary(procedure_id)


@app.get("/metrics", response_class=PlainTextResponse)
def metrics(request: Request) -> str:
    return request.app.state.metrics.render_prometheus()
