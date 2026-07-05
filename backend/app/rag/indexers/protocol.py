"""Indexer protocol for multimodal RAG eval pipelines."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any, Protocol

from app.rag.indexers.cost import IndexCost


class Indexer(Protocol):
    method: str

    def build_index(
        self,
        *,
        corpus_dir: Path,
        collection: str,
        force: bool = False,
        options: Mapping[str, Any] | None = None,
    ) -> IndexCost: ...
