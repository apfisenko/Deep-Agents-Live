"""Simple structured feedback (S2)."""

from __future__ import annotations

from pydantic import BaseModel, Field


class FeedbackIssue(BaseModel):
    text: str = Field(min_length=1)
    criterion_id: str | None = None


class SimpleFeedback(BaseModel):
    strengths: list[str] = Field(default_factory=list)
    issues: list[FeedbackIssue] = Field(default_factory=list)
    next_step: str = Field(min_length=1)
