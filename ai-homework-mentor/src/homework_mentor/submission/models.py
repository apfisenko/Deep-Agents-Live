"""Submission domain models."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field


class SourceType(StrEnum):
    LOCAL_PATH = "local_path"
    GITHUB_URL = "github_url"
    UNKNOWN = "unknown"


class Submission(BaseModel):
    """Structured parse of a user homework submission input."""

    source_type: SourceType
    source_value: str | None = None
    topic: str | None = None
    raw_text: str = ""
    needs_clarification: bool = False
    clarification_question: str | None = None


class TopicExtraction(BaseModel):
    """SGR schema: extract topic only; never invent."""

    reasoning: str = Field(
        description="Brief note on whether an explicit topic is present in the text",
    )
    observed_topic: str | None = Field(
        default=None,
        description="Assignment topic if explicitly stated; otherwise null",
    )
    confidence: str = Field(
        description="high if explicit topic; low if weak hint; none if absent",
    )
