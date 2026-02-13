from spark.transform import normalize_event, risk_bucket


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
