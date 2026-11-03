from __future__ import annotations

import json

from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError
from app.core.time import utcnow
from app.models import AgentRun, Ticket
from app.models.agent_run import RUN_COMPLETED, RUN_FAILED, RUN_RUNNING
from app.models.ticket import PENDING, PROCESSING, RESOLVED


def acquire_run(db: Session, ticket_id: str, model_name: str | None) -> AgentRun:
    """Atomically claim a ticket for triage, or raise ConflictError.

    Two independent database-level guards make duplicate runs impossible:
    1. A conditional UPDATE only flips the ticket to Processing if it is not
       already Processing (exactly one concurrent caller sees rowcount == 1).
    2. A partial unique index allows a single 'running' run per ticket.
    """
    now = utcnow()
    try:
        claimed = db.execute(
            update(Ticket)
            .where(Ticket.ticket_id == ticket_id, Ticket.status != PROCESSING)
            .values(status=PROCESSING, updated_at=now)
        )
        if claimed.rowcount != 1:
            db.rollback()
            raise ConflictError(
                f"Ticket {ticket_id} is already being processed.", details={"ticket_id": ticket_id}
            )
        run = AgentRun(
            ticket_id=ticket_id, status=RUN_RUNNING, started_at=now, model_name=model_name
        )
        db.add(run)
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ConflictError(
            f"Ticket {ticket_id} is already being processed.", details={"ticket_id": ticket_id}
        ) from exc
    return run


def complete_run(
    db: Session,
    run: AgentRun,
    *,
    resolution_tag: str,
    customer_response: str,
    decision_summary: str,
    tools_used: list[str],
) -> None:
    """Persist the successful result and resolve the ticket in one transaction."""
    now = utcnow()
    run.status = RUN_COMPLETED
    run.resolution_tag = resolution_tag
    run.customer_response = customer_response
    run.decision_summary = decision_summary
    run.tools_used = json.dumps(tools_used)
    run.completed_at = now
    db.execute(
        update(Ticket)
        .where(Ticket.ticket_id == run.ticket_id)
        .values(status=RESOLVED, updated_at=now)
    )
    db.commit()


def fail_run(db: Session, run_id: int, *, error_code: str, error_message: str) -> None:
    """Mark a run failed and restore the ticket status. Never marks the ticket Resolved
    because of this run; it returns to Resolved only if an earlier run really resolved it."""
    db.rollback()
    run = db.get(AgentRun, run_id)
    if run is None:
        return
    now = utcnow()
    run.status = RUN_FAILED
    run.error_code = error_code
    run.error_message = error_message[:1000]
    run.completed_at = now
    db.flush()
    previously_resolved = db.scalar(
        select(AgentRun.id)
        .where(
            AgentRun.ticket_id == run.ticket_id,
            AgentRun.status == RUN_COMPLETED,
            AgentRun.id != run.id,
        )
        .limit(1)
    )
    db.execute(
        update(Ticket)
        .where(Ticket.ticket_id == run.ticket_id)
        .values(status=RESOLVED if previously_resolved else PENDING, updated_at=now)
    )
    db.commit()


def recover_interrupted_runs(db: Session) -> int:
    """On startup, fail runs left 'running' by a crash/restart and release their tickets."""
    stale = list(db.scalars(select(AgentRun).where(AgentRun.status == RUN_RUNNING)))
    for run in stale:
        fail_run(
            db,
            run.id,
            error_code="interrupted",
            error_message="The run was interrupted by a server restart.",
        )
    return len(stale)


def get_run(db: Session, run_id: int) -> AgentRun | None:
    return db.get(AgentRun, run_id)


def list_runs(db: Session, ticket_id: str | None = None, limit: int = 100) -> list[AgentRun]:
    stmt = select(AgentRun).order_by(AgentRun.id.desc()).limit(limit)
    if ticket_id:
        stmt = stmt.where(AgentRun.ticket_id == ticket_id)
    return list(db.scalars(stmt))


def latest_run(db: Session, ticket_id: str) -> AgentRun | None:
    return db.scalar(
        select(AgentRun)
        .where(AgentRun.ticket_id == ticket_id)
        .order_by(AgentRun.id.desc())
        .limit(1)
    )


def parse_tools_used(raw: str | None) -> list[str]:
    if not raw:
        return []
    try:
        value = json.loads(raw)
    except ValueError:
        return []
    return [str(v) for v in value] if isinstance(value, list) else []
