"""Batch VLM captioning for multimodal slide PNG corpus."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
BACKEND_DIR = REPO_ROOT / "backend"
SCRIPTS_DIR = REPO_ROOT / "evals" / "scripts"
REPORTS_DIR = REPO_ROOT / "evals" / "reports"

for path in (BACKEND_DIR, SCRIPTS_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from app.rag.caption.batch import run_caption_batch
from env_loader import load_repo_env


def _parse_slides(raw: str | None) -> list[int] | None:
    if not raw:
        return None
    return [int(part.strip()) for part in raw.split(",") if part.strip()]


def _resolve_repo_path(raw: str) -> Path:
    candidate = Path(raw)
    if candidate.is_absolute():
        return candidate.resolve()
    normalized = Path(*[part for part in candidate.parts if part not in {".", ".."}])
    return (REPO_ROOT / normalized).resolve()


def _model_slug_from_out_dir(out_dir: Path) -> str:
    return out_dir.resolve().name


def main() -> int:
    load_repo_env()
    parser = argparse.ArgumentParser(description="Run VLM captioning over multimodal slide PNGs")
    parser.add_argument("--slide-dir", default=str(REPO_ROOT / "data" / "multimodal-rag"))
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--model", required=True, help="OpenRouter VLM model id")
    parser.add_argument("--max-side", type=int, default=1536)
    parser.add_argument("--concurrency", type=int, default=3)
    parser.add_argument("--slides", default="", help="Comma-separated slide numbers, e.g. 2,10,11")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    out_dir = _resolve_repo_path(args.out_dir)
    slide_dir = _resolve_repo_path(args.slide_dir)

    slug = _model_slug_from_out_dir(out_dir)
    meta_path = REPORTS_DIR / f"{slug}-caption-meta.json"

    meta = run_caption_batch(
        slide_dir=slide_dir,
        out_dir=out_dir,
        model_id=args.model,
        slides=_parse_slides(args.slides or None),
        force=args.force,
        max_side=args.max_side,
        concurrency=args.concurrency,
        meta_path=meta_path,
    )
    print(
        f"caption done: model={args.model}, slides={meta.slides_processed}, "
        f"{meta.caption_wall_time_s}s ({meta.sec_per_slide}s/slide), "
        f"vlm_calls={meta.vlm_api_calls}, est_vlm=${meta.est_vlm_cost_usd}, meta={meta_path}",
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
