"""VLM caption multimodal indexer: captions -> e5 -> Qdrant."""

from __future__ import annotations

import json
import time
from collections.abc import Mapping
from pathlib import Path
from typing import TYPE_CHECKING, Any

from app.rag.caption.batch import EMBED_EST_COST_USD
from app.rag.indexers.slide_embed import (
    EXPECTED_SLIDES,
    get_settings_or_raise,
    load_slide_texts,
    upsert_slide_texts_to_qdrant,
)

if TYPE_CHECKING:
    from app.rag.indexers.cost import IndexCost


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[4]


def _corpus_complete(corpus_dir: Path) -> bool:
    if not corpus_dir.is_dir():
        return False
    return len(list(corpus_dir.glob("slide-*.txt"))) == EXPECTED_SLIDES


def _model_slug(corpus_dir: Path) -> str:
    return corpus_dir.name


def _meta_path(model_slug: str) -> Path:
    return _repo_root() / "evals" / "reports" / f"{model_slug}-caption-meta.json"


def _load_caption_meta(model_slug: str) -> dict[str, Any]:
    path = _meta_path(model_slug)
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def ensure_caption_artifacts(
    *,
    corpus_dir: Path,
    model_slug: str,
    options: Mapping[str, Any] | None,
) -> None:
    opts = dict(options or {})
    if _corpus_complete(corpus_dir) and not opts.get("force_caption"):
        return
    target = "caption-multimodal-nemotron"
    if "gemini" in model_slug:
        target = "caption-multimodal-gemini"
    msg = f"Caption artifacts missing in {corpus_dir}. Run: make {target}"
    raise FileNotFoundError(msg)


class CaptionIndexer:
    method = "B_caption"

    def build_index(
        self,
        *,
        corpus_dir: Path,
        collection: str,
        force: bool = False,
        options: Mapping[str, Any] | None = None,
    ) -> IndexCost:
        opts = dict(options or {})
        repo = _repo_root()
        slide_dir = Path(str(opts.get("slide_dir", "data/multimodal-rag")))
        if not slide_dir.is_absolute():
            slide_dir = (repo / slide_dir).resolve()
        if not slide_dir.exists():
            msg = f"Slide directory not found: {slide_dir}"
            raise FileNotFoundError(msg)

        corpus_dir.mkdir(parents=True, exist_ok=True)
        slug = _model_slug(corpus_dir.resolve())
        started = time.perf_counter()
        ensure_caption_artifacts(corpus_dir=corpus_dir, model_slug=slug, options=opts)

        settings = get_settings_or_raise()
        source_prefix = f"evals/artifacts/captions/{slug}"
        slides = load_slide_texts(corpus_dir, source_prefix=source_prefix)
        embed_started = time.perf_counter()
        cost = upsert_slide_texts_to_qdrant(
            slides=slides,
            collection=collection,
            settings=settings,
            force=force,
            build_time_s=time.perf_counter() - embed_started,
        )

        meta = _load_caption_meta(slug)
        caption_wall = float(meta.get("caption_wall_time_s") or 0.0)
        vlm_calls = int(meta.get("vlm_api_calls") or 0)
        if _corpus_complete(corpus_dir) and vlm_calls < EXPECTED_SLIDES:
            vlm_calls = EXPECTED_SLIDES
        vlm_cost = float(meta.get("est_vlm_cost_usd") or 0.0)
        total_time = round(caption_wall + (time.perf_counter() - started), 2)

        return type(cost)(
            collection=cost.collection,
            build_time_s=total_time,
            index_size_mb=cost.index_size_mb,
            api_calls=vlm_calls + cost.api_calls,
            est_cost_usd=round(vlm_cost + EMBED_EST_COST_USD, 6),
            chunks=cost.chunks,
            is_multivector=cost.is_multivector,
        )
