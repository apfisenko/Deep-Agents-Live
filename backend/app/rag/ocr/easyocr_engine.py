"""EasyOCR engine (CPU, Russian + English)."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import easyocr
import numpy as np

from app.rag.ocr.preprocess import load_preprocessed_image


@lru_cache(maxsize=1)
def _reader(languages: tuple[str, ...]) -> easyocr.Reader:
    return easyocr.Reader(list(languages), gpu=False)


class EasyOcrEngine:
    name = "modern"

    def __init__(self, *, languages: tuple[str, ...] = ("ru", "en")) -> None:
        self.languages = languages

    def recognize(self, image_path: Path, *, preprocess: str = "dark_theme") -> str:
        image = load_preprocessed_image(image_path, profile=preprocess)
        reader = _reader(self.languages)
        lines = reader.readtext(np.array(image), detail=0, paragraph=True)
        if isinstance(lines, str):
            return lines.strip()
        return "\n".join(str(line).strip() for line in lines if str(line).strip())
