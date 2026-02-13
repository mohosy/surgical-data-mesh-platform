from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import Deque, Dict, List

from .models import TelemetryEvent


LEVEL_ORDER = {"low": 0, "medium": 1, "high": 2, "critical": 3}


@dataclass
class RunningRiskStats:
    events: int = 0
    high_risk_events: int = 0
    critical_events: int = 0
    max_force_newtons: float = 0.0
    risk_score_total: float = 0.0
    latencies_ms: list[int] = field(default_factory=list)


class SafetyAlertEngine:
    def __init__(self, max_alerts: int = 1000, max_latency_samples: int = 2000) -> None:
        self.alerts: Deque[dict] = deque(maxlen=max_alerts)
        self.patient_stats: Dict[str, RunningRiskStats] = defaultdict(RunningRiskStats)
        self.procedure_stats: Dict[str, RunningRiskStats] = defaultdict(RunningRiskStats)
        self.max_latency_samples = max_latency_samples

    @staticmethod
    def risk_score(event: TelemetryEvent) -> float:
        score = min(45.0, event.force_newtons * 1.1)
        score += min(35.0, event.latency_ms / 4.0)
        if event.error_code:
            score += 20.0
        if event.step in {"dissection", "cauterization"} and event.force_newtons >= 30:
            score += 8.0
        return round(min(100.0, score), 2)

    @staticmethod
    def risk_level(score: float) -> str:
        if score >= 85:
            return "critical"
        if score >= 60:
            return "high"
        if score >= 35:
            return "medium"
        return "low"

    def _append_latency(self, stats: RunningRiskStats, latency_ms: int) -> None:
        stats.latencies_ms.append(latency_ms)
        if len(stats.latencies_ms) > self.max_latency_samples:
            stats.latencies_ms.pop(0)

    def _update_stats(self, stats: RunningRiskStats, event: TelemetryEvent, score: float, level: str) -> None:
        stats.events += 1
        stats.risk_score_total += score
        stats.max_force_newtons = max(stats.max_force_newtons, event.force_newtons)
        self._append_latency(stats, int(event.latency_ms))

        if level in {"high", "critical"}:
            stats.high_risk_events += 1
        if level == "critical":
            stats.critical_events += 1

    def _build_alert(self, event: TelemetryEvent, score: float, level: str, reasons: list[str]) -> dict:
        return {
            "event_id": event.event_id,
            "patient_id": event.patient_id,
            "procedure_id": event.procedure_id,
            "step": event.step,
            "risk_score": score,
            "risk_level": level,
            "reasons": reasons,
            "error_code": event.error_code,
            "timestamp": event.timestamp.isoformat(),
        }

    def _p95_latency(self, values: list[int]) -> float:
        if not values:
            return 0.0
        ordered = sorted(values)
        idx = int(round(0.95 * (len(ordered) - 1)))
        return float(ordered[idx])

    def ingest(self, event: TelemetryEvent) -> list[dict]:
        score = self.risk_score(event)
        level = self.risk_level(score)

        patient = self.patient_stats[event.patient_id]
        procedure = self.procedure_stats[event.procedure_id]
        self._update_stats(patient, event, score, level)
        self._update_stats(procedure, event, score, level)

        reasons: list[str] = []
        if event.force_newtons >= 40:
            reasons.append("high_force")
        if event.latency_ms >= 150:
            reasons.append("high_latency")
        if event.error_code:
            reasons.append("error_code_present")
        if level in {"high", "critical"} and not reasons:
            reasons.append("elevated_composite_risk")

        if not reasons:
            return []

        alert = self._build_alert(event, score, level, reasons)
        self.alerts.appendleft(alert)
        return [alert]

    def recent_alerts(self, limit: int = 20, min_level: str = "low") -> list[dict]:
        normalized_level = min_level.lower()
        threshold = LEVEL_ORDER.get(normalized_level, LEVEL_ORDER["low"])

        out: list[dict] = []
        for alert in self.alerts:
            if LEVEL_ORDER.get(alert["risk_level"], 0) >= threshold:
                out.append(alert)
            if len(out) >= limit:
                break
        return out

    def patient_summary(self, patient_id: str) -> dict:
        stats = self.patient_stats.get(patient_id, RunningRiskStats())
        avg = (stats.risk_score_total / stats.events) if stats.events else 0.0
        return {
            "patient_id": patient_id,
            "events": stats.events,
            "high_risk_events": stats.high_risk_events,
            "critical_events": stats.critical_events,
            "max_force_newtons": round(stats.max_force_newtons, 2),
            "avg_risk_score": round(avg, 2),
            "p95_latency_ms": round(self._p95_latency(stats.latencies_ms), 2),
        }

    def procedure_summary(self, procedure_id: str) -> dict:
        stats = self.procedure_stats.get(procedure_id, RunningRiskStats())
        avg = (stats.risk_score_total / stats.events) if stats.events else 0.0
        return {
            "procedure_id": procedure_id,
            "events": stats.events,
            "high_risk_events": stats.high_risk_events,
            "critical_events": stats.critical_events,
            "max_force_newtons": round(stats.max_force_newtons, 2),
            "avg_risk_score": round(avg, 2),
            "p95_latency_ms": round(self._p95_latency(stats.latencies_ms), 2),
        }
