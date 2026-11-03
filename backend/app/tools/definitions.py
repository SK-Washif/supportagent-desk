"""Provider-neutral tool definitions and validated argument models."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session


@dataclass(frozen=True)
class ToolContext:
    """Execution scope for a tool call: the DB and the customer who owns the ticket."""

    db: Session
    customer_id: str


class GetOrderStatusArgs(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    order_id: str = Field(pattern=r"^ORD-\d{1,12}$", description="Order identifier, e.g. ORD-9012")


class GetUserTierArgs(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    user_id: str = Field(pattern=r"^USR-\d{1,12}$", description="Customer identifier, e.g. USR-204")


@dataclass(frozen=True)
class ToolSpec:
    name: str
    description: str
    args_model: type[BaseModel]
    handler: Callable[[ToolContext, Any], dict[str, Any]]

    @property
    def parameters_schema(self) -> dict[str, Any]:
        schema = self.args_model.model_json_schema()
        schema.pop("title", None)
        for prop in schema.get("properties", {}).values():
            prop.pop("title", None)
        return schema
