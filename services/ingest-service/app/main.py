import os

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import PlainTextResponse

from .metrics import IngestMetrics
from .models import IngestResponse, TelemetryEvent
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
    key = event_partition_key(event.patient_id, event.procedure_id)
    payload = event.model_dump(mode="json")

    try:
        request.app.state.publisher.publish(request.app.state.topic, key, payload)
        request.app.state.metrics.accepted_total += 1
    except Exception as exc:  # pragma: no cover
        request.app.state.metrics.failed_total += 1
        raise HTTPException(status_code=502, detail=f"Publish failed: {exc}") from exc

    return IngestResponse(accepted=True, topic=request.app.state.topic, partition_key=key)


@app.get("/metrics", response_class=PlainTextResponse)
def metrics(request: Request) -> str:
    return request.app.state.metrics.render_prometheus()
