"""Persists observable execution events AS the agent runs (one commit per event)."""

from __future__ import annotations

import re
from typing import Any

from sqlalchemy.orm import Session

from app.core.time import utcnow
from app.models import ExecutionTrace

AGENT_STARTED = "AGENT_STARTED"
TICKET_CONTEXT_LOADED = "TICKET_CONTEXT_LOADED"
LLM_REQUEST_SENT = "LLM_REQUEST_SENT"
TOOL_SELECTED = "TOOL_SELECTED"
TOOL_ARGUMENTS_VALIDATED = "TOOL_ARGUMENTS_VALIDATED"
TOOL_EXECUTION_STARTED = "TOOL_EXECUTION_STARTED"
TOOL_EXECUTION_COMPLETED = "TOOL_EXECUTION_COMPLETED"
TOOL_RESULT_RETURNED = "TOOL_RESULT_RETURNED"
FINAL_RESPONSE_GENERATED = "FINAL_RESPONSE_GENERATED"
AGENT_COMPLETED = "AGENT_COMPLETED"
AGENT_FAILED = "AGENT_FAILED"

SUCCESS = "success"
FAILED = "failed"

_SENSITIVE_KEY = re.compile(r"(api[_-]?key|secret|token|password|authorization|credential)", re.I)
_KEY_VALUE = re.compile(r"(?:AIza[0-9A-Za-z_\-]{20,}|sk-[0-9A-Za-z_\-]{20,})")
_MAX_STRING = 2000
_MAX_DEPTH = 6


def sanitize(value: Any, depth: int = 0) -> Any:
    """Make trace details JSON-safe, truncated, and free of credentials."""
    if depth > _MAX_DEPTH:
        return "[truncated]"
    if isinstance(value, dict):
        return {
            str(k): "[redacted]" if _SENSITIVE_KEY.search(str(k)) else sanitize(v, depth + 1)
            for k, v in value.items()
        }
    if isinstance(value, (list, tuple, set)):
        return [sanitize(v, depth + 1) for v in list(value)[:50]]
    if isinstance(value, str):
        text = _KEY_VALUE.sub("[redacted]", value)
        return text if len(text) <= _MAX_STRING else text[:_MAX_STRING] + "…[truncated]"
    if value is None or isinstance(value, (bool, int, float)):
        return value
    return sanitize(str(value), depth + 1)


class TraceRecorder:
    def __init__(self, db: Session, run_id: int):
        self._db = db
        self._run_id = run_id
        self._seq = 0

    def record(
        self,
        event_type: str,
        title: str,
        details: dict[str, Any] | None = None,
        status: str = SUCCESS,
    ) -> ExecutionTrace:
        self._seq += 1
        event = ExecutionTrace(
            agent_run_id=self._run_id,
            sequence_number=self._seq,
            event_type=event_type,
            event_title=title,
            details=sanitize(details or {}),
            status=status,
            created_at=utcnow(),
        )
        self._db.add(event)
        self._db.commit()
        return event
