from __future__ import annotations

import threading
from collections.abc import Callable

from app.agents.groq_provider import GroqProvider
from app.agents.types import LLMProvider
from app.core.config import Settings
from app.core.exceptions import ConfigurationError


def make_groq_provider_factory(settings: Settings) -> Callable[[], LLMProvider]:
    """Lazy, cached provider. Raises ConfigurationError if no Groq key is set."""
    lock = threading.Lock()
    cache: dict[str, LLMProvider] = {}

    def factory() -> LLMProvider:
        if not settings.groq_configured:
            raise ConfigurationError(
                "GROQ_API_KEY is not configured. Create a free key at "
                "https://console.groq.com/keys, add it to backend/.env (see .env.example) "
                "and restart the backend. Tickets remain viewable without it."
            )
        with lock:
            if "p" not in cache:
                cache["p"] = GroqProvider(
                    api_key=settings.groq_api_key,
                    model=settings.groq_model,
                    fallback_model=settings.groq_fallback_model or None,
                    base_url=settings.groq_base_url,
                    timeout_seconds=settings.groq_timeout_seconds,
                    reasoning_effort=settings.groq_reasoning_effort,
                    max_output_tokens=settings.groq_max_output_tokens,
                )
            return cache["p"]

    return factory