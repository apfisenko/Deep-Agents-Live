"""Chat API schemas."""

from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class ChatRequest(BaseModel):
    session_id: UUID
    channel: Literal["web", "telegram"]
    message: str = Field(min_length=1, max_length=4000)
    metadata: dict[str, Any] | None = None

    @field_validator("message")
    @classmethod
    def strip_message(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            msg = "message must not be empty"
            raise ValueError(msg)
        return stripped


class ChatResponse(BaseModel):
    session_id: str
    reply: str
    format: Literal["markdown"] = "markdown"


class ReindexResponse(BaseModel):
    indexed: int
    skipped: int
    removed: int
