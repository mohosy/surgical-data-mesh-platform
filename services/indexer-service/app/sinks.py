import os
from collections import defaultdict
from dataclasses import dataclass
from typing import Protocol

from .models import TelemetryEvent


class TimelineStore(Protocol):
    def write(self, event: TelemetryEvent) -> None:
        ...

    def by_patient(self, patient_id: str) -> list[dict]:
        ...


class SearchStore(Protocol):
    def index(self, event: TelemetryEvent) -> None:
        ...

    def query(self, text: str) -> list[dict]:
        ...


class CaseDocumentStore(Protocol):
    def upsert(self, event: TelemetryEvent) -> None:
        ...


@dataclass
class InMemoryTimelineStore:
    events: dict[str, list[dict]]

    def __init__(self) -> None:
        self.events = defaultdict(list)

    def write(self, event: TelemetryEvent) -> None:
        self.events[event.patient_id].append(event.model_dump(mode="json"))

    def by_patient(self, patient_id: str) -> list[dict]:
        return sorted(self.events.get(patient_id, []), key=lambda x: x["timestamp"])


@dataclass
class InMemorySearchStore:
    docs: list[dict]

    def __init__(self) -> None:
        self.docs = []

    def index(self, event: TelemetryEvent) -> None:
        self.docs.append(event.model_dump(mode="json"))

    def query(self, text: str) -> list[dict]:
        text_lower = text.lower()
        return [
            d
            for d in self.docs
            if text_lower in d["step"].lower()
            or (d.get("error_code") and text_lower in d["error_code"].lower())
        ]


@dataclass
class InMemoryCaseDocumentStore:
    docs: dict[str, dict]

    def __init__(self) -> None:
        self.docs = {}

    def upsert(self, event: TelemetryEvent) -> None:
        key = f"{event.patient_id}:{event.procedure_id}"
        existing = self.docs.get(
            key,
            {
                "patient_id": event.patient_id,
                "procedure_id": event.procedure_id,
                "last_step": None,
                "max_force_newtons": 0.0,
                "events": 0,
            },
        )
        existing["last_step"] = event.step
        existing["max_force_newtons"] = max(existing["max_force_newtons"], event.force_newtons)
        existing["events"] += 1
        self.docs[key] = existing


# Optional adapters for production backends (Cassandra/Elasticsearch/MongoDB)
# This keeps the service runnable locally while still showing integration boundaries.


class CassandraTimelineStore(InMemoryTimelineStore):
    pass


class ElasticsearchSearchStore(InMemorySearchStore):
    pass


class MongoCaseDocumentStore(InMemoryCaseDocumentStore):
    pass


def build_stores() -> tuple[TimelineStore, SearchStore, CaseDocumentStore]:
    timeline_backend = os.getenv("TIMELINE_BACKEND", "memory").lower()
    search_backend = os.getenv("SEARCH_BACKEND", "memory").lower()
    docs_backend = os.getenv("DOCS_BACKEND", "memory").lower()

    timeline: TimelineStore = (
        CassandraTimelineStore() if timeline_backend == "cassandra" else InMemoryTimelineStore()
    )
    search: SearchStore = (
        ElasticsearchSearchStore() if search_backend == "elasticsearch" else InMemorySearchStore()
    )
    docs: CaseDocumentStore = (
        MongoCaseDocumentStore() if docs_backend == "mongodb" else InMemoryCaseDocumentStore()
    )
    return timeline, search, docs
