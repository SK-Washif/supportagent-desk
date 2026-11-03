"""Central tool registry. Only tools registered here can ever be executed."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from pydantic import ValidationError

from app.core.exceptions import ToolError
from app.tools.customer_tools import get_user_tier
from app.tools.definitions import (
    GetOrderStatusArgs,
    GetUserTierArgs,
    ToolContext,
    ToolSpec,
)
from app.tools.order_tools import get_order_status

_TOOLS: dict[str, ToolSpec] = {
    spec.name: spec
    for spec in (
        ToolSpec(
            name="get_order_status",
            description=(
                "Look up the delivery status and estimated delivery of a customer order. "
                "Use when the ticket depends on where an order is or when it will arrive."
            ),
            args_model=GetOrderStatusArgs,
            handler=get_order_status,
        ),
        ToolSpec(
            name="get_user_tier",
            description=(
                "Look up a customer's current subscription tier and whether they are eligible "
                "to upgrade. Use when the ticket depends on the customer's plan or account tier."
            ),
            args_model=GetUserTierArgs,
            handler=get_user_tier,
        ),
    )
}


@dataclass(frozen=True)
class ToolDeclaration:
    name: str
    description: str
    parameters_schema: dict[str, Any]


def list_declarations() -> list[ToolDeclaration]:
    return [ToolDeclaration(t.name, t.description, t.parameters_schema) for t in _TOOLS.values()]


def tool_names() -> list[str]:
    return list(_TOOLS)


def get_tool(name: str) -> ToolSpec:
    spec = _TOOLS.get(name)
    if spec is None:
        raise ToolError("unknown_tool", f"Tool '{name}' is not available.")
    return spec


def validate_arguments(name: str, raw_args: Any) -> Any:
    """Return validated args for a registered tool, or raise ToolError."""
    spec = get_tool(name)
    if not isinstance(raw_args, dict):
        raise ToolError("invalid_arguments", "Tool arguments must be a JSON object.")
    try:
        return spec.args_model.model_validate(raw_args)
    except ValidationError as exc:
        problems = "; ".join(
            f"{'.'.join(str(p) for p in err['loc']) or 'arguments'}: {err['msg']}"
            for err in exc.errors()
        )
        raise ToolError("invalid_arguments", f"Invalid arguments: {problems}") from exc


def execute_tool(name: str, validated_args: Any, ctx: ToolContext) -> dict[str, Any]:
    spec = get_tool(name)
    try:
        return spec.handler(ctx, validated_args)
    except ToolError:
        raise
    except Exception as exc:  # unexpected failure inside a tool
        raise ToolError("tool_execution_failed", f"Tool '{name}' failed unexpectedly.") from exc
