from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.repositories import run_repo, ticket_repo
from app.schemas.agent import RunOut
from app.schemas.ticket import TicketDetail, TicketSummary


def run_to_schema(run) -> RunOut:
    return RunOut.model_validate(
        {
            "id": run.id,
            "ticket_id": run.ticket_id,
            "status": run.status,
            "resolution_tag": run.resolution_tag,
            "customer_response": run.customer_response,
            "decision_summary": run.decision_summary,
            "tools_used": run_repo.parse_tools_used(run.tools_used),
            "model_name": run.model_name,
            "started_at": run.started_at,
            "completed_at": run.completed_at,
            "error_code": run.error_code,
            "error_message": run.error_message,
        }
    )


def list_tickets(db: Session) -> list[TicketSummary]:
    return [TicketSummary.model_validate(t) for t in ticket_repo.list_tickets(db)]


def get_ticket_detail(db: Session, ticket_id: str) -> TicketDetail:
    ticket = ticket_repo.get_ticket(db, ticket_id)
    if ticket is None:
        raise NotFoundError(f"Ticket {ticket_id} was not found.", details={"ticket_id": ticket_id})
    detail = TicketDetail.model_validate(ticket)
    latest = run_repo.latest_run(db, ticket_id)
    detail.latest_run = run_to_schema(latest) if latest else None
    return detail


def list_ticket_runs(db: Session, ticket_id: str) -> list[RunOut]:
    if ticket_repo.get_ticket(db, ticket_id) is None:
        raise NotFoundError(f"Ticket {ticket_id} was not found.", details={"ticket_id": ticket_id})
    return [run_to_schema(r) for r in run_repo.list_runs(db, ticket_id)]
