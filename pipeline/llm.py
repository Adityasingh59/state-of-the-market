"""One place that calls Claude: structured JSON output + the spend cap."""

from __future__ import annotations

import json

import anthropic

from . import config
from .cost import CostTracker

_client: anthropic.Anthropic | None = None


def client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        # Reads ANTHROPIC_API_KEY (or an `ant auth login` profile). The SDK
        # retries 429 / 5xx / connection errors with backoff.
        _client = anthropic.Anthropic(max_retries=5, timeout=600)
    return _client


class ModelOutputError(RuntimeError):
    """The response could not be used (refusal, truncation, bad JSON)."""


def estimate_tokens(text: str) -> int:
    # Deliberately pessimistic (~3 chars per token) so the budget check
    # over-reserves rather than under-reserves.
    return len(text) // 3 + 50


def call_json(
    *,
    tracker: CostTracker,
    step: str,
    model: str,
    system: str,
    user: str,
    schema: dict,
    effort: str,
    max_tokens: int,
    note: str = "",
) -> dict:
    """Send one request whose answer must match `schema`; return the parsed JSON."""
    reservation = tracker.reserve(model, estimate_tokens(system + user), max_tokens)

    kwargs: dict = dict(
        model=model,
        max_tokens=max_tokens,
        # Stable system prompt first, cached across the many tagging calls.
        system=[{"type": "text", "text": system, "cache_control": {"type": "ephemeral"}}],
        messages=[{"role": "user", "content": user}],
        output_config={
            "effort": effort,
            "format": {"type": "json_schema", "schema": schema},
        },
    )
    if config.USE_FALLBACKS:
        kwargs["betas"] = [config.FALLBACK_BETA]
        kwargs["fallbacks"] = "default"

    try:
        response = client().beta.messages.create(**kwargs)
    except anthropic.APIError:
        tracker.release(reservation)
        raise

    tracker.settle(reservation, response, step=step, note=note)

    if response.stop_reason == "refusal":
        category = getattr(getattr(response, "stop_details", None), "category", None)
        raise ModelOutputError(f"refusal (category={category})")
    if response.stop_reason == "max_tokens":
        raise ModelOutputError("hit max_tokens; use a smaller batch")

    text = next((b.text for b in response.content if b.type == "text"), None)
    if text is None:
        raise ModelOutputError("no text block in response")
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        raise ModelOutputError(f"invalid JSON: {e}") from e
