"""Indexer registry and factory for multimodal eval configs."""

from __future__ import annotations

import importlib

from app.rag.indexers.protocol import Indexer
from app.rag.indexers.stub import StubIndexer

INDEXER_REGISTRY: dict[str, str] = {
    "baseline": "app.rag.indexers.baseline:BaselineTextIndexer",
    "A_ocr_tesseract": "app.rag.indexers.a_ocr_tesseract:TesseractOcrIndexer",
    "A_ocr_modern": "app.rag.indexers.a_ocr_modern:ModernOcrIndexer",
    "B_caption": "stub:05",
    "C_unified": "stub:06",
    "D_jina_multivector": "stub:07",
}


def make_indexer(method: str) -> Indexer:
    entry = INDEXER_REGISTRY.get(method)
    if entry is None:
        known = ", ".join(sorted(INDEXER_REGISTRY))
        msg = f"Unknown indexer method {method!r}. Known: {known}"
        raise ValueError(msg)
    if entry.startswith("stub:"):
        return StubIndexer(method)
    module_path, class_name = entry.split(":", maxsplit=1)
    module = importlib.import_module(module_path)
    indexer_cls = getattr(module, class_name)
    return indexer_cls()
