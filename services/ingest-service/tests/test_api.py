from datetime import datetime, timezone

from fastapi.testclient import TestClient

from app.dedupe import EventDeduplicator
from app.main import app
from app.metrics import IngestMetrics
from app.publisher import InMemoryPublisher


def _reset_app_state() -> None:
    app.state.publisher = InMemoryPublisher()
    app.state.metrics = IngestMetrics()
    app.state.deduplicator = EventDeduplicator(max_ids=100)


def _payload(event_id: str = "evt-001") -> dict:
    return {
        "event_id": event_id,
        "patient_id": "pat-123",
        "procedure_id": "proc-456",
        "robot_arm": "arm_1",
        "step": "suturing",
        "force_newtons": 17.2,
        "velocity_mm_s": 12.3,
        "latency_ms": 21,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "attributes": {"site": "USC"},
    }


def test_ingest_accepts_valid_event() -> None:
    _reset_app_state()
    client = TestClient(app)

    res = client.post("/events", json=_payload())
    assert res.status_code == 200
    assert res.json()["accepted"] is True
    assert res.json()["deduplicated"] is False
    assert len(app.state.publisher.messages) == 1


def test_health_endpoint() -> None:
    _reset_app_state()
    client = TestClient(app)
    res = client.get("/health")

    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_ingest_deduplicates_replayed_event() -> None:
    _reset_app_state()
    client = TestClient(app)

    first = client.post("/events", json=_payload("evt-dup-1"))
    second = client.post("/events", json=_payload("evt-dup-1"))

    assert first.status_code == 200
    assert second.status_code == 200
    assert second.json()["deduplicated"] is True
    assert len(app.state.publisher.messages) == 1


def test_batch_ingest_reports_deduplicates() -> None:
    _reset_app_state()
    client = TestClient(app)
    client.post("/events", json=_payload("evt-prior-1"))

    batch_payload = {
        "events": [
            _payload("evt-prior-1"),  # duplicate across requests
            _payload("evt-batch-2"),
            _payload("evt-batch-3"),
        ]
    }
    res = client.post("/events/batch", json=batch_payload)

    assert res.status_code == 200
    body = res.json()
    assert body["total"] == 3
    assert body["accepted"] == 3
    assert body["deduplicated"] == 1
    assert body["failed"] == 0
    assert len(app.state.publisher.messages) == 3
