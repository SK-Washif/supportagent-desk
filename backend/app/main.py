from __future__ import annotations

import logging
from collections.abc import Callable
from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.agents.factory import make_groq_provider_factory
from app.agents.types import LLMProvider
from app.api.errors import register_exception_handlers
from app.api.routes import agent, health, tickets
from app.core.config import Settings, get_settings
from app.core.logging import configure_logging
from app.database.seed import seed_database
from app.database.session import build_engine, build_session_factory, init_db
from app.repositories.run_repo import recover_interrupted_runs

logger = logging.getLogger(__name__)


def create_app(
    settings: Settings | None = None,
    provider_factory: Callable[[], LLMProvider] | None = None,
) -> FastAPI:
    settings = settings or get_settings()
    configure_logging(settings.log_level)

    engine = build_engine(settings.database_url)
    init_db(engine)
    session_factory = build_session_factory(engine)
    with session_factory() as db:
        seed_database(db)
        recovered = recover_interrupted_runs(db)
        if recovered:
            logger.warning("Marked %s interrupted run(s) as failed", recovered)

    if not settings.groq_configured:
        logger.warning(
            "GROQ_API_KEY is not set: tickets work, AI triage will return a config error."
        )

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        yield
        engine.dispose()

    app = FastAPI(
        title="SupportAgent Desk API",
        version="1.0.0",
        description="AI-powered support triage with Groq LLM function calling and execution traces.",
        lifespan=lifespan,
    )
    app.state.settings = settings
    app.state.engine = engine
    app.state.session_factory = session_factory
    app.state.provider_factory = provider_factory or make_groq_provider_factory(settings)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["*"],
    )
    register_exception_handlers(app)

    api = APIRouter(prefix="/api")
    api.include_router(health.router)
    api.include_router(tickets.router)
    api.include_router(agent.router)
    app.include_router(api)
    return app
