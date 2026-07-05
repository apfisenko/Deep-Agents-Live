"""Tests for TEDS table structure metric."""

from __future__ import annotations

from app.rag.ingestion.teds import ocr_text_to_table_html, teds_score


def test_teds_identical_html_scores_one() -> None:
    html = "<table><tr><td>A</td><td>49%</td></tr></table>"
    assert teds_score(html, html) == 1.0


def test_ocr_text_to_table_html_parses_percent_rows() -> None:
    text = "Поддержка клиентов — 49%\nОперации — 47%"
    html = ocr_text_to_table_html(text)
    assert "<table>" in html
    assert "49%" in html
    assert "47%" in html
