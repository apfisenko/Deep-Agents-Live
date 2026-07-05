"""Batch OCR for multimodal slide PNG corpus."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
BACKEND_DIR = REPO_ROOT / "backend"
SCRIPTS_DIR = REPO_ROOT / "evals" / "scripts"

for path in (BACKEND_DIR, SCRIPTS_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from app.rag.ocr.batch import run_ocr_batch


def _parse_slides(raw: str | None) -> list[int] | None:
    if not raw:
        return None
    return [int(part.strip()) for part in raw.split(",") if part.strip()]


def main() -> int:
    parser = argparse.ArgumentParser(description="Run OCR over multimodal slide PNGs")
    parser.add_argument("--slide-dir", default=str(REPO_ROOT / "data" / "multimodal-rag"))
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--engine", choices=("tesseract", "modern"), required=True)
    parser.add_argument("--preprocess", default="dark_theme")
    parser.add_argument("--slides", default="", help="Comma-separated slide numbers, e.g. 2,10,11")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    elapsed = run_ocr_batch(
        slide_dir=Path(args.slide_dir),
        out_dir=Path(args.out_dir),
        engine_name=args.engine,
        preprocess=args.preprocess,
        slides=_parse_slides(args.slides or None),
        force=args.force,
    )
    print(f"OCR done: engine={args.engine}, {elapsed:.1f}s, out={args.out_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
