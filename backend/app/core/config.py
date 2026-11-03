"""Application configuration, validated once at startup.

A missing GROQ_API_KEY is deliberately *not* a startup error: the dashboard
and ticket APIs must keep working, and triage reports a clear config error.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parents[2]
PROJECT_ROOT = BACKEND_DIR.parent

SQLITE_PREFIX = "sqlite:///"
DEFAULT_MODEL = "openai/gpt-oss-120b"
DEFAULT_FALLBACK_MODEL = "openai/gpt-oss-20b"
DEFAULT_BASE_URL = "https://api.groq.com/openai/v1"


def resolve_database_url(url: str) -> str:
    if not url.startswith(SQLITE_PREFIX):
        raise ValueError("Only SQLite URLs (sqlite:///...) are supported.")
    raw = url[len(SQLITE_PREFIX):]
    if raw in ("", ":memory:"):
        return url
    path = Path(raw)
    if not path.is_absolute():
        path = BACKEND_DIR / path
    return f"{SQLITE_PREFIX}{path.resolve().as_posix()}"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(PROJECT_ROOT / ".env", BACKEND_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # Groq free tier (OpenAI-compatible). Any OpenAI-compatible endpoint works.
    groq_api_key: str = ""
    groq_model: str = DEFAULT_MODEL
    groq_fallback_model: str = DEFAULT_FALLBACK_MODEL
    groq_base_url: str = DEFAULT_BASE_URL
    groq_timeout_seconds: int = Field(default=60, ge=5, le=300)
    groq_reasoning_effort: str = "low"
    groq_max_output_tokens: int = Field(default=1500, ge=256, le=8000)

    database_url: str = "sqlite:///./supportagent.db"
    backend_host: str = "127.0.0.1"
    backend_port: int = Field(default=8000, ge=1, le=65535)
    frontend_url: str = "http://localhost:5173"
    max_agent_iterations: int = Field(default=5, ge=1, le=10)
    log_level: str = "INFO"

    @field_validator("database_url")
    @classmethod
    def _anchor_sqlite(cls, value: str) -> str:
        return resolve_database_url(value.strip())

    @field_validator(
        "groq_api_key", "groq_model", "groq_fallback_model",
        "groq_base_url", "groq_reasoning_effort", mode="before",
    )
    @classmethod
    def _strip(cls, value: object) -> object:
        return value.strip() if isinstance(value, str) else value

    @field_validator("groq_model")
    @classmethod
    def _model_not_blank(cls, value: str) -> str:
        return value or DEFAULT_MODEL

    @property
    def groq_configured(self) -> bool:
        return bool(self.groq_api_key)

    @property
    def cors_origins(self) -> list[str]:
        origins = {self.frontend_url.rstrip("/")}
        if "localhost" in self.frontend_url:
            origins.add(self.frontend_url.replace("localhost", "127.0.0.1").rstrip("/"))
        elif "127.0.0.1" in self.frontend_url:
            origins.add(self.frontend_url.replace("127.0.0.1", "localhost").rstrip("/"))
        return sorted(origins)


@lru_cache
def get_settings() -> Settings:
    return Settings()