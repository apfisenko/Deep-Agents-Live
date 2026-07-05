"""Jina v4 multivector image indexer (method D)."""

from __future__ import annotations

import shutil
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from app.rag.embed.jina_cache import cache_file_for, load_cached_vectors, save_cached_vectors
from app.rag.embed.jina_multivector import (
    DEFAULT_JINA_MODEL,
    EST_COST_PER_IMAGE_USD,
    JinaMultivectorEmbedder,
)
from app.rag.indexers.cost import IndexCost
from app.rag.indexers.multivector_qdrant import upsert_slide_multivectors_to_qdrant
from app.rag.indexers.slide_embed import get_settings_or_raise
from app.rag.indexers.slide_image_embed import load_slide_pngs


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[4]


class JinaMultivectorIndexer:
    method = "D_jina_multivector"

    def build_index(
        self,
        *,
        corpus_dir: Path,
        collection: str,
        force: bool = False,
        options: Mapping[str, Any] | None = None,
    ) -> IndexCost:
        opts = dict(options or {})
        settings = get_settings_or_raise()
        model_id = str(opts.get("embed_model") or DEFAULT_JINA_MODEL)
        max_side = int(opts.get("max_side") or settings.d_max_side)
        slides = load_slide_pngs(corpus_dir)
        embedder = JinaMultivectorEmbedder(model_id, settings=settings)

        cache_dir = Path(str(opts.get("cache_dir", "evals/artifacts/jina-multivector")))
        if not cache_dir.is_absolute():
            cache_dir = (_repo_root() / cache_dir).resolve()
        if opts.get("clear_jina_cache") and cache_dir.exists():
            shutil.rmtree(cache_dir)
        cache_dir.mkdir(parents=True, exist_ok=True)

        total = len(slides)
        done = 0
        api_calls = 0

        def embed_fn(path: Path) -> list[list[float]]:
            nonlocal done, api_calls
            done += 1
            cache_path = cache_file_for(cache_dir, path.name)
            cached = load_cached_vectors(cache_path)
            if cached is not None:
                print(f"  jina embed {done}/{total}: {path.name} (cached)", flush=True)  # noqa: T201
                return cached
            print(f"  jina embed {done}/{total}: {path.name}", flush=True)  # noqa: T201
            vectors = embedder.embed_image(path, max_side=max_side)
            api_calls += 1
            save_cached_vectors(cache_path, vectors)
            return vectors

        cost = upsert_slide_multivectors_to_qdrant(
            slides=slides,
            collection=collection,
            settings=settings,
            force=force,
            embed_fn=embed_fn,
            api_calls=max(api_calls, len(slides)),
            est_cost_usd=api_calls * EST_COST_PER_IMAGE_USD,
        )
        return IndexCost(
            collection=cost.collection,
            build_time_s=cost.build_time_s,
            index_size_mb=cost.index_size_mb,
            api_calls=api_calls,
            est_cost_usd=round(api_calls * EST_COST_PER_IMAGE_USD, 6),
            chunks=cost.chunks,
            is_multivector=True,
        )
