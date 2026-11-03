"""Groq adapter using the OpenAI-compatible chat completions API.

Groq's free tier is generous and requires no credit card. We use automatic
tool calling via the standard OpenAI function-calling protocol, but execute
tools ourselves so every call is validated, scoped, and traced.
"""

from __future__ import annotations

import json
import logging
from typing import Any

import httpx

from app.agents.types import LLMTurn, Message, ToolCall
from app.core.exceptions import (
    ConfigurationError,
    InvalidLLMResponseError,
    LLMProviderError,
    RateLimitError,
)
from app.tools.registry import ToolDeclaration

logger = logging.getLogger(__name__)


class GroqProvider:
    def __init__(
        self,
        *,
        api_key: str,
        model: str,
        fallback_model: str | None = None,
        base_url: str = "https://api.groq.com/openai/v1",
        timeout_seconds: int = 60,
        reasoning_effort: str = "low",
        max_output_tokens: int = 1500,
        client: Any | None = None,
    ):
        self.model_name = model
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout_seconds
        self._reasoning_effort = reasoning_effort
        self._max_tokens = max_output_tokens
        self._fallback = fallback_model or None
        self._client = client

    # ---- request -------------------------------------------------------------------------
    def generate(
        self,
        *,
        system_instruction: str,
        messages: list[Message],
        tools: list[ToolDeclaration],
    ) -> LLMTurn:
        payload = {
            "model": self.model_name,
            "messages": self._to_openai_messages(system_instruction, messages),
            "temperature": 0.2,
            "max_tokens": self._max_tokens,
        }
        if self._reasoning_effort and self.model_name.startswith("openai/"):
            payload["reasoning_effort"] = self._reasoning_effort
        if tools:
            payload["tools"] = [
                {
                    "type": "function",
                    "function": {
                        "name": t.name,
                        "description": t.description,
                        "parameters": t.parameters_schema,
                    },
                }
                for t in tools
            ]
            payload["tool_choice"] = "auto"

        try:
            data = self._post_completion(payload, self.model_name)
            return self._parse_response(data, model=self.model_name)
        except RateLimitError:
            if self._fallback and self._fallback != self.model_name:
                logger.warning(
                    "Primary model %s rate limited; falling back to %s",
                    self.model_name,
                    self._fallback,
                )
                payload["model"] = self._fallback
                try:
                    data = self._post_completion(payload, self._fallback)
                    return self._parse_response(data, model=self._fallback)
                except Exception as exc:
                    logger.exception("Fallback model also failed")
                    raise LLMProviderError(
                        f"Both {self.model_name} and {self._fallback} failed. "
                        "Check your Groq rate limits at https://console.groq.com/settings/limits"
                    ) from exc
            raise

    def _post_completion(self, payload: dict, model: str) -> dict:
        try:
            if self._client is not None:
                resp = self._client.post(payload)
            else:
                resp = httpx.post(
                    f"{self._base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self._api_key}",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                    timeout=self._timeout,
                )
        except httpx.HTTPError as exc:
            logger.exception("Groq HTTP request failed")
            raise LLMProviderError("Could not reach the Groq API.") from exc

        if resp.status_code == 429:
            raise RateLimitError()
        if resp.status_code in (401, 403):
            raise ConfigurationError(
                f"Groq rejected the API key (HTTP {resp.status_code}). "
                "Check GROQ_API_KEY in backend/.env — get a new key at https://console.groq.com/keys"
            )
        if resp.status_code == 404:
            raise ConfigurationError(
                f"Model '{model}' not found. Check GROQ_MODEL in backend/.env — "
                "list available models at https://console.groq.com/docs/models"
            )
        if resp.status_code >= 400:
            detail = ""
            try:
                detail = resp.json().get("error", {}).get("message", "")[:200]
            except Exception:
                pass
            raise LLMProviderError(f"Groq request failed (HTTP {resp.status_code}) {detail}".strip())

        return resp.json()

    @staticmethod
    def _to_openai_messages(system_instruction: str, messages: list[Message]) -> list[dict]:
        out: list[dict[str, Any]] = [{"role": "system", "content": system_instruction}]
        for m in messages:
            if m.role == "tool":
                for r in m.tool_results:
                    out.append(
                        {
                            "role": "tool",
                            "tool_call_id": r.call_id or "call_0",
                            "content": json.dumps(r.response),
                        }
                    )
                continue
            if m.role == "assistant" and m.tool_calls:
                out.append(
                    {
                        "role": "assistant",
                        "content": m.text or None,
                        "tool_calls": [
                            {
                                "id": c.id or f"call_{i}",
                                "type": "function",
                                "function": {
                                    "name": c.name,
                                    "arguments": json.dumps(c.args or {}),
                                },
                            }
                            for i, c in enumerate(m.tool_calls)
                        ],
                    }
                )
                continue
            out.append({"role": m.role, "content": m.text})
        return out

    @staticmethod
    def _parse_response(data: dict, model: str) -> LLMTurn:
        choices = data.get("choices") or []
        if not choices:
            raise InvalidLLMResponseError("Groq returned no choices.")
        msg = choices[0].get("message") or {}
        text = (msg.get("content") or "").strip()
        raw_calls = msg.get("tool_calls") or []
        calls: list[ToolCall] = []
        for raw in raw_calls:
            fn = raw.get("function") or {}
            args_raw = fn.get("arguments") or "{}"
            try:
                args = json.loads(args_raw) if isinstance(args_raw, str) else args_raw
            except ValueError:
                args = {}
            calls.append(ToolCall(id=raw.get("id"), name=fn.get("name") or "", args=args))
        return LLMTurn(
            text=text,
            tool_calls=calls,
            message=Message(role="assistant", text=text, tool_calls=calls),
            model=model,
        )