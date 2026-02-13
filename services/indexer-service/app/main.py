from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse

from .metrics import IndexerMetrics
from .models import IndexResponse, TelemetryEvent
from .sinks import build_stores


app = FastAPI(title="Safety Indexer", version="1.0.0")
timeline_store, search_store, docs_store = build_stores()
app.state.timeline_store = timeline_store
app.state.search_store = search_store
app.state.docs_store = docs_store
app.state.metrics = IndexerMetrics()


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
    request.app.state.metrics.indexed_total += 1
    return IndexResponse(indexed=True, event_id=event.event_id)


@app.get("/patients/{patient_id}/timeline")
def timeline(patient_id: str, request: Request) -> list[dict]:
    request.app.state.metrics.timeline_queries_total += 1
    return request.app.state.timeline_store.by_patient(patient_id)


@app.get("/search")
def search(q: str, request: Request) -> list[dict]:
    request.app.state.metrics.search_queries_total += 1
    return request.app.state.search_store.query(q)


@app.get("/metrics", response_class=PlainTextResponse)
def metrics(request: Request) -> str:
    return request.app.state.metrics.render_prometheus()
