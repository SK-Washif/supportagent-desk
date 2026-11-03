from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.api.deps import get_app_settings, get_db
from app.core.config import Settings
from app.schemas.agent import RunOut, TraceOut
from app.schemas.common import ApiResponse
from app.services import agent_service

router = APIRouter(prefix="/agent", tags=["agent"])


@router.post("/triage/{ticket_id}", response_model=ApiResponse[dict])
def run_triage(
    ticket_id: str,
    request: Request,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_app_settings),
):
    run, traces = agent_service.run_triage(
        db, settings, request.app.state.provider_factory, ticket_id
    )
    return ApiResponse(
        data={
            "run": run.model_dump(mode="json"),
            "traces": [t.model_dump(mode="json") for t in traces],
        }
    )


@router.get("/runs", response_model=ApiResponse[list[RunOut]])
def list_runs(db: Session = Depends(get_db)):
    return ApiResponse(data=agent_service.list_runs(db))


@router.get("/runs/{run_id}", response_model=ApiResponse[RunOut])
def get_run(run_id: int, db: Session = Depends(get_db)):
    return ApiResponse(data=agent_service.get_run(db, run_id))


@router.get("/runs/{run_id}/traces", response_model=ApiResponse[list[TraceOut]])
def get_traces(run_id: int, db: Session = Depends(get_db)):
    return ApiResponse(data=agent_service.get_traces(db, run_id))
