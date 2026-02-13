from datetime import datetime, timezone

from fastapi.testclient import TestClient

from app.main import app
from app.metrics import IndexerMetrics
from app.safety import SafetyAlertEngine
from app.sinks import InMemoryCaseDocumentStore, InMemorySearchStore, InMemoryTimelineStore


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


def _reset_app_state() -> None:
    app.state.timeline_store = InMemoryTimelineStore()
    app.state.search_store = InMemorySearchStore()
    app.state.docs_store = InMemoryCaseDocumentStore()
    app.state.metrics = IndexerMetrics()
    app.state.safety_engine = SafetyAlertEngine()


def test_index_and_query_flow() -> None:
    _reset_app_state()
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


def test_alert_feed_emits_high_risk_event() -> None:
    _reset_app_state()
    client = TestClient(app)
    payload = _payload()
    payload["event_id"] = "evt-alert-1"
    payload["force_newtons"] = 55.0
    payload["latency_ms"] = 180

    idx = client.post("/index", json=payload)
    assert idx.status_code == 200

    alerts = client.get("/alerts/recent", params={"min_level": "high"})
    assert alerts.status_code == 200
    assert len(alerts.json()) >= 1
    first = alerts.json()[0]
    assert first["event_id"] == "evt-alert-1"
    assert first["risk_level"] in {"high", "critical"}


def test_patient_and_procedure_risk_summary() -> None:
    _reset_app_state()
    client = TestClient(app)

    p1 = _payload()
    p1["event_id"] = "evt-sum-1"
    p1["procedure_id"] = "proc-A"
    p1["force_newtons"] = 20.0
    p1["latency_ms"] = 60

    p2 = _payload()
    p2["event_id"] = "evt-sum-2"
    p2["procedure_id"] = "proc-A"
    p2["force_newtons"] = 48.0
    p2["latency_ms"] = 160

    assert client.post("/index", json=p1).status_code == 200
    assert client.post("/index", json=p2).status_code == 200

    patient_summary = client.get("/patients/pat-123/risk-summary")
    assert patient_summary.status_code == 200
    p_body = patient_summary.json()
    assert p_body["events"] == 2
    assert p_body["high_risk_events"] >= 1
    assert p_body["max_force_newtons"] == 48.0

    procedure_summary = client.get("/procedures/proc-A/risk-summary")
    assert procedure_summary.status_code == 200
    s_body = procedure_summary.json()
    assert s_body["events"] == 2
    assert s_body["high_risk_events"] >= 1
