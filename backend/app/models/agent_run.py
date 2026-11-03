from __future__ import annotations

from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.time import utcnow
from app.database.base import Base

RUN_RUNNING = "running"
RUN_COMPLETED = "completed"
RUN_FAILED = "failed"

AUTO_RESOLVE = "Auto-Resolve"
ESCALATE_TO_SALES = "Escalate to Sales"


class AgentRun(Base):
    """One agent execution. Every triage creates a new row; history is never overwritten."""

    __tablename__ = "agent_runs"

    id: Mapped[int] = mapped_column(primary_key=True)
    ticket_id: Mapped[str] = mapped_column(
        ForeignKey("tickets.ticket_id", ondelete="CASCADE"), index=True
    )
    status: Mapped[str] = mapped_column(String(16), default=RUN_RUNNING)
    resolution_tag: Mapped[str | None] = mapped_column(String(32), nullable=True)
    customer_response: Mapped[str | None] = mapped_column(Text, nullable=True)
    decision_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    tools_used: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON list
    model_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    error_code: Mapped[str | None] = mapped_column(String(64), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    ticket: Mapped[Ticket] = relationship(back_populates="runs")
    traces: Mapped[list[ExecutionTrace]] = relationship(
        back_populates="run",
        order_by="ExecutionTrace.sequence_number",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        CheckConstraint("status IN ('running','completed','failed')", name="ck_run_status"),
        # Database-level guard: at most ONE running run per ticket.
        Index(
            "uq_agent_runs_one_running_per_ticket",
            "ticket_id",
            unique=True,
            sqlite_where=text("status = 'running'"),
        ),
    )


from app.models.execution_trace import ExecutionTrace  # noqa: E402
from app.models.ticket import Ticket  # noqa: E402
