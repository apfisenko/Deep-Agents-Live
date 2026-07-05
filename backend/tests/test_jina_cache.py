"""Tests for Jina multivector disk cache."""

from __future__ import annotations

from pathlib import Path

from app.rag.embed.jina_cache import cache_file_for, load_cached_vectors, save_cached_vectors


def test_jina_cache_roundtrip(tmp_path: Path) -> None:
    vectors = [[1.0, 0.0], [0.0, 1.0]]
    path = cache_file_for(tmp_path, "slide-10.png")
    save_cached_vectors(path, vectors)
    loaded = load_cached_vectors(path)
    assert loaded == vectors
