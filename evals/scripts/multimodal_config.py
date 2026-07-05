"""YAML loader for multimodal eval configs (indexer + vector_db + RunConfig)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field

from app.agent.run_config import RunConfig
from app.env_resolver import resolve_env_placeholders


class IndexerSection(BaseModel):
    method: str
    corpus_dir: str
    options: dict[str, Any] = Field(default_factory=dict)


class VectorDbSection(BaseModel):
    collection: str
    embedding_model: str = "intfloat/multilingual-e5-large"
    chunk_size: int = 800
    chunk_overlap: int = 0
    top_k: int = 5
    langfuse_dataset: str | None = None


class MultimodalEvalConfig(RunConfig):
    indexer: IndexerSection
    vector_db: VectorDbSection

    @classmethod
    def from_yaml_path(cls, path: Path, *, resolve_env: bool = True) -> MultimodalEvalConfig:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(raw, dict):
            msg = f"Invalid YAML root in {path}"
            raise TypeError(msg)
        if resolve_env:
            raw = resolve_env_placeholders(raw)
        return cls.model_validate(raw)

    def resolve_corpus_dir(self, repo_root: Path) -> Path:
        corpus = Path(self.indexer.corpus_dir)
        if corpus.is_absolute():
            return corpus
        return (repo_root / corpus).resolve()
