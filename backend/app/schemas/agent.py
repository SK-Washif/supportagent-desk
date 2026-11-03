from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.common import ApiModel

ResolutionTag = Literal["Auto-Resolve", "Escalate to Sales"]


class LLMTriageOutput(BaseModel):
    """What we accept from the model. Extra keys are ignored, never trusted."""

    model_config = ConfigDict(extra="ignore")

    customer_response: str = Field(min_length=1, max_length=4000)
    resolution_tag: ResolutionTag
    decision_summary: str = Field(min_length=1, max_length=600)

    @field_validator("customer_response", "decision_summary")
    @classmethod
    def _not_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("must not be blank")
        return value


class TriageResult(BaseModel):
    """Final validated agent output (blueprint schema)."""

    ticket_id: str
    customer_response: str = Field(min_length=1, max_length=4000)
    resolution_tag: ResolutionTag
    decision_summary: str = Field(min_length=1, max_length=600)
    tools_used: list[str]


class TraceOut(ApiModel):
    id: int
    agent_run_id: int
    sequence_number: int
    event_type: str
    event_title: str
    details: dict[str, Any]
    status: str
    created_at: datetime


class RunOut(ApiModel):
    id: int
    ticket_id: str
    status: str
    resolution_tag: str | None
    customer_response: str | None
    decision_summary: str | None
    tools_used: list[str]
    model_name: str | None
    started_at: datetime
    completed_at: datetime | None
    error_code: str | None
    error_message: str | None
