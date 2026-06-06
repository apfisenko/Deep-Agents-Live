"""Health endpoint schemas."""

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = Field(examples=["ok"])
    version: str = Field(examples=["0.1.0"])
    rag_indexed_docs: int = Field(ge=0, examples=[0])
    sessions_active: int = Field(ge=0, examples=[0])
