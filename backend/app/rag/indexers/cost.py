"""Index build cost metrics for multimodal eval indexers."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class IndexCost:
    collection: str
    build_time_s: float
    index_size_mb: float
    api_calls: int
    est_cost_usd: float
    chunks: int
    is_multivector: bool = False
