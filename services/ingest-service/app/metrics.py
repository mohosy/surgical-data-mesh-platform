from dataclasses import dataclass


@dataclass
class IngestMetrics:
    accepted_total: int = 0
    failed_total: int = 0
    deduplicated_total: int = 0
    batch_requests_total: int = 0
    batch_events_total: int = 0

    def render_prometheus(self) -> str:
        return "\n".join(
            [
                "# HELP ingest_events_accepted_total Number of accepted telemetry events",
                "# TYPE ingest_events_accepted_total counter",
                f"ingest_events_accepted_total {self.accepted_total}",
                "# HELP ingest_events_failed_total Number of failed telemetry events",
                "# TYPE ingest_events_failed_total counter",
                f"ingest_events_failed_total {self.failed_total}",
                "# HELP ingest_events_deduplicated_total Number of deduplicated telemetry events",
                "# TYPE ingest_events_deduplicated_total counter",
                f"ingest_events_deduplicated_total {self.deduplicated_total}",
                "# HELP ingest_batch_requests_total Number of batch ingest requests",
                "# TYPE ingest_batch_requests_total counter",
                f"ingest_batch_requests_total {self.batch_requests_total}",
                "# HELP ingest_batch_events_total Number of events received through batch ingest",
                "# TYPE ingest_batch_events_total counter",
                f"ingest_batch_events_total {self.batch_events_total}",
                "",
            ]
        )
