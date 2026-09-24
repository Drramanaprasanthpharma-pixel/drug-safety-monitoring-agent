"""
Provider-agnostic AI client (spec section 3).

Configured entirely via environment variables — never hard-coded, never
sent to the frontend (all calls happen server-side, spec section 17):

    AI_PROVIDER=anthropic|openai   (see backend/.env.example; anthropic is the default)
    AI_API_KEY=<key>
    AI_MODEL=<model name>   (optional — a sensible default is used per provider)

If AI_PROVIDER/AI_API_KEY are unset, `AIClient.configured()` is False and
`generate_json` raises AIUnavailable immediately, without making a network
call. Callers (drug_agent.py) treat AIUnavailable the same way as any other
provider failure: fall back to "the local database and safety engine still
work; this specific unknown drug could not be retrieved" (spec section 18).
This code path is exercised by tests/test_agent.py; the live HTTP calls to
each provider are implemented but require a real API key to exercise
end-to-end, which is outside what this environment can verify (see the
project README's testing notes).
"""
from __future__ import annotations
import os
from typing import Optional

import httpx

DEFAULT_MODELS = {
    "anthropic": "claude-sonnet-4-5",
    "openai": "gpt-4o-mini",
}

REQUEST_TIMEOUT_SECONDS = 25.0
MAX_TOKENS = 2000


class AIUnavailable(Exception):
    """Raised whenever the AI provider cannot be used right now: not
    configured, network/timeout failure, or a non-2xx response. Never
    raised for 'the AI responded but the content didn't validate' — that
    is a validation failure, handled separately in drug_agent.py, so the
    two failure modes (section 18: unavailable vs. section 7: invalid
    response) can be reported and tested distinctly."""


class AIClient:
    def __init__(self) -> None:
        self.provider = (os.environ.get("AI_PROVIDER") or "").strip().lower()
        self.api_key = (os.environ.get("AI_API_KEY") or "").strip()
        self.model = (os.environ.get("AI_MODEL") or "").strip() or DEFAULT_MODELS.get(self.provider, "")

    def configured(self) -> bool:
        return bool(self.provider and self.api_key)

    def generate_json(self, system: str, user: str) -> str:
        """Returns the raw text response from the configured provider.
        Callers are responsible for JSON-parsing and schema validation —
        this function's only job is getting text back from *a* provider
        without the rest of the app needing to know which one."""
        if not self.configured():
            raise AIUnavailable(
                "No AI provider configured (set AI_PROVIDER and AI_API_KEY to enable AI-assisted drug retrieval)."
            )
        try:
            if self.provider == "anthropic":
                return self._call_anthropic(system, user)
            if self.provider == "openai":
                return self._call_openai(system, user)
        except httpx.TimeoutException as e:
            raise AIUnavailable(f"AI provider request timed out: {e}") from e
        except httpx.HTTPError as e:
            raise AIUnavailable(f"AI provider request failed: {e}") from e
        raise AIUnavailable(f"Unsupported AI_PROVIDER '{self.provider}' (expected anthropic or openai).")

    def _call_anthropic(self, system: str, user: str) -> str:
        resp = httpx.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": self.model,
                "max_tokens": MAX_TOKENS,
                "system": system,
                "messages": [{"role": "user", "content": user}],
            },
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        resp.raise_for_status()
        data = resp.json()
        return "".join(b.get("text", "") for b in data.get("content", []) if b.get("type") == "text")

    def _call_openai(self, system: str, user: str) -> str:
        resp = httpx.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {self.api_key}", "content-type": "application/json"},
            json={
                "model": self.model,
                "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
                "response_format": {"type": "json_object"},
                "temperature": 0,
                "max_tokens": MAX_TOKENS,
            },
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]



def get_client() -> AIClient:
    """Fresh instance per call so tests can monkeypatch os.environ without
    caching stale configuration across calls."""
    return AIClient()
