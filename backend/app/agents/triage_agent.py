"""The autonomous triage agent: a bounded, fully traced LLM tool-calling loop."""

from __future__ import annotations

import json
import logging
import re
from typing import Any

from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.agents import trace as ev
from app.agents.prompts import REPAIR_INSTRUCTION, SYSTEM_INSTRUCTION, build_ticket_message
from app.agents.trace import TraceRecorder
from app.agents.types import LLMProvider, LLMTurn, Message, ToolCall, ToolResult
from app.core.exceptions import AgentLimitError, InvalidLLMResponseError, ToolError
from app.models import Ticket
from app.schemas.agent import LLMTriageOutput, TriageResult
from app.tools import registry
from app.tools.definitions import ToolContext

logger = logging.getLogger(__name__)

MAX_REPAIR_ATTEMPTS = 1
_FENCE = re.compile(r"^```(?:json)?\s*|\s*```$", re.I)


def parse_final_output(text: str) -> LLMTriageOutput:
    """Parse and validate the model's final JSON. Raises ValueError with a short reason."""
    cleaned = _FENCE.sub("", text.strip()).strip()
    data: Any
    try:
        data = json.loads(cleaned)
    except ValueError:
        start, end = cleaned.find("{"), cleaned.rfind("}")
        if start == -1 or end <= start:
            raise ValueError("the reply was not a JSON object") from None
        try:
            data = json.loads(cleaned[start : end + 1])
        except ValueError:
            raise ValueError("the reply was not valid JSON") from None
    if not isinstance(data, dict):
        raise ValueError("the reply was not a JSON object")
    try:
        return LLMTriageOutput.model_validate(data)
    except ValidationError as exc:
        fields = ", ".join(
            sorted({str(e["loc"][0]) if e["loc"] else "reply" for e in exc.errors()})
        )
        raise ValueError(f"invalid or missing fields: {fields}") from exc


class TriageAgent:
    def __init__(
        self,
        *,
        provider: LLMProvider,
        db: Session,
        recorder: TraceRecorder,
        max_iterations: int,
    ):
        self._provider = provider
        self._db = db
        self._trace = recorder
        self._max_iterations = max_iterations

    def run(self, ticket: Ticket) -> TriageResult:
        self._trace.record(
            ev.AGENT_STARTED,
            "Agent started",
            {
                "ticket_id": ticket.ticket_id,
                "model": self._provider.model_name,
                "max_iterations": self._max_iterations,
            },
        )
        self._trace.record(
            ev.TICKET_CONTEXT_LOADED,
            "Ticket context loaded",
            {
                "ticket_id": ticket.ticket_id,
                "customer_id": ticket.customer_id,
                "order_id": ticket.order_id,
                "subject": ticket.subject,
                "message": ticket.message,
            },
        )

        ctx = ToolContext(db=self._db, customer_id=ticket.customer_id)
        declarations = registry.list_declarations()
        messages: list[Message] = [Message(role="user", text=build_ticket_message(ticket))]
        tools_used: list[str] = []
        repairs = 0
        repair_reason: str | None = None

        for iteration in range(1, self._max_iterations + 1):
            self._trace.record(
                ev.LLM_REQUEST_SENT,
                f"Request sent to {self._provider.model_name}"
                + (" (format repair)" if repair_reason else ""),
                {
                    "iteration": iteration,
                    "model": self._provider.model_name,
                    "message_count": len(messages),
                    "tools_available": [d.name for d in declarations],
                    **(
                        {"reason": "format_repair", "problem": repair_reason}
                        if repair_reason
                        else {}
                    ),
                },
            )
            repair_reason = None
            turn = self._provider.generate(
                system_instruction=SYSTEM_INSTRUCTION, messages=messages, tools=declarations
            )
            messages.append(turn.message)

            if turn.tool_calls:
                results = [
                    self._handle_call(c, ctx, iteration, tools_used) for c in turn.tool_calls
                ]
                messages.append(Message(role="tool", tool_results=results))
                continue

            try:
                output = parse_final_output(turn.text)
            except ValueError as exc:
                if repairs >= MAX_REPAIR_ATTEMPTS:
                    raise InvalidLLMResponseError(
                        f"The model's final answer failed validation: {exc}."
                    ) from exc
                repairs += 1
                repair_reason = str(exc)
                messages.append(
                    Message(role="user", text=REPAIR_INSTRUCTION.format(problem=repair_reason))
                )
                continue

            result = self._finalize(ticket, output, tools_used, turn)
            return result

        raise AgentLimitError(
            f"The agent reached the limit of {self._max_iterations} iterations "
            "without a final answer."
        )

    # ------------------------------------------------------------------------------------
    def _finalize(
        self, ticket: Ticket, output: LLMTriageOutput, tools_used: list[str], turn: LLMTurn
    ) -> TriageResult:
        result = TriageResult(
            ticket_id=ticket.ticket_id,
            customer_response=output.customer_response,
            resolution_tag=output.resolution_tag,
            decision_summary=output.decision_summary,
            tools_used=list(tools_used),
        )
        self._trace.record(
            ev.FINAL_RESPONSE_GENERATED,
            "Final response generated and validated",
            {
                "resolution_tag": result.resolution_tag,
                "decision_summary": result.decision_summary,
                "tools_used": result.tools_used,
                "customer_response": result.customer_response,
            },
        )
        return result

    def _handle_call(
        self, call: ToolCall, ctx: ToolContext, iteration: int, tools_used: list[str]
    ) -> ToolResult:
        name = call.name or ""
        known = name in registry.tool_names()
        self._trace.record(
            ev.TOOL_SELECTED,
            f"Model selected tool: {name or '(unnamed)'}",
            {
                "tool": name,
                "arguments": call.args,
                "call_id": call.id,
                "iteration": iteration,
                "registered": known,
            },
            status=ev.SUCCESS if known else ev.FAILED,
        )

        def failure(err: ToolError) -> ToolResult:
            self._trace.record(
                ev.TOOL_RESULT_RETURNED,
                f"Error returned to model from {name or '(unnamed)'}",
                {"tool": name, "error": {"code": err.code, "message": err.message}},
                status=ev.FAILED,
            )
            return ToolResult(
                name=name,
                call_id=call.id,
                response={"error": {"code": err.code, "message": err.message}},
            )

        if not known:
            return failure(ToolError("unknown_tool", f"Tool '{name}' is not available."))

        try:
            args = registry.validate_arguments(name, call.args)
        except ToolError as err:
            self._trace.record(
                ev.TOOL_ARGUMENTS_VALIDATED,
                f"Arguments rejected for {name}",
                {
                    "tool": name,
                    "arguments": call.args,
                    "error": {"code": err.code, "message": err.message},
                },
                status=ev.FAILED,
            )
            return failure(err)
        self._trace.record(
            ev.TOOL_ARGUMENTS_VALIDATED,
            f"Arguments validated for {name}",
            {"tool": name, "arguments": args.model_dump()},
        )

        self._trace.record(
            ev.TOOL_EXECUTION_STARTED,
            f"Executing {name}",
            {"tool": name, "arguments": args.model_dump()},
        )
        tools_used.append(name) if name not in tools_used else None
        try:
            output = registry.execute_tool(name, args, ctx)
        except ToolError as err:
            logger.warning("Tool %s failed: %s", name, err.code)
            self._db.rollback()
            self._trace.record(
                ev.TOOL_EXECUTION_COMPLETED,
                f"{name} failed",
                {"tool": name, "error": {"code": err.code, "message": err.message}},
                status=ev.FAILED,
            )
            return failure(err)
        self._trace.record(
            ev.TOOL_EXECUTION_COMPLETED, f"{name} completed", {"tool": name, "raw_output": output}
        )
        self._trace.record(
            ev.TOOL_RESULT_RETURNED,
            f"Result of {name} returned to model",
            {"tool": name, "response": output},
        )
        return ToolResult(name=name, call_id=call.id, response=output)
