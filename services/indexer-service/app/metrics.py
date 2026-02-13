from dataclasses import dataclass


@dataclass
class IndexerMetrics:
    indexed_total: int = 0
    search_queries_total: int = 0
    timeline_queries_total: int = 0
    alert_queries_total: int = 0
    alerts_emitted_total: int = 0
    risk_summary_queries_total: int = 0
    procedure_summary_queries_total: int = 0

    def render_prometheus(self) -> str:
        return "\n".join(
            [
                "# HELP indexer_events_indexed_total Number of indexed telemetry events",
                "# TYPE indexer_events_indexed_total counter",
                f"indexer_events_indexed_total {self.indexed_total}",
                "# HELP indexer_search_queries_total Number of search queries",
                "# TYPE indexer_search_queries_total counter",
                f"indexer_search_queries_total {self.search_queries_total}",
                "# HELP indexer_timeline_queries_total Number of timeline queries",
                "# TYPE indexer_timeline_queries_total counter",
                f"indexer_timeline_queries_total {self.timeline_queries_total}",
                "# HELP indexer_alert_queries_total Number of alert feed queries",
                "# TYPE indexer_alert_queries_total counter",
                f"indexer_alert_queries_total {self.alert_queries_total}",
                "# HELP indexer_alerts_emitted_total Number of emitted safety alerts",
                "# TYPE indexer_alerts_emitted_total counter",
                f"indexer_alerts_emitted_total {self.alerts_emitted_total}",
                "# HELP indexer_risk_summary_queries_total Number of patient risk summary queries",
                "# TYPE indexer_risk_summary_queries_total counter",
                f"indexer_risk_summary_queries_total {self.risk_summary_queries_total}",
                "# HELP indexer_procedure_summary_queries_total Number of procedure risk summary queries",
                "# TYPE indexer_procedure_summary_queries_total counter",
                f"indexer_procedure_summary_queries_total {self.procedure_summary_queries_total}",
                "",
            ]
        )
