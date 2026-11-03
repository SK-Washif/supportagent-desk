from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import ExecutionTrace


def list_traces(db: Session, run_id: int) -> list[ExecutionTrace]:
    return list(
        db.scalars(
            select(ExecutionTrace)
            .where(ExecutionTrace.agent_run_id == run_id)
            .order_by(ExecutionTrace.sequence_number)
        )
    )
