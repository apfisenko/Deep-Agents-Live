"""Pydantic models for eval run configurations (E-5)."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseModel, Field, model_validator

from app.env_resolver import resolve_env_placeholders


class AgentSection(BaseModel):
    impl: Literal["langchain-react"]
    api_url: str


class RetrievalSection(BaseModel):
    backend: Literal["in-memory", "chroma-embedded", "qdrant"]


class ModelSection(BaseModel):
    provider: Literal["openrouter"]
    name: str
    temperature: float = Field(ge=0.0, le=2.0)


class JudgeSection(BaseModel):
    provider: Literal["openrouter"]
    name: str
    temperature: float = Field(default=0.0, ge=0.0, le=2.0)


class PromptSection(BaseModel):
    source: Literal["file", "langfuse"]
    name: str
    path: str | None = None
    label: str | None = None

    @model_validator(mode="after")
    def validate_source_fields(self) -> PromptSection:
        if self.source == "file" and not self.path:
            msg = "prompt.path is required when source=file"
            raise ValueError(msg)
        if self.source == "langfuse" and not self.label:
            msg = "prompt.label is required when source=langfuse"
            raise ValueError(msg)
        return self


class RunConfig(BaseModel):
    config_id: str
    comment: str = ""
    benchmark_only: bool = False
    agent: AgentSection
    retrieval: RetrievalSection
    model: ModelSection
    judge: JudgeSection
    prompt: PromptSection
    datasets: dict[str, str] = Field(default_factory=dict)
    # metrics-guide §C: optional behavior-layer evaluators (e.g. executed_tools_count)
    extra_evaluators: list[str] = Field(default_factory=list)

    @classmethod
    def from_yaml_path(cls, path: Path, *, resolve_env: bool = True) -> RunConfig:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(raw, dict):
            msg = f"Invalid YAML root in {path}"
            raise TypeError(msg)
        if resolve_env:
            raw = resolve_env_placeholders(raw)
        return cls.model_validate(raw)

    def to_metadata(self) -> dict[str, Any]:
        return {
            "config_id": self.config_id,
            "model": self.model.name,
            "temperature": self.model.temperature,
            "benchmark_only": self.benchmark_only,
        }
