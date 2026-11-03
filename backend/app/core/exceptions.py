"""Domain exceptions. Each maps to an HTTP status and a stable error code."""

from __future__ import annotations

from typing import Any


class AppError(Exception):
    status_code = 500
    code = "internal_error"
    public_message = "An unexpected error occurred."

    def __init__(self, message: str | None = None, *, details: dict[str, Any] | None = None):
        self.message = message or self.public_message
        self.details = details or {}
        super().__init__(self.message)


class NotFoundError(AppError):
    status_code = 404
    code = "not_found"
    public_message = "Resource not found."


class ConflictError(AppError):
    status_code = 409
    code = "conflict"
    public_message = "The request conflicts with the current state."


class ConfigurationError(AppError):
    status_code = 503
    code = "configuration_error"
    public_message = "The service is not configured correctly."


class RateLimitError(AppError):
    status_code = 429
    code = "llm_rate_limited"
    public_message = "The AI provider rate limit or quota was reached. Try again later."


class LLMProviderError(AppError):
    status_code = 502
    code = "llm_provider_error"
    public_message = "The AI provider request failed."


class InvalidLLMResponseError(AppError):
    status_code = 502
    code = "invalid_llm_response"
    public_message = "The AI provider returned a response that could not be validated."


class AgentLimitError(AppError):
    status_code = 422
    code = "agent_iteration_limit"
    public_message = "The agent did not finish within the allowed number of iterations."


class DatabaseFailure(AppError):
    status_code = 500
    code = "database_error"
    public_message = "A database error occurred."


class ToolError(Exception):
    """Raised inside tools. The message is safe to show and to feed to the LLM."""

    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message
        super().__init__(message)
