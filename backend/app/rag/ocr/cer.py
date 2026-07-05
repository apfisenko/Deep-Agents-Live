"""Character Error Rate for OCR quality diagnostics."""

from __future__ import annotations

from rapidfuzz.distance import Levenshtein

from app.rag.ocr.normalize import normalize_for_cer


def cer(reference: str, hypothesis: str) -> float:
    ref = normalize_for_cer(reference)
    hyp = normalize_for_cer(hypothesis)
    if not ref:
        return float("inf") if hyp else 0.0
    return Levenshtein.distance(ref, hyp) / len(ref)
