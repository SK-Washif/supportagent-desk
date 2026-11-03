from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.agent import RunOut
from app.schemas.common import ApiResponse
from app.schemas.ticket import TicketDetail, TicketSummary
from app.services import ticket_service

router = APIRouter(prefix="/tickets", tags=["tickets"])


@router.get("", response_model=ApiResponse[list[TicketSummary]])
def list_tickets(db: Session = Depends(get_db)):
    return ApiResponse(data=ticket_service.list_tickets(db))


@router.get("/{ticket_id}", response_model=ApiResponse[TicketDetail])
def get_ticket(ticket_id: str, db: Session = Depends(get_db)):
    return ApiResponse(data=ticket_service.get_ticket_detail(db, ticket_id))


@router.get("/{ticket_id}/runs", response_model=ApiResponse[list[RunOut]])
def list_ticket_runs(ticket_id: str, db: Session = Depends(get_db)):
    """Run history for one ticket, newest first."""
    return ApiResponse(data=ticket_service.list_ticket_runs(db, ticket_id))
