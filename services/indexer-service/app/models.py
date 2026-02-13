from datetime import datetime
from typing import Optional, Union

from pydantic import BaseModel, Field


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


class IndexResponse(BaseModel):
    indexed: bool
    event_id: str
