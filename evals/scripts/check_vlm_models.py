"""Preflight check for OpenRouter VLM models (catalog + optional probe)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import httpx

REPO_ROOT = Path(__file__).resolve().parents[2]
BACKEND_DIR = REPO_ROOT / "backend"
SCRIPTS_DIR = REPO_ROOT / "evals" / "scripts"

for path in (BACKEND_DIR, SCRIPTS_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from app.rag.caption.openrouter_vlm import OpenRouterVlmCaptioner
from env_loader import load_repo_env

DEFAULT_MODELS = (
    "nvidia/nemotron-nano-12b-v2-vl:free",
    "google/gemini-2.5-flash",
)


def _fetch_catalog(base_url: str) -> set[str]:
    url = f"{base_url.rstrip('/')}/models"
    with httpx.Client(timeout=20.0) as client:
        response = client.get(url)
        response.raise_for_status()
        body = response.json()
    return {item["id"] for item in body.get("data", []) if item.get("id")}


def check_models(
    model_ids: list[str],
    *,
    probe: bool = False,
    probe_slide: Path | None = None,
) -> int:
    load_repo_env()
    from app.config import get_settings

    settings = get_settings()
    catalog = _fetch_catalog(settings.openrouter_base_url)
    missing = [model_id for model_id in model_ids if model_id not in catalog]
    if missing:
        print(f"FAIL: models not in OpenRouter catalog: {missing}", file=sys.stderr)
        return 1
    print(f"OK catalog: {', '.join(model_ids)}")

    if not probe:
        return 0

    slide = probe_slide or (REPO_ROOT / "data" / "multimodal-rag" / "slide-02.png")
    if not slide.exists():
        print(f"FAIL: probe slide not found: {slide}", file=sys.stderr)
        return 1

    for model_id in model_ids:
        captioner = OpenRouterVlmCaptioner(model_id, settings=settings)
        result = captioner.caption_slide(slide, max_side=1536)
        if not result.text.strip():
            print(f"FAIL: empty caption from {model_id}", file=sys.stderr)
            return 1
        print(
            f"OK probe {model_id}: {len(result.text)} chars, "
            f"tokens={result.usage.total_tokens}, est=${result.est_cost_usd:.6f}",
        )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Check OpenRouter VLM model availability")
    parser.add_argument(
        "--models",
        default=",".join(DEFAULT_MODELS),
        help="Comma-separated OpenRouter model ids",
    )
    parser.add_argument("--probe", action="store_true", help="Run 1-slide caption with API key")
    parser.add_argument("--probe-slide", default="", help="PNG path for probe")
    args = parser.parse_args()
    model_ids = [part.strip() for part in args.models.split(",") if part.strip()]
    probe_slide = Path(args.probe_slide) if args.probe_slide else None
    return check_models(model_ids, probe=args.probe, probe_slide=probe_slide)


if __name__ == "__main__":
    sys.exit(main())
