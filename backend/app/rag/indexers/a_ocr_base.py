"""Base OCR indexer: ensure OCR artifacts then e5 -> Qdrant."""

from __future__ import annotations

import time
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from app.rag.indexers.slide_embed import (
    EXPECTED_SLIDES,
    get_settings_or_raise,
    load_slide_texts,
    upsert_slide_texts_to_qdrant,
)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[4]


def _corpus_complete(corpus_dir: Path) -> bool:
    if not corpus_dir.is_dir():
        return False
    return len(list(corpus_dir.glob("slide-*.txt"))) == EXPECTED_SLIDES


def ensure_ocr_artifacts(
    *,
    engine: str,
    corpus_dir: Path,
    options: Mapping[str, Any] | None,
    force: bool,
) -> None:
    opts = dict(options or {})
    if _corpus_complete(corpus_dir) and not opts.get("force_ocr"):
        return
    target = "ocr-multimodal-tesseract" if engine == "tesseract" else "ocr-multimodal-modern"
    msg = f"OCR artifacts missing in {corpus_dir}. Run: make {target}"
    raise FileNotFoundError(msg)


class OcrTextIndexer:
    ocr_engine: str = ""
    method: str = ""
    artifact_prefix: str = ""

    def build_index(
        self,
        *,
        corpus_dir: Path,
        collection: str,
        force: bool = False,
        options: Mapping[str, Any] | None = None,
    ):
        opts = dict(options or {})
        repo = _repo_root()
        slide_dir = Path(str(opts.get("slide_dir", "data/multimodal-rag")))
        if not slide_dir.is_absolute():
            slide_dir = (repo / slide_dir).resolve()
        if not slide_dir.exists():
            raise FileNotFoundError(f"Slide directory not found: {slide_dir}")
        corpus_dir.mkdir(parents=True, exist_ok=True)
        started = time.perf_counter()
        ensure_ocr_artifacts(
            engine=self.ocr_engine,
            corpus_dir=corpus_dir,
            options=opts,
            force=force,
        )
        settings = get_settings_or_raise()
        slides = load_slide_texts(corpus_dir, source_prefix=self.artifact_prefix)
        return upsert_slide_texts_to_qdrant(
            slides=slides,
            collection=collection,
            settings=settings,
            force=force,
            build_time_s=time.perf_counter() - started,
        )
