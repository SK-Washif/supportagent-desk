from __future__ import annotations

from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.time import utcnow
from app.database.base import Base


class ExecutionTrace(Base):
    __tablename__ = "execution_traces"

    id: Mapped[int] = mapped_column(primary_key=True)
    agent_run_id: Mapped[int] = mapped_column(
        ForeignKey("agent_runs.id", ondelete="CASCADE"), index=True
    )
    sequence_number: Mapped[int] = mapped_column()
    event_type: Mapped[str] = mapped_column(String(48))
    event_title: Mapped[str] = mapped_column(String(200))
    details: Mapped[dict] = mapped_column(JSON, default=dict)
    status: Mapped[str] = mapped_column(String(16), default="success")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

    run: Mapped[AgentRun] = relationship(back_populates="traces")

    __table_args__ = (UniqueConstraint("agent_run_id", "sequence_number", name="uq_trace_seq"),)


from app.models.agent_run import AgentRun  # noqa: E402
