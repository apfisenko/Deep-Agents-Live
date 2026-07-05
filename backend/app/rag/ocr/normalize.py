"""Text normalization for OCR CER metrics."""

from __future__ import annotations

import re
import unicodedata

_MULTI_SPACE_RE = re.compile(r"\s+")


def normalize_for_cer(text: str) -> str:
    normalized = unicodedata.normalize("NFKC", text)
    normalized = normalized.replace("\u200b", "").replace("\ufeff", "")
    normalized = _MULTI_SPACE_RE.sub(" ", normalized.strip().lower())
    return normalized
