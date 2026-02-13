import os

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import PlainTextResponse

from .dedupe import EventDeduplicator
from .metrics import IngestMetrics
from .models import BatchIngestRequest, BatchIngestResponse, IngestResponse, TelemetryEvent
from .publisher import (
    InMemoryPublisher,
    KafkaEventPublisher,
    Publisher,
    event_partition_key,
)


def _build_publisher() -> Publisher:
    bootstrap = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "")
    if bootstrap:
        return KafkaEventPublisher(bootstrap)
    return InMemoryPublisher()


app = FastAPI(title="Telemetry Gateway", version="1.0.0")
app.state.publisher = _build_publisher()
app.state.metrics = IngestMetrics()
app.state.topic = os.getenv("KAFKA_TOPIC", "surgical.telemetry.raw")
app.state.deduplicator = EventDeduplicator(int(os.getenv("INGEST_DEDUPE_MAX_IDS", "50000")))


def _ingest_one(event: TelemetryEvent, request: Request) -> IngestResponse:
    key = event_partition_key(event.patient_id, event.procedure_id)
    topic = request.app.state.topic

    if request.app.state.deduplicator.is_duplicate(event.event_id):
        request.app.state.metrics.deduplicated_total += 1
        return IngestResponse(
            accepted=True,
            topic=topic,
            partition_key=key,
            event_id=event.event_id,
            deduplicated=True,
        )

    payload = event.model_dump(mode="json")
    request.app.state.publisher.publish(topic, key, payload)
    request.app.state.metrics.accepted_total += 1
    return IngestResponse(
        accepted=True,
        topic=topic,
        partition_key=key,
        event_id=event.event_id,
        deduplicated=False,
    )


@app.get("/health")
def health(request: Request) -> dict:
    publisher = request.app.state.publisher
    return {
        "status": "ok",
        "topic": request.app.state.topic,
        "publisher": type(publisher).__name__,
    }


@app.post("/events", response_model=IngestResponse)
def ingest(event: TelemetryEvent, request: Request) -> IngestResponse:
    try:
        return _ingest_one(event, request)
    except Exception as exc:  # pragma: no cover
        request.app.state.metrics.failed_total += 1
        raise HTTPException(status_code=502, detail=f"Publish failed: {exc}") from exc


@app.post("/events/batch", response_model=BatchIngestResponse)
def ingest_batch(batch: BatchIngestRequest, request: Request) -> BatchIngestResponse:
    metrics = request.app.state.metrics
    metrics.batch_requests_total += 1
    metrics.batch_events_total += len(batch.events)

    accepted = 0
    deduplicated = 0
    failed = 0
    failures: list[dict[str, str]] = []

    for event in batch.events:
        try:
            result = _ingest_one(event, request)
            accepted += 1
            if result.deduplicated:
                deduplicated += 1
        except Exception as exc:  # pragma: no cover
            failed += 1
            metrics.failed_total += 1
            failures.append({"event_id": event.event_id, "reason": str(exc)})

    return BatchIngestResponse(
        total=len(batch.events),
        accepted=accepted,
        deduplicated=deduplicated,
        failed=failed,
        failures=failures,
    )


@app.get("/metrics", response_class=PlainTextResponse)
def metrics(request: Request) -> str:
    return request.app.state.metrics.render_prometheus()
