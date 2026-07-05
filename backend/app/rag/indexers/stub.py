"""Placeholder indexers for sprint-07 methods A–D (tasks 04–07)."""

from __future__ import annotations

from pathlib import Path

from app.rag.indexers.cost import IndexCost

_STUB_TASKS: dict[str, str] = {
    "A_ocr_tesseract": "04",
    "A_ocr_modern": "04",
    "B_caption": "05",
    "C_unified": "06",
    "D_jina_multivector": "07",
}


class StubIndexer:
    def __init__(self, method: str) -> None:
        self.method = method

    def build_index(
        self,
        *,
        corpus_dir: Path,
        collection: str,
        force: bool = False,
        options: object = None,
    ) -> IndexCost:
        task = _STUB_TASKS.get(self.method, "??")
        msg = (
            f"Indexer {self.method!r} is not implemented yet "
            f"(sprint-07 task {task}). corpus_dir={corpus_dir}, collection={collection}"
        )
        raise NotImplementedError(msg)
