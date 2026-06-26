"""Tests for markdown-aware chunking."""

from pathlib import Path

import pytest
from app.config import Settings
from app.rag.chunking import split_document_text


def test_split_markdown_by_headers_keeps_sections_together() -> None:
    settings = Settings(
        env="test",
        openrouter_api_key="test-key",
        chunk_markdown_by_headers=True,
    )
    settings = settings.model_copy(update={"chunk_size": 600, "chunk_overlap": 80})
    text = """# Program

## Format
Duration: 2 months
Schedule: twice per week

## Topics
Agents, RAG, observability
"""
    parts = split_document_text(text, Path("programs/sample.md"), settings)
    assert len(parts) == 2
    assert "Duration: 2 months" in parts[0]
    assert "Agents, RAG" in parts[1]


def test_split_markdown_splits_large_section_recursively(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("CHUNK_SIZE", "120")
    monkeypatch.setenv("CHUNK_OVERLAP", "20")
    settings = Settings(
        env="test",
        openrouter_api_key="test-key",
        chunk_markdown_by_headers=True,
    )
    text = "## Section\n" + ("word " * 80)
    parts = split_document_text(text, Path("programs/large.md"), settings)
    assert len(parts) >= 2
    assert all(len(part) <= 140 for part in parts)


def test_split_pdf_uses_recursive_only(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CHUNK_SIZE", "50")
    monkeypatch.setenv("CHUNK_OVERLAP", "10")
    settings = Settings(
        env="test",
        openrouter_api_key="test-key",
        chunk_markdown_by_headers=True,
    )
    text = "A" * 120
    parts = split_document_text(text, Path("cases/sample.pdf"), settings)
    assert len(parts) >= 2
