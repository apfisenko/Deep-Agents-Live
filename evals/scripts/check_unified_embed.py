"""Preflight check for OpenRouter unified VL embed model (method C)."""

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

from app.rag.embed.unified_vl import DEFAULT_UNIFIED_EMBED_MODEL, OpenRouterUnifiedEmbedder
from env_loader import load_repo_env

DEFAULT_MODEL = DEFAULT_UNIFIED_EMBED_MODEL


def check(*, probe: bool, model_id: str, max_side: int) -> int:
    load_repo_env()
    from app.config import get_settings

    settings = get_settings()
    embedder = OpenRouterUnifiedEmbedder(model_id, settings=settings)
    print(f"OK config: model={model_id}, c_max_side={settings.c_max_side}")

    if not probe:
        return 0

    slide = REPO_ROOT / "data" / "multimodal-rag" / "slide-02.png"
    if not slide.exists():
        print(f"FAIL: probe slide not found: {slide}", file=sys.stderr)
        return 1

    image_vec = embedder.embed_image(slide, max_side=max_side)
    query_vec = embedder.embed_query("Какие отделы внедряют ИИ-агентов?")
    if len(image_vec) < 64 or len(query_vec) != len(image_vec):
        print(
            f"FAIL: dim mismatch image={len(image_vec)} query={len(query_vec)}",
            file=sys.stderr,
        )
        return 1
    print(f"OK probe: dim={len(image_vec)}, image+query embed succeeded")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Check unified VL embed model")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--max-side", type=int, default=1536)
    parser.add_argument("--probe", action="store_true")
    args = parser.parse_args()
    return check(probe=args.probe, model_id=args.model, max_side=args.max_side)


if __name__ == "__main__":
    sys.exit(main())
