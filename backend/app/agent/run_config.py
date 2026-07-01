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


class RetrieverHybridWeights(BaseModel):
    vector: float = 1.0
    graph: float = 1.2
    global_: float = Field(default=1.2, alias="global")

    model_config = {"populate_by_name": True}


class RetrieverSection(BaseModel):
    backend: Literal["vector", "graph", "global", "hybrid", "text2cypher"] = "vector"
    top_k: int = Field(default=5, ge=1, le=50)
    rrf_k: int = Field(default=60, ge=1)
    combo_slug: str = "ai-agents-combo"
    anchor_k: int = Field(default=8, ge=1, le=30)
    hybrid_weights: RetrieverHybridWeights = Field(default_factory=RetrieverHybridWeights)
    reranker_enabled: bool = True
    reranker_model: str = "BAAI/bge-reranker-v2-m3"
    reranker_candidate_k: int = Field(default=15, ge=1, le=100)
    reranker_timeout_sec: float = Field(default=8.0, gt=0)


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
    retriever: RetrieverSection = Field(default_factory=RetrieverSection)
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

    def to_metadata(self) -> dict[str, str]:
        """Langfuse propagated attributes must be strings."""
        return {
            "config_id": self.config_id,
            "model": self.model.name,
            "temperature": str(self.model.temperature),
            "benchmark_only": str(self.benchmark_only).lower(),
            "retriever_backend": self.retriever.backend,
        }

    def to_retriever_runtime(self) -> dict[str, Any]:
        weights = self.retriever.hybrid_weights
        return {
            "backend": self.retriever.backend,
            "top_k": self.retriever.top_k,
            "rrf_k": self.retriever.rrf_k,
            "rrf_weight_vector": weights.vector,
            "rrf_weight_graph": weights.graph,
            "rrf_weight_global": weights.global_,
            "reranker_enabled": self.retriever.reranker_enabled,
            "reranker_model": self.retriever.reranker_model,
            "reranker_candidate_k": self.retriever.reranker_candidate_k,
            "reranker_timeout_sec": self.retriever.reranker_timeout_sec,
            "graph_combo_slug": self.retriever.combo_slug,
            "graph_anchor_k": self.retriever.anchor_k,
        }
