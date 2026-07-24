"""Pydantic models for context metric events."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel, Field

ContextMetricSource = Literal["model_usage", "estimate"]
ContextEventType = Literal["none", "summarize", "compact", "offload"]


class ContextMetricEvent(BaseModel):
    """One context size observation for a review step."""

    step: int = Field(ge=0)
    tokens_before: int = Field(ge=0)
    tokens_after: int = Field(ge=0)
    source: ContextMetricSource
    event_type: ContextEventType = "none"
    timestamp: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))
    offload_path: str | None = None

    @property
    def delta(self) -> int:
        return self.tokens_after - self.tokens_before
