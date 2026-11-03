from __future__ import annotations

from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.time import utcnow
from app.database.base import Base

PENDING = "Pending"
PROCESSING = "Processing"
RESOLVED = "Resolved"
TICKET_STATUSES = (PENDING, PROCESSING, RESOLVED)


class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(primary_key=True)
    ticket_id: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    customer_id: Mapped[str] = mapped_column(
        ForeignKey("customers.customer_id", ondelete="RESTRICT"), index=True
    )
    order_id: Mapped[str | None] = mapped_column(
        ForeignKey("orders.order_id", ondelete="RESTRICT"), nullable=True
    )
    subject: Mapped[str] = mapped_column(String(200))
    message: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(16), default=PENDING, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, onupdate=utcnow)

    customer: Mapped[Customer] = relationship(back_populates="tickets")
    order: Mapped[Order | None] = relationship()
    runs: Mapped[list[AgentRun]] = relationship(
        back_populates="ticket", order_by="AgentRun.id", cascade="all, delete-orphan"
    )

    @property
    def customer_name(self) -> str:
        return self.customer.name

    __table_args__ = (
        CheckConstraint("status IN ('Pending','Processing','Resolved')", name="ck_ticket_status"),
        Index("ix_tickets_updated_at", "updated_at"),
    )


from app.models.agent_run import AgentRun  # noqa: E402
from app.models.customer import Customer  # noqa: E402
from app.models.order import Order  # noqa: E402