"""Disk cache for Jina multivector slide embeddings."""

from __future__ import annotations

import json
from pathlib import Path


def cache_file_for(cache_dir: Path, slide_png_name: str) -> Path:
    stem = slide_png_name.removesuffix(".png")
    return cache_dir / f"{stem}.json"


def load_cached_vectors(path: Path) -> list[list[float]] | None:
    if not path.is_file():
        return None
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, list) or not raw:
        return None
    return [[float(value) for value in row] for row in raw]


def save_cached_vectors(path: Path, vectors: list[list[float]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(vectors), encoding="utf-8")
