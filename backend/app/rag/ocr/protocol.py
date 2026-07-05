"""OCR engine protocol."""

from __future__ import annotations

from pathlib import Path
from typing import Protocol


class OcrEngine(Protocol):
    name: str

    def recognize(self, image_path: Path, *, preprocess: str = "dark_theme") -> str: ...
