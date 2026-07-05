"""Batch OCR over slide PNG corpus."""

from __future__ import annotations

import time
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from app.rag.ocr.registry import make_ocr_engine

EXPECTED_SLIDES = 66


def slide_paths(slide_dir: Path, slides: list[int] | None) -> list[Path]:
    if slides is not None:
        return [slide_dir / f"slide-{slide_no:02d}.png" for slide_no in slides]
    paths = sorted(slide_dir.glob("slide-*.png"))
    if len(paths) != EXPECTED_SLIDES:
        msg = f"Expected {EXPECTED_SLIDES} PNG slides in {slide_dir}, found {len(paths)}"
        raise RuntimeError(msg)
    return paths


def run_ocr_batch(
    *,
    slide_dir: Path,
    out_dir: Path,
    engine_name: str,
    preprocess: str = "dark_theme",
    slides: list[int] | None = None,
    force: bool = False,
    engine_options: Mapping[str, Any] | None = None,
) -> float:
    slide_dir = slide_dir.resolve()
    out_dir = out_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    engine = make_ocr_engine(engine_name, engine_options)
    paths = slide_paths(slide_dir, slides)
    started = time.perf_counter()

    for image_path in paths:
        slide_no = int(image_path.stem.split("-", maxsplit=1)[1])
        out_path = out_dir / f"slide-{slide_no:02d}.txt"
        if out_path.exists() and not force:
            continue
        if not image_path.exists():
            msg = f"Slide image not found: {image_path}"
            raise FileNotFoundError(msg)
        text = engine.recognize(image_path, preprocess=preprocess)
        out_path.write_text(text + ("\n" if text else ""), encoding="utf-8")

    return time.perf_counter() - started
