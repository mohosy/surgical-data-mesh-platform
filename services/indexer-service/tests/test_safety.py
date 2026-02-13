from datetime import datetime, timezone

from typing import Optional

from app.models import TelemetryEvent
from app.safety import SafetyAlertEngine


def _event(
    event_id: str, force: float, latency: int, error_code: Optional[str] = None
) -> TelemetryEvent:
    return TelemetryEvent(
        event_id=event_id,
        patient_id="pat-7",
        procedure_id="proc-9",
        robot_arm="arm_3",
        step="dissection",
        force_newtons=force,
        velocity_mm_s=18.0,
        latency_ms=latency,
        error_code=error_code,
        timestamp=datetime.now(timezone.utc),
        attributes={},
    )


def test_high_force_event_creates_alert() -> None:
    engine = SafetyAlertEngine()
    alerts = engine.ingest(_event("evt-001", 52.0, 50))

    assert len(alerts) == 1
    assert alerts[0]["risk_level"] in {"high", "critical"}


def test_patient_summary_tracks_counts_and_percentile() -> None:
    engine = SafetyAlertEngine()
    engine.ingest(_event("evt-001", 10.0, 40))
    engine.ingest(_event("evt-002", 45.0, 160, error_code="HAPTIC_DRIFT"))

    summary = engine.patient_summary("pat-7")
    assert summary["events"] == 2
    assert summary["high_risk_events"] >= 1
    assert summary["p95_latency_ms"] >= 40
