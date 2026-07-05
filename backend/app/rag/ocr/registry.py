"""OCR engine registry."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from app.rag.ocr.protocol import OcrEngine

OCR_ENGINE_REGISTRY: dict[str, str] = {
    "tesseract": "tesseract",
    "modern": "modern",
}


def make_ocr_engine(name: str, options: Mapping[str, Any] | None = None) -> OcrEngine:
    opts = dict(options or {})
    if name == "tesseract":
        from app.rag.ocr.tesseract_engine import TesseractEngine

        return TesseractEngine(languages=str(opts.get("languages", "rus+eng")))
    if name == "modern":
        from app.rag.ocr.easyocr_engine import EasyOcrEngine

        langs = opts.get("modern_langs", ("ru", "en"))
        if isinstance(langs, list):
            langs = tuple(str(item) for item in langs)
        elif isinstance(langs, tuple):
            langs = tuple(str(item) for item in langs)
        else:
            langs = ("ru", "en")
        return EasyOcrEngine(languages=langs)
    known = ", ".join(sorted(OCR_ENGINE_REGISTRY))
    msg = f"Unknown OCR engine {name!r}. Known: {known}"
    raise ValueError(msg)
