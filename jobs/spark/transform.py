from datetime import datetime


def risk_bucket(force_newtons: float, latency_ms: int) -> str:
    if force_newtons >= 40 or latency_ms >= 150:
        return "high"
    if force_newtons >= 20 or latency_ms >= 80:
        return "medium"
    return "low"


def normalize_event(event: dict) -> dict:
    ts = datetime.fromisoformat(event["timestamp"].replace("Z", "+00:00"))
    out = dict(event)
    out["event_day"] = ts.strftime("%Y-%m-%d")
    out["risk_bucket"] = risk_bucket(float(event["force_newtons"]), int(event["latency_ms"]))
    return out
