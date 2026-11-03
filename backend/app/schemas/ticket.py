from __future__ import annotations

from datetime import datetime

from app.schemas.agent import RunOut
from app.schemas.common import ApiModel


class CustomerOut(ApiModel):
    customer_id: str
    name: str
    email: str
    current_tier: str


class OrderOut(ApiModel):
    order_id: str
    customer_id: str
    status: str
    estimated_delivery: str


class TicketSummary(ApiModel):
    ticket_id: str
    customer_id: str
    customer_name: str
    order_id: str | None
    subject: str
    status: str
    created_at: datetime
    updated_at: datetime


class TicketDetail(TicketSummary):
    message: str
    customer: CustomerOut
    order: OrderOut | None
    latest_run: RunOut | None = None