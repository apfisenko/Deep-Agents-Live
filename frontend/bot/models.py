"""API response models."""

from pydantic import BaseModel


class ChatResponse(BaseModel):
    session_id: str
    reply: str
    format: str
