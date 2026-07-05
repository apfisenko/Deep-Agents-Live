"""Unified VL image embedding indexer (method C)."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

from app.rag.embed.unified_vl import DEFAULT_UNIFIED_EMBED_MODEL, OpenRouterUnifiedEmbedder
from app.rag.indexers.cost import IndexCost
from app.rag.indexers.slide_embed import get_settings_or_raise
from app.rag.indexers.slide_image_embed import load_slide_pngs, upsert_slide_images_to_qdrant


class UnifiedEmbedIndexer:
    method = "C_unified"

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
        model_id = str(opts.get("embed_model") or DEFAULT_UNIFIED_EMBED_MODEL)
        max_side = int(opts.get("max_side") or settings.c_max_side)
        embedder = OpenRouterUnifiedEmbedder(model_id, settings=settings)
        slides = load_slide_pngs(corpus_dir)

        def embed_fn(path: Path) -> list[float]:
            return embedder.embed_image(path, max_side=max_side)

        return upsert_slide_images_to_qdrant(
            slides=slides,
            collection=collection,
            settings=settings,
            force=force,
            embed_fn=embed_fn,
            api_calls=len(slides),
            est_cost_usd=0.0,
            payload_tag="unified-image-embed",
        )
