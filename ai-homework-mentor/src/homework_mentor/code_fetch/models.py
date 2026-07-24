"""Shared models for code fetch (local / GitHub)."""

from __future__ import annotations

from pathlib import Path  # noqa: TC003 — required by Pydantic at runtime

from pydantic import BaseModel, Field


class CodeFetchError(RuntimeError):
    """Raised when student code cannot be staged."""


class FetchResult(BaseModel):
    """Result of staging student code without executing it."""

    staging_dir: Path
    source: str
    files: list[str] = Field(default_factory=list)

    @property
    def file_count(self) -> int:
        return len(self.files)
