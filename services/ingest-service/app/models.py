from datetime import datetime
from typing import Optional, Union

from pydantic import BaseModel, Field, model_validator


class TelemetryEvent(BaseModel):
    event_id: str = Field(min_length=6)
    patient_id: str = Field(min_length=3)
    procedure_id: str = Field(min_length=3)
    robot_arm: str = Field(pattern=r"^(arm_[1-4]|camera)$")
    step: str = Field(min_length=2)
    force_newtons: float = Field(ge=0, le=200)
    velocity_mm_s: float = Field(ge=0, le=300)
    latency_ms: int = Field(ge=0, le=2000)
    error_code: Optional[str] = None
    timestamp: datetime
    attributes: dict[str, Union[str, int, float]] = Field(default_factory=dict)


class IngestResponse(BaseModel):
    accepted: bool
    topic: str
    partition_key: str
    event_id: str
    deduplicated: bool = False


class BatchIngestRequest(BaseModel):
    events: list[TelemetryEvent] = Field(min_length=1, max_length=1000)

    @model_validator(mode="after")
    def check_unique_event_ids(self) -> "BatchIngestRequest":
        ids = [event.event_id for event in self.events]
        if len(set(ids)) != len(ids):
            raise ValueError("Batch contains duplicate event_id values")
        return self


class BatchIngestResponse(BaseModel):
    total: int
    accepted: int
    deduplicated: int
    failed: int
    failures: list[dict[str, str]] = Field(default_factory=list)
