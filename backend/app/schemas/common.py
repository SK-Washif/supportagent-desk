from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict, field_serializer

T = TypeVar("T")


class ApiModel(BaseModel):
    """Base for API output: ORM-friendly, naive datetimes serialised as UTC with 'Z'."""

    model_config = ConfigDict(from_attributes=True)

    @field_serializer("*", mode="wrap", check_fields=False)
    def _serialize_datetimes(self, value: Any, handler: Any) -> Any:
        if isinstance(value, datetime):
            if value.tzinfo is None:
                value = value.replace(tzinfo=UTC)
            return value.astimezone(UTC).isoformat().replace("+00:00", "Z")
        return handler(value)


class ErrorBody(BaseModel):
    code: str
    message: str
    details: dict[str, Any] = {}


class ApiResponse(BaseModel, Generic[T]):
    success: bool = True
    data: T | None = None
    error: ErrorBody | None = None
