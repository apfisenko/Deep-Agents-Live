"""Tests for PDF text extraction."""

from pathlib import Path
from unittest.mock import patch

import fitz
import pytest
from app.config import Settings
from app.rag.pdf_text import extract_pdf_text


@pytest.fixture
def pdf_settings() -> Settings:
    return Settings(
        env="test",
        openrouter_api_key="test-key",
        pdf_ocr_enabled=True,
        pdf_ocr_min_chars=10,
        pdf_ocr_llm_fallback=False,
    )


def test_extract_pdf_text_uses_text_layer(tmp_path: Path, pdf_settings: Settings) -> None:
    pdf_path = tmp_path / "sample.pdf"
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), "Corporate AI training for banks")
    doc.save(pdf_path)
    doc.close()

    text = extract_pdf_text(pdf_path, pdf_settings)
    assert "Corporate AI training" in text


def test_extract_pdf_text_uses_sidecar_override(tmp_path: Path, pdf_settings: Settings) -> None:
    pdf_path = tmp_path / "sample.pdf"
    pdf_path.write_bytes(b"%PDF-1.4\n")
    sidecar = pdf_path.with_suffix(".pdf.extracted.txt")
    sidecar.write_text("Sidecar extracted text about SILART RAG training", encoding="utf-8")

    text = extract_pdf_text(pdf_path, pdf_settings)
    assert "SILART RAG training" in text


def test_extract_pdf_text_runs_llm_fallback_for_image_page(
    tmp_path: Path,
    pdf_settings: Settings,
) -> None:
    pdf_settings = pdf_settings.model_copy(update={"pdf_ocr_llm_fallback": True})
    pdf_path = tmp_path / "image.pdf"
    doc = fitz.open()
    doc.new_page()
    doc.save(pdf_path)
    doc.close()
    ocr_text = "Живаго Банк AI-driven тренинг. " * 3

    with (
        patch("app.rag.pdf_text._ocr_page_tesseract", return_value=""),
        patch("app.rag.pdf_text._ocr_page_llm", return_value=ocr_text),
    ):
        text = extract_pdf_text(pdf_path, pdf_settings)

    assert "Живаго Банк" in text
