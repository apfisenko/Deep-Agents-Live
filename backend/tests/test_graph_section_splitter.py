"""Tests for program section splitter."""

from __future__ import annotations

import asyncio

from app.graph.section_splitter import ProgramSectionSplitter


def test_program_section_splitter_splits_tema_headers() -> None:
    text = """
## Программа
### Тема 1. Intro
Line one
### Тема 2. RAG basics
Line two
"""
    splitter = ProgramSectionSplitter()
    chunks = asyncio.run(splitter.run(text))
    assert len(chunks.chunks) == 2
    assert chunks.chunks[0].metadata["moduleNumber"] == 1
    assert chunks.chunks[1].metadata["moduleNumber"] == 2
    assert "RAG" in chunks.chunks[1].text
