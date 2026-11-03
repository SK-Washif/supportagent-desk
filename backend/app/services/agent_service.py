"""Orchestrates one triage execution: lock -> run agent -> persist -> release."""

from __future__ import annotations

import logging
from collections.abc import Callable

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.agents import trace as ev
from app.agents.trace import TraceRecorder
from app.agents.triage_agent import TriageAgent
from app.agents.types import LLMProvider
from app.core.config import Settings
from app.core.exceptions import AppError, DatabaseFailure, NotFoundError
from app.repositories import run_repo, ticket_repo, trace_repo
from app.schemas.agent import RunOut, TraceOut
from app.services.ticket_service import run_to_schema

logger = logging.getLogger(__name__)

ProviderFactory = Callable[[], LLMProvider]


class AgentExecutionError(AppError):
    code = "agent_failed"
    public_message = "The agent failed unexpectedly. See server logs for details."


def run_triage(
    db: Session, settings: Settings, provider_factory: ProviderFactory, ticket_id: str
) -> tuple[RunOut, list[TraceOut]]:
    ticket = ticket_repo.get_ticket(db, ticket_id)
    if ticket is None:
        raise NotFoundError(f"Ticket {ticket_id} was not found.", details={"ticket_id": ticket_id})

    # Configuration problems are reported before anything is touched: no run, no status change.
    provider = provider_factory()

    run = run_repo.acquire_run(db, ticket_id, provider.model_name)  # atomic; raises 409
    recorder = TraceRecorder(db, run.id)
    run_id = run.id

    try:
        agent = TriageAgent(
            provider=provider,
            db=db,
            recorder=recorder,
            max_iterations=settings.max_agent_iterations,
        )
        result = agent.run(ticket)
        run_repo.complete_run(
            db,
            run,
            resolution_tag=result.resolution_tag,
            customer_response=result.customer_response,
            decision_summary=result.decision_summary,
            tools_used=result.tools_used,
        )
    except Exception as exc:
        error = _to_app_error(exc)
        _record_failure(db, recorder, run_id, error)
        error.details = {**error.details, "run_id": run_id, "ticket_id": ticket_id}
        raise error from exc

    try:
        recorder.record(
            ev.AGENT_COMPLETED,
            "Agent completed",
            {"ticket_id": ticket_id, "ticket_status": "Resolved", "tools_used": result.tools_used},
        )
    except SQLAlchemyError:  # the run is already durably complete; don't turn it into a failure
        logger.exception("Could not record AGENT_COMPLETED for run %s", run_id)

    return get_run_with_traces(db, run_id)


def _to_app_error(exc: Exception) -> AppError:
    if isinstance(exc, AppError):
        return exc
    if isinstance(exc, SQLAlchemyError):
        logger.exception("Database failure during triage")
        return DatabaseFailure()
    logger.exception("Unexpected agent failure")
    return AgentExecutionError()


def _record_failure(db: Session, recorder: TraceRecorder, run_id: int, error: AppError) -> None:
    """Trace the failure, then mark the run failed and restore the ticket (best effort)."""
    try:
        db.rollback()
        recorder.record(
            ev.AGENT_FAILED,
            "Agent failed",
            {"error_code": error.code, "error_message": error.message},
            status=ev.FAILED,
        )
    except Exception:
        logger.exception("Could not record AGENT_FAILED trace for run %s", run_id)
        db.rollback()
    try:
        run_repo.fail_run(db, run_id, error_code=error.code, error_message=error.message)
    except Exception:
        logger.exception("Could not mark run %s as failed", run_id)


def get_run_with_traces(db: Session, run_id: int) -> tuple[RunOut, list[TraceOut]]:
    run = run_repo.get_run(db, run_id)
    if run is None:
        raise NotFoundError(f"Run {run_id} was not found.", details={"run_id": run_id})
    traces = [TraceOut.model_validate(t) for t in trace_repo.list_traces(db, run_id)]
    return run_to_schema(run), traces


def get_run(db: Session, run_id: int) -> RunOut:
    run = run_repo.get_run(db, run_id)
    if run is None:
        raise NotFoundError(f"Run {run_id} was not found.", details={"run_id": run_id})
    return run_to_schema(run)


def get_traces(db: Session, run_id: int) -> list[TraceOut]:
    if run_repo.get_run(db, run_id) is None:
        raise NotFoundError(f"Run {run_id} was not found.", details={"run_id": run_id})
    return [TraceOut.model_validate(t) for t in trace_repo.list_traces(db, run_id)]


def list_runs(db: Session, limit: int = 100) -> list[RunOut]:
    return [run_to_schema(r) for r in run_repo.list_runs(db, limit=limit)]
