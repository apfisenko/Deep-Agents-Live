"""EasyOCR (modern) multimodal indexer."""

from __future__ import annotations

from app.rag.indexers.a_ocr_base import OcrTextIndexer


class ModernOcrIndexer(OcrTextIndexer):
    method = "A_ocr_modern"
    ocr_engine = "modern"
    artifact_prefix = "evals/artifacts/ocr/modern"
