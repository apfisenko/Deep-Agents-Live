"""Config-driven multimodal index CLI (sprint-07 task 03)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
BACKEND_DIR = REPO_ROOT / "backend"
SCRIPTS_DIR = REPO_ROOT / "evals" / "scripts"
EVALS_ROOT = REPO_ROOT / "evals"

for path in (BACKEND_DIR, SCRIPTS_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from app.rag.indexers import make_indexer
from env_loader import load_repo_env
from multimodal_config import MultimodalEvalConfig


def index_from_config(config_path: Path, *, force: bool = False) -> int:
    load_repo_env()
    cfg = MultimodalEvalConfig.from_yaml_path(config_path)
    corpus_dir = cfg.resolve_corpus_dir(REPO_ROOT)
    indexer = make_indexer(cfg.indexer.method)
    build_kwargs: dict[str, object] = {
        "corpus_dir": corpus_dir,
        "collection": cfg.vector_db.collection,
        "force": force,
    }
    if cfg.indexer.options:
        build_kwargs["options"] = cfg.indexer.options
    cost = indexer.build_index(**build_kwargs)  # type: ignore[arg-type]
    cost_path = EVALS_ROOT / "reports" / f"{cfg.config_id}-index-cost.json"
    cost_path.parent.mkdir(parents=True, exist_ok=True)
    cost_path.write_text(
        json.dumps(
            {
                "collection": cost.collection,
                "build_time_s": cost.build_time_s,
                "index_size_mb": cost.index_size_mb,
                "est_cost_usd": cost.est_cost_usd,
                "api_calls": cost.api_calls,
                "chunks": cost.chunks,
                "is_multivector": cost.is_multivector,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(
        f"indexed {cost.chunks} slides into {cost.collection} "
        f"({cost.index_size_mb} MB, {cost.build_time_s}s, "
        f"est ${cost.est_cost_usd}, multivector={cost.is_multivector})",
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Index multimodal corpus via eval config")
    parser.add_argument(
        "--config",
        default=str(EVALS_ROOT / "configs" / "multimodal-baseline.yaml"),
    )
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    return index_from_config(Path(args.config), force=args.force)


if __name__ == "__main__":
    sys.exit(main())
