from datetime import datetime


def risk_bucket(force_newtons: float, latency_ms: int) -> str:
    if force_newtons >= 40 or latency_ms >= 150:
        return "high"
    if force_newtons >= 20 or latency_ms >= 80:
        return "medium"
    return "low"


def safety_score(force_newtons: float, latency_ms: int, has_error: bool = False) -> float:
    score = min(45.0, force_newtons * 1.1)
    score += min(35.0, latency_ms / 4.0)
    if has_error:
        score += 20.0
    return round(min(100.0, score), 2)


def detect_force_spike(events: list[dict], threshold: float = 12.0) -> bool:
    if len(events) < 2:
        return False
    sorted_events = sorted(events, key=lambda e: e["timestamp"])
    deltas = []
    for prev, curr in zip(sorted_events, sorted_events[1:]):
        deltas.append(float(curr["force_newtons"]) - float(prev["force_newtons"]))
    return max(deltas) >= threshold


def aggregate_procedure_kpis(events: list[dict]) -> dict:
    if not events:
        return {
            "events": 0,
            "high_risk_events": 0,
            "avg_safety_score": 0.0,
            "max_force_newtons": 0.0,
            "p95_latency_ms": 0.0,
            "force_spike_detected": False,
        }

    scores = [
        safety_score(
            float(event["force_newtons"]),
            int(event["latency_ms"]),
            bool(event.get("error_code")),
        )
        for event in events
    ]
    latencies = sorted(int(event["latency_ms"]) for event in events)
    p95_index = int(round(0.95 * (len(latencies) - 1)))

    return {
        "events": len(events),
        "high_risk_events": sum(
            1 for event in events if risk_bucket(float(event["force_newtons"]), int(event["latency_ms"])) == "high"
        ),
        "avg_safety_score": round(sum(scores) / len(scores), 2),
        "max_force_newtons": round(max(float(event["force_newtons"]) for event in events), 2),
        "p95_latency_ms": float(latencies[p95_index]),
        "force_spike_detected": detect_force_spike(events),
    }


def normalize_event(event: dict) -> dict:
    ts = datetime.fromisoformat(event["timestamp"].replace("Z", "+00:00"))
    out = dict(event)
    out["event_day"] = ts.strftime("%Y-%m-%d")
    out["risk_bucket"] = risk_bucket(float(event["force_newtons"]), int(event["latency_ms"]))
    out["safety_score"] = safety_score(
        float(event["force_newtons"]),
        int(event["latency_ms"]),
        bool(event.get("error_code")),
    )
    return out
