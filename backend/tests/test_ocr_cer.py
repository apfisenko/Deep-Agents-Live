"""Unit tests for OCR CER normalization and formula."""

from __future__ import annotations

import math

from app.rag.ocr.cer import cer
from app.rag.ocr.normalize import normalize_for_cer


def test_normalize_for_cer_lowercase_and_spaces() -> None:
    assert normalize_for_cer("  Hello   World  ") == "hello world"


def test_cer_identical_zero() -> None:
    assert cer("Привет мир", "привет мир") == 0.0


def test_cer_can_exceed_one() -> None:
    value = cer("abc", "abcdefgh")
    assert value > 1.0


def test_cer_empty_reference_with_hypothesis() -> None:
    assert math.isinf(cer("", "text"))
