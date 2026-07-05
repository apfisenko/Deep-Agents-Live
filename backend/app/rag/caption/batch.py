"""Batch VLM captioning over slide PNG corpus."""

from __future__ import annotations

import json
import time
from collections.abc import Mapping
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from app.rag.caption.openrouter_vlm import OpenRouterVlmCaptioner
from app.rag.caption.prompts import DEFAULT_CAPTION_PROMPT

EXPECTED_SLIDES = 66
EMBED_EST_COST_USD = 0.002


@dataclass(frozen=True)
class CaptionBatchMeta:
    model_id: str
    slide_dir: str
    out_dir: str
    slides_processed: int
    caption_wall_time_s: float
    vlm_api_calls: int
    prompt_tokens: int
    completion_tokens: int
    est_vlm_cost_usd: float
    sec_per_slide: float


def slide_paths(slide_dir: Path, slides: list[int] | None) -> list[Path]:
    if slides is not None:
        return [slide_dir / f"slide-{slide_no:02d}.png" for slide_no in slides]
    paths = sorted(slide_dir.glob("slide-*.png"))
    if len(paths) != EXPECTED_SLIDES:
        msg = f"Expected {EXPECTED_SLIDES} PNG slides in {slide_dir}, found {len(paths)}"
        raise RuntimeError(msg)
    return paths


def _caption_one(
    *,
    captioner: OpenRouterVlmCaptioner,
    image_path: Path,
    out_path: Path,
    prompt: str,
    max_side: int,
    force: bool,
) -> tuple[int, int, int, float] | None:
    if out_path.exists() and not force:
        return None
    if not image_path.exists():
        msg = f"Slide image not found: {image_path}"
        raise FileNotFoundError(msg)
    result = captioner.caption_slide(image_path, prompt=prompt, max_side=max_side)
    text = result.text
    out_path.write_text(text + ("\n" if text else ""), encoding="utf-8")
    return (
        result.usage.prompt_tokens,
        result.usage.completion_tokens,
        result.usage.total_tokens,
        result.est_cost_usd,
    )


def run_caption_batch(
    *,
    slide_dir: Path,
    out_dir: Path,
    model_id: str,
    slides: list[int] | None = None,
    force: bool = False,
    max_side: int = 1536,
    concurrency: int = 3,
    prompt: str | None = None,
    meta_path: Path | None = None,
    batch_options: Mapping[str, Any] | None = None,
) -> CaptionBatchMeta:
    opts = dict(batch_options or {})
    slide_dir = slide_dir.resolve()
    out_dir = out_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    captioner = OpenRouterVlmCaptioner(model_id)
    paths = slide_paths(slide_dir, slides)
    text_prompt = prompt or DEFAULT_CAPTION_PROMPT
    workers = max(1, int(opts.get("caption_concurrency", concurrency)))
    max_side_px = int(opts.get("caption_max_side", max_side))

    started = time.perf_counter()
    prompt_tokens = 0
    completion_tokens = 0
    vlm_cost = 0.0
    api_calls = 0

    def _job(image_path: Path) -> tuple[int, int, int, float] | None:
        slide_no = int(image_path.stem.split("-", maxsplit=1)[1])
        out_path = out_dir / f"slide-{slide_no:02d}.txt"
        return _caption_one(
            captioner=captioner,
            image_path=image_path,
            out_path=out_path,
            prompt=text_prompt,
            max_side=max_side_px,
            force=force,
        )

    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(_job, path): path for path in paths}
        for future in as_completed(futures):
            stats = future.result()
            if stats is None:
                continue
            p_tok, c_tok, _total, cost = stats
            prompt_tokens += p_tok
            completion_tokens += c_tok
            vlm_cost += cost
            api_calls += 1
            print(f"caption progress: {api_calls} slides captioned", flush=True)

    wall = time.perf_counter() - started
    processed = len(list(out_dir.glob("slide-*.txt")))
    meta = CaptionBatchMeta(
        model_id=model_id,
        slide_dir=str(slide_dir),
        out_dir=str(out_dir),
        slides_processed=processed,
        caption_wall_time_s=round(wall, 2),
        vlm_api_calls=api_calls,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        est_vlm_cost_usd=round(vlm_cost, 6),
        sec_per_slide=round(wall / max(api_calls, 1), 2),
    )
    if meta_path is not None:
        meta_path.parent.mkdir(parents=True, exist_ok=True)
        meta_path.write_text(json.dumps(asdict(meta), indent=2) + "\n", encoding="utf-8")
    return meta
