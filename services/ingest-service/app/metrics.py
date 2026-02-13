from dataclasses import dataclass


@dataclass
class IngestMetrics:
    accepted_total: int = 0
    failed_total: int = 0

    def render_prometheus(self) -> str:
        return "\n".join(
            [
                "# HELP ingest_events_accepted_total Number of accepted telemetry events",
                "# TYPE ingest_events_accepted_total counter",
                f"ingest_events_accepted_total {self.accepted_total}",
                "# HELP ingest_events_failed_total Number of failed telemetry events",
                "# TYPE ingest_events_failed_total counter",
                f"ingest_events_failed_total {self.failed_total}",
                "",
            ]
        )
