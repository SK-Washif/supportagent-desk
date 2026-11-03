from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.models import Ticket


def list_tickets(db: Session) -> list[Ticket]:
    return list(
        db.scalars(
            select(Ticket)
            .options(joinedload(Ticket.customer))
            .order_by(Ticket.ticket_id)
        )
    )


def get_ticket(db: Session, ticket_id: str) -> Ticket | None:
    return db.scalar(
        select(Ticket)
        .where(Ticket.ticket_id == ticket_id)
        .options(joinedload(Ticket.customer), joinedload(Ticket.order))
    )


def count_by_status(db: Session) -> dict[str, int]:
    rows = db.execute(select(Ticket.status, func.count()).group_by(Ticket.status)).all()
    return {status: count for status, count in rows}