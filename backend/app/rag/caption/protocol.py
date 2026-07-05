"""VLM caption engine protocol."""

from __future__ import annotations

from pathlib import Path
from typing import Protocol


class CaptionUsage:
    """Token usage from a single VLM call."""

    __slots__ = ("completion_tokens", "prompt_tokens", "total_tokens")

    def __init__(
        self,
        *,
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
        total_tokens: int = 0,
    ) -> None:
        self.prompt_tokens = prompt_tokens
        self.completion_tokens = completion_tokens
        self.total_tokens = total_tokens


class CaptionResult:
    """Caption text plus usage metadata."""

    __slots__ = ("est_cost_usd", "text", "usage")

    def __init__(
        self,
        *,
        text: str,
        usage: CaptionUsage | None = None,
        est_cost_usd: float = 0.0,
    ) -> None:
        self.text = text
        self.usage = usage or CaptionUsage()
        self.est_cost_usd = est_cost_usd


class VlmCaptioner(Protocol):
    model_id: str

    def caption_slide(
        self,
        image_path: Path,
        *,
        prompt: str | None = None,
        max_side: int = 1536,
    ) -> CaptionResult: ...
