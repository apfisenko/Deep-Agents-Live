"""OpenRouter model pricing helpers for caption cost estimation."""

from __future__ import annotations

# USD per token (OpenRouter catalog snapshot 2026-07-05).
_MODEL_PRICING: dict[str, tuple[float, float]] = {
    "nvidia/nemotron-nano-12b-v2-vl:free": (0.0, 0.0),
    "google/gemini-2.5-flash-lite": (1e-7, 4e-7),
    "google/gemini-2.5-flash": (3e-7, 2.5e-6),
}


def estimate_vlm_cost_usd(
    model_id: str,
    *,
    prompt_tokens: int,
    completion_tokens: int,
) -> float:
    prompt_rate, completion_rate = _MODEL_PRICING.get(model_id, (3e-7, 2.5e-6))
    return prompt_tokens * prompt_rate + completion_tokens * completion_rate
