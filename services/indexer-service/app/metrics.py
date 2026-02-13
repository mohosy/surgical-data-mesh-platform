from dataclasses import dataclass


@dataclass
class IndexerMetrics:
    indexed_total: int = 0
    search_queries_total: int = 0
    timeline_queries_total: int = 0

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
                "",
            ]
        )
