from datetime import datetime, timezone

from app.models import TelemetryEvent
from app.sinks import InMemoryCaseDocumentStore, InMemorySearchStore, InMemoryTimelineStore


def _event(step: str, force: float) -> TelemetryEvent:
    return TelemetryEvent(
        event_id=f"evt-{step}",
        patient_id="pat-1",
        procedure_id="proc-1",
        robot_arm="arm_1",
        step=step,
        force_newtons=force,
        velocity_mm_s=20,
        latency_ms=30,
        timestamp=datetime.now(timezone.utc),
        attributes={},
    )


def test_timeline_store_orders_events() -> None:
    store = InMemoryTimelineStore()
    store.write(_event("incision", 8.0))
    store.write(_event("suturing", 16.0))

    rows = store.by_patient("pat-1")
    assert len(rows) == 2


def test_search_store_finds_matching_steps() -> None:
    store = InMemorySearchStore()
    store.index(_event("suturing", 10.0))
    store.index(_event("closure", 9.0))

    result = store.query("sutu")
    assert len(result) == 1
    assert result[0]["step"] == "suturing"


def test_docs_store_keeps_aggregates() -> None:
    store = InMemoryCaseDocumentStore()
    store.upsert(_event("incision", 12.0))
    store.upsert(_event("suturing", 20.0))

    summary = store.docs["pat-1:proc-1"]
    assert summary["events"] == 2
    assert summary["max_force_newtons"] == 20.0
    assert summary["last_step"] == "suturing"
