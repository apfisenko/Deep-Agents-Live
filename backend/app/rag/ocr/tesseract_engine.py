"""Tesseract OCR engine for PNG slides."""

from __future__ import annotations

from pathlib import Path

import pytesseract

from app.rag.ocr.preprocess import load_preprocessed_image


class TesseractEngine:
    name = "tesseract"

    def __init__(self, *, languages: str = "rus+eng") -> None:
        self.languages = languages

    def recognize(self, image_path: Path, *, preprocess: str = "dark_theme") -> str:
        image = load_preprocessed_image(image_path, profile=preprocess)
        return pytesseract.image_to_string(image, lang=self.languages).strip()
