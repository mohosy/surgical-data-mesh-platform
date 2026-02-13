from spark.transform import (
    aggregate_procedure_kpis,
    detect_force_spike,
    normalize_event,
    risk_bucket,
    safety_score,
)


def test_risk_bucket_high() -> None:
    assert risk_bucket(45.0, 20) == "high"
    assert risk_bucket(10.0, 160) == "high"


def test_risk_bucket_medium() -> None:
    assert risk_bucket(25.0, 20) == "medium"
    assert risk_bucket(10.0, 100) == "medium"


def test_normalize_event_enriches_output() -> None:
    event = {
        "event_id": "evt-1",
        "patient_id": "pat-1",
        "procedure_id": "proc-1",
        "robot_arm": "arm_1",
        "step": "suturing",
        "force_newtons": 30,
        "velocity_mm_s": 12,
        "latency_ms": 85,
        "timestamp": "2026-02-13T18:20:00Z",
    }
    normalized = normalize_event(event)

    assert normalized["risk_bucket"] == "medium"
    assert normalized["event_day"] == "2026-02-13"
    assert normalized["safety_score"] > 0


def test_safety_score_accounts_for_error_penalty() -> None:
    without_error = safety_score(20.0, 80, False)
    with_error = safety_score(20.0, 80, True)
    assert with_error > without_error


def test_detect_force_spike() -> None:
    events = [
        {"timestamp": "2026-02-13T00:00:00Z", "force_newtons": 10},
        {"timestamp": "2026-02-13T00:00:01Z", "force_newtons": 16},
        {"timestamp": "2026-02-13T00:00:02Z", "force_newtons": 32},
    ]
    assert detect_force_spike(events, threshold=12) is True


def test_aggregate_procedure_kpis() -> None:
    events = [
        {"timestamp": "2026-02-13T00:00:00Z", "force_newtons": 12, "latency_ms": 35, "error_code": None},
        {"timestamp": "2026-02-13T00:00:01Z", "force_newtons": 28, "latency_ms": 80, "error_code": None},
        {"timestamp": "2026-02-13T00:00:02Z", "force_newtons": 46, "latency_ms": 165, "error_code": "HAPTIC_DRIFT"},
    ]
    kpis = aggregate_procedure_kpis(events)

    assert kpis["events"] == 3
    assert kpis["high_risk_events"] == 1
    assert kpis["avg_safety_score"] > 0
    assert kpis["max_force_newtons"] == 46.0
    assert kpis["force_spike_detected"] is True
