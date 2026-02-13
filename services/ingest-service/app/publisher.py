import json
from typing import Protocol

from kafka import KafkaProducer


def event_partition_key(patient_id: str, procedure_id: str) -> str:
    return f"{patient_id}:{procedure_id}"


class Publisher(Protocol):
    def publish(self, topic: str, key: str, payload: dict) -> None:
        ...


class InMemoryPublisher:
    def __init__(self) -> None:
        self.messages: list[dict] = []

    def publish(self, topic: str, key: str, payload: dict) -> None:
        self.messages.append({"topic": topic, "key": key, "payload": payload})


class KafkaEventPublisher:
    def __init__(self, bootstrap_servers: str) -> None:
        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            key_serializer=lambda v: v.encode("utf-8"),
            linger_ms=10,
            retries=3,
        )

    def publish(self, topic: str, key: str, payload: dict) -> None:
        self.producer.send(topic, key=key, value=payload).get(timeout=5)
