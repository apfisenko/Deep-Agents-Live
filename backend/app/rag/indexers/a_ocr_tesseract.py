"""Tesseract OCR multimodal indexer."""

from __future__ import annotations

from app.rag.indexers.a_ocr_base import OcrTextIndexer


class TesseractOcrIndexer(OcrTextIndexer):
    method = "A_ocr_tesseract"
    ocr_engine = "tesseract"
    artifact_prefix = "evals/artifacts/ocr/tesseract"
