from datetime import datetime, timezone

from fastapi.testclient import TestClient

from app.main import app


def _payload() -> dict:
    return {
        "event_id": "evt-123",
        "patient_id": "pat-123",
        "procedure_id": "proc-456",
        "robot_arm": "arm_2",
        "step": "dissection",
        "force_newtons": 11.0,
        "velocity_mm_s": 14.0,
        "latency_ms": 26,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "attributes": {"room": "OR-2"},
    }


def test_index_and_query_flow() -> None:
    client = TestClient(app)

    idx = client.post("/index", json=_payload())
    assert idx.status_code == 200
    assert idx.json()["indexed"] is True

    timeline = client.get("/patients/pat-123/timeline")
    assert timeline.status_code == 200
    assert len(timeline.json()) == 1

    search = client.get("/search", params={"q": "dissec"})
    assert search.status_code == 200
    assert len(search.json()) == 1
