"""Preflight check for Jina v4 multivector API (method D)."""

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

from app.rag.embed.jina_multivector import DEFAULT_JINA_MODEL, JinaMultivectorEmbedder
from env_loader import load_repo_env


def check(*, probe: bool, model_id: str, max_side: int) -> int:
    load_repo_env()
    from app.config import get_settings

    settings = get_settings()
    if not settings.jina_api_key:
        print("FAIL: JINA_API_KEY is not set", file=sys.stderr)
        return 1
    print(f"OK config: model={model_id}, d_max_side={settings.d_max_side}")

    if not probe:
        return 0

    slide = REPO_ROOT / "data" / "multimodal-rag" / "slide-10.png"
    if not slide.exists():
        print(f"FAIL: probe slide not found: {slide}", file=sys.stderr)
        return 1

    embedder = JinaMultivectorEmbedder(model_id, settings=settings)
    image_mv = embedder.embed_image(slide, max_side=max_side)
    query_mv = embedder.embed_query("Какой процент компаний использует ИИ-агентов?")
    if not image_mv or not query_mv:
        print("FAIL: empty multivector response", file=sys.stderr)
        return 1
    print(
        f"OK probe: image_patches={len(image_mv)}, query_patches={len(query_mv)}, "
        f"dim={len(image_mv[0])}",
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Check Jina multivector API")
    parser.add_argument("--model", default=DEFAULT_JINA_MODEL)
    parser.add_argument("--max-side", type=int, default=768)
    parser.add_argument("--probe", action="store_true")
    args = parser.parse_args()
    return check(probe=args.probe, model_id=args.model, max_side=args.max_side)


if __name__ == "__main__":
    sys.exit(main())
