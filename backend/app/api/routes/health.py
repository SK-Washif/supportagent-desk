from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.deps import get_app_settings, get_db
from app.core.config import Settings
from app.schemas.common import ApiResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=ApiResponse[dict])
def health(db: Session = Depends(get_db), settings: Settings = Depends(get_app_settings)):
    db.execute(text("SELECT 1"))
    return ApiResponse(
        data={
            "status": "ok",
            "database": "ok",
            "llm_provider": "Groq",
            "llm_configured": settings.groq_configured,
            "llm_model": settings.groq_model,
            "llm_fallback_model": settings.groq_fallback_model or None,
            "max_agent_iterations": settings.max_agent_iterations,
        }
    )


@router.post("/health/llm", response_model=ApiResponse[dict])
def check_llm(request: Request):
    """Verify key + model without spending tokens (list-models call)."""
    import httpx
    from app.core.exceptions import ConfigurationError, LLMProviderError

    settings = request.app.state.settings
    if not settings.groq_configured:
        raise ConfigurationError(
            "GROQ_API_KEY is not set. Create one at https://console.groq.com/keys"
        )
    try:
        resp = httpx.get(
            f"{settings.groq_base_url.rstrip('/')}/models",
            headers={"Authorization": f"Bearer {settings.groq_api_key}"},
            timeout=15,
        )
    except httpx.HTTPError as exc:
        raise LLMProviderError("Could not reach the Groq API.") from exc
    if resp.status_code in (401, 403):
        raise ConfigurationError("Groq rejected the API key.")
    if resp.status_code >= 400:
        raise LLMProviderError(f"Groq returned HTTP {resp.status_code}")
    available = [m["id"] for m in resp.json().get("data", [])]
    return ApiResponse(
        data={
            "key_valid": True,
            "models": {
                settings.groq_model: settings.groq_model in available,
                settings.groq_fallback_model: settings.groq_fallback_model in available,
            },
            "available_models": sorted(available)[:50],
        }
    )