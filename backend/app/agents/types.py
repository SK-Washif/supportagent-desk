"""Provider-neutral conversation types."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal, Protocol

from app.tools.registry import ToolDeclaration


@dataclass
class ToolCall:
    name: str
    args: Any
    id: str | None = None


@dataclass
class ToolResult:
    name: str
    response: dict[str, Any]
    call_id: str | None = None


@dataclass
class Message:
    role: Literal["user", "assistant", "tool"]
    text: str = ""
    tool_calls: list[ToolCall] = field(default_factory=list)
    tool_results: list[ToolResult] = field(default_factory=list)
    provider_payload: Any = None


@dataclass
class LLMTurn:
    text: str
    tool_calls: list[ToolCall]
    message: Message
    model: str | None = None


class LLMProvider(Protocol):
    model_name: str

    def generate(
        self,
        *,
        system_instruction: str,
        messages: list[Message],
        tools: list[ToolDeclaration],
    ) -> LLMTurn: ...