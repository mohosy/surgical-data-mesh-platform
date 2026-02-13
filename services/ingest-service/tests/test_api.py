from datetime import datetime, timezone

from fastapi.testclient import TestClient

from app.main import app
from app.publisher import InMemoryPublisher


def test_ingest_accepts_valid_event() -> None:
    app.state.publisher = InMemoryPublisher()
    client = TestClient(app)

    payload = {
        "event_id": "evt-001",
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

    res = client.post("/events", json=payload)
    assert res.status_code == 200
    assert res.json()["accepted"] is True


def test_health_endpoint() -> None:
    app.state.publisher = InMemoryPublisher()
    client = TestClient(app)
    res = client.get("/health")

    assert res.status_code == 200
    assert res.json()["status"] == "ok"
