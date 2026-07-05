"""Config-driven multimodal retrieval eval (sprint-07 task 03)."""

from __future__ import annotations

import argparse
import asyncio
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
BACKEND_DIR = REPO_ROOT / "backend"
SCRIPTS_DIR = REPO_ROOT / "evals" / "scripts"
EVALS_ROOT = REPO_ROOT / "evals"

for path in (BACKEND_DIR, SCRIPTS_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from qdrant_client import QdrantClient

from app.config import get_settings
from app.integrations.qdrant_url import resolve_qdrant_url
from dataset_registry import MULTIMODAL_DATASET_SLUGS, resolve_dataset_target, slug_to_run_suffix
from env_loader import load_repo_env
from models import load_manifest
from multimodal_config import MultimodalEvalConfig
from multimodal_metrics import (
    mean_metric,
    segment_retrieval_metrics,
    unanswerable_refusal_score,
)
from multimodal_retrieval import retrieve_pages

TOP_K = 5


def git_sha8() -> str:
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "--short=8", "HEAD"],
            cwd=REPO_ROOT,
            text=True,
            stderr=subprocess.DEVNULL,
        )
        return out.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


def iso_ts() -> str:
    return datetime.now(tz=UTC).strftime("%Y%m%dT%H%M%SZ")


def manifest_to_experiment_items(manifest_path: Path) -> list[dict[str, Any]]:
    manifest = load_manifest(manifest_path)
    items: list[dict[str, Any]] = []
    for item in manifest.items:
        meta = item.metadata.model_dump(exclude_none=True)
        facts = meta.pop("facts", item.metadata.facts)
        metadata = {
            **meta,
            "item_id": item.id,
            "facts_count": len(facts),
        }
        if facts:
            preview = "; ".join(facts[:3])
            metadata["facts_preview"] = preview[:200]
        expected_output = item.expected_output.model_dump()
        expected_output["reference_facts"] = facts
        items.append(
            {
                "input": item.input.model_dump(),
                "expected_output": expected_output,
                "metadata": metadata,
            },
        )
    return items


@dataclass(frozen=True)
class ItemRun:
    item_id: str
    segment: str
    metrics: dict[str, float]
    retrieved_pages: list[int]
    answer_preview: str = ""


async def evaluate_generation_item(
    evaluators: list[Any],
    *,
    item: dict[str, Any],
    answer: str,
    contexts: list[str],
) -> dict[str, float]:
    output = {"answer": answer, "contexts": contexts, "tools_called": []}
    scores: dict[str, float] = {}
    for evaluator in evaluators:
        try:
            if evaluator.__name__ == "task_error":
                result = evaluator(output=output)
            elif evaluator.__name__ in {"answer_correctness", "faithfulness", "answer_relevancy"}:
                result = await evaluator(
                    input=item["input"],
                    output=output,
                    expected_output=item["expected_output"],
                    metadata=item.get("metadata"),
                )
            else:
                result = evaluator(
                    output=output,
                    expected_output=item["expected_output"],
                    metadata=item.get("metadata"),
                )
            scores[result.name] = float(result.value)
        except Exception as exc:
            print(f"warn: {item['metadata']['item_id']} {evaluator.__name__}: {exc}")
            scores[evaluator.__name__] = 0.0
    return scores


async def run_dataset(
    *,
    config: MultimodalEvalConfig,
    slug: str,
    collection: str,
    with_generation: bool,
) -> Path:
    target = resolve_dataset_target(config, slug, apply_name_override=False)
    items = manifest_to_experiment_items(target.manifest_path)
    settings = get_settings()
    client = QdrantClient(
        url=resolve_qdrant_url(settings.qdrant_url),
        api_key=settings.qdrant_api_key or None,
    )
    if not client.collection_exists(collection):
        msg = (
            f"Collection {collection!r} missing. "
            f"Run index_multimodal.py --config ... first."
        )
        raise RuntimeError(msg)

    gen_evaluators: list[Any] = []
    if with_generation:
        from evaluators import build_judge_runtime, make_item_evaluators

        judge = build_judge_runtime(config)
        gen_evaluators = make_item_evaluators(judge, dataset_slug=slug)

    item_runs: list[ItemRun] = []
    metric_buckets: dict[str, list[float]] = {}

    for index, item in enumerate(items, start=1):
        meta = item["metadata"]
        item_id = str(meta["item_id"])
        segment = str(meta.get("multimodal_segment", ""))
        gold_pages = [int(p) for p in meta.get("gold_pages") or []]
        question = item["input"]["message"]
        print(f"  item {index}/{len(items)}: {item_id}")

        retrieved_pages, contexts = retrieve_pages(
            client,
            collection,
            question,
            method=config.indexer.method,
            embedding_model=config.vector_db.embedding_model,
            top_k=TOP_K,
            settings=settings,
        )
        metrics = segment_retrieval_metrics(segment, retrieved_pages, gold_pages, k=TOP_K)

        answer_preview = ""
        if segment == "S5_unanswerable" and with_generation and gen_evaluators:
            import httpx
            from uuid import uuid4

            from run_experiment import call_agent, resolve_eval_stream_url

            async with httpx.AsyncClient(timeout=180.0) as http:
                payload = {
                    "session_id": str(uuid4()),
                    "channel": "web",
                    "message": question,
                    "config_id": config.config_id,
                    "metadata": {"eval_item_id": item_id},
                }
                chat_url = resolve_eval_stream_url(config.agent.api_url)
                result = await call_agent(http, url=chat_url, payload=payload)
                answer_preview = (result.answer or "").replace("\n", " ")[:400]
                gen_scores = await evaluate_generation_item(
                    gen_evaluators,
                    item=item,
                    answer=result.answer,
                    contexts=result.contexts or contexts,
                )
                metrics.update(gen_scores)
                metrics["unanswerable_refusal_rate"] = unanswerable_refusal_score(result.answer)
        elif segment == "S5_unanswerable":
            metrics["unanswerable_refusal_rate"] = float("nan")

        item_runs.append(
            ItemRun(
                item_id=item_id,
                segment=segment,
                metrics=metrics,
                retrieved_pages=retrieved_pages,
                answer_preview=answer_preview,
            ),
        )
        for name, value in metrics.items():
            if value == value:
                metric_buckets.setdefault(name, []).append(value)

    run_suffix = slug_to_run_suffix(slug)
    run_name = f"{config.config_id}--{run_suffix}--{git_sha8()}--{iso_ts()}"
    lines = [
        f"Local multimodal eval run: {run_name}",
        f"{len(items)} items",
        f"collection={collection}",
        f"indexer={config.indexer.method}",
        f"embedding_model={config.vector_db.embedding_model}",
        f"corpus_dir={config.indexer.corpus_dir}",
        f"top_k={TOP_K}",
        "",
        "Average Scores:",
    ]
    for key in sorted(metric_buckets):
        avg = mean_metric(metric_buckets[key])
        if avg is not None:
            lines.append(f"  • avg_{key}: {avg:.3f}")

    lines.extend(["", "Items:"])
    for row in item_runs:
        recall = row.metrics.get("gold_page_recall_at_5", float("nan"))
        ndcg = row.metrics.get("ndcg_at_5", float("nan"))
        mrr_val = row.metrics.get("mrr", float("nan"))
        set_recall = row.metrics.get("gold_page_set_recall_at_5", float("nan"))
        refusal = row.metrics.get("unanswerable_refusal_rate", float("nan"))
        lines.append(
            f"{row.item_id}\t"
            f"{recall:.3f}\t{ndcg:.3f}\t{mrr_val:.3f}\t"
            f"{set_recall:.3f}\t{refusal:.3f}\t"
            f"{row.retrieved_pages}\t"
            f"{row.answer_preview}",
        )

    report_path = EVALS_ROOT / "reports" / f"{run_name}.txt"
    report_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {report_path}")
    return report_path


async def main_async(config_path: Path, *, with_generation: bool) -> int:
    load_repo_env()
    from app.integrations.qdrant_url import reset_qdrant_url_cache

    reset_qdrant_url_cache()
    config = MultimodalEvalConfig.from_yaml_path(config_path)
    collection = config.vector_db.collection
    for slug in MULTIMODAL_DATASET_SLUGS:
        print(f"running {slug}...")
        await run_dataset(
            config=config,
            slug=slug,
            collection=collection,
            with_generation=with_generation,
        )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Run multimodal retrieval eval from config")
    parser.add_argument(
        "--config",
        default=str(EVALS_ROOT / "configs" / "multimodal-baseline.yaml"),
    )
    parser.add_argument("--with-generation", action="store_true")
    args = parser.parse_args()
    return asyncio.run(main_async(Path(args.config), with_generation=args.with_generation))


if __name__ == "__main__":
    sys.exit(main())
