"""Run graphrag baseline locally without Langfuse (agent + judge metrics only)."""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from typing import Any
from uuid import uuid4

REPO_ROOT = Path(__file__).resolve().parents[2]
BACKEND_DIR = REPO_ROOT / "backend"
SCRIPTS_DIR = REPO_ROOT / "evals" / "scripts"
EVALS_ROOT = REPO_ROOT / "evals"

for path in (BACKEND_DIR, SCRIPTS_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

import httpx
from app.agent.run_config import RunConfig
from dataset_registry import GRAPHAG_DATASET_SLUGS, resolve_dataset_target
from env_loader import load_repo_env
from evaluators import build_judge_runtime, make_item_evaluators
from models import load_manifest
from run_experiment import (
    call_agent,
    git_sha8,
    iso_ts,
    manifest_to_experiment_items,
    resolve_eval_stream_url,
    slug_to_run_suffix,
)


def check_backend_health(api_url: str, *, min_rag_docs: int = 1) -> None:
    health_url = api_url.replace("/api/v1/chat", "/health")
    with httpx.Client(timeout=30.0) as client:
        response = client.get(health_url)
        response.raise_for_status()
        rag_docs = int(response.json().get("rag_indexed_docs", 0))
        if rag_docs < min_rag_docs:
            msg = f"RAG index empty (rag_indexed_docs={rag_docs})"
            raise RuntimeError(msg)


async def evaluate_item(
    evaluators: list[Any],
    *,
    item: dict[str, Any],
    output: dict[str, Any],
) -> dict[str, float | str]:
    scores: dict[str, float | str] = {}
    for evaluator in evaluators:
        try:
            if evaluator.__name__ == "task_error":
                result = evaluator(output=output)
            elif evaluator.__name__ in {
                "answer_correctness",
                "faithfulness",
                "answer_relevancy",
                "context_recall",
            }:
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
            scores[evaluator.__name__] = 0.0
            print(f"warn: {item['metadata']['item_id']} {evaluator.__name__}: {exc}")
    return scores


async def run_dataset(
    *,
    config: RunConfig,
    slug: str,
    config_path: Path,
) -> Path:
    target = resolve_dataset_target(config, slug, apply_name_override=False)
    items = manifest_to_experiment_items(target.manifest_path)
    judge = build_judge_runtime(config)
    evaluators = make_item_evaluators(judge, dataset_slug=slug)

    chat_url = resolve_eval_stream_url(config.agent.api_url)
    metric_sums: dict[str, list[float]] = {}
    item_rows: list[str] = []

    async with httpx.AsyncClient(timeout=180.0) as client:
        for index, item in enumerate(items, start=1):
            print(f"  item {index}/{len(items)}: {item['metadata']['item_id']}")
            payload = {
                "session_id": str(uuid4()),
                "channel": "web",
                "message": item["input"]["message"],
                "config_id": config.config_id,
                "metadata": {"eval_item_id": item["metadata"]["item_id"]},
            }
            result = await call_agent(client, url=chat_url, payload=payload)
            output = {
                "answer": result.answer,
                "contexts": result.contexts,
                "tools_called": result.tools_called,
                "error": None if result.answer else "empty reply",
            }
            scores = await evaluate_item(evaluators, item=item, output=output)
            for name, value in scores.items():
                if isinstance(value, float) and name != "task_error":
                    metric_sums.setdefault(name, []).append(value)
            answer_preview = (output.get("answer") or "").replace("\n", " ")[:500]
            item_rows.append(
                f"{item['metadata']['item_id']}\t"
                f"{float(scores.get('answer_correctness', 0)):.3f}\t"
                f"{float(scores.get('required_entity_recall_at_5', 0)):.3f}\t"
                f"{float(scores.get('faithfulness', 0)):.3f}\t"
                f"{answer_preview}",
            )

    run_suffix = slug_to_run_suffix(slug)
    run_name = f"{config.config_id}--{run_suffix}--{git_sha8()}--{iso_ts()}"
    averages = {
        f"avg_{name}": sum(values) / len(values)
        for name, values in metric_sums.items()
        if values
    }
    error_rate = sum(
        1 for row in item_rows if "correctness=0.000" in row and "entity@5=0.000" in row
    ) / max(len(items), 1)

    lines = [
        f"Local graphrag baseline run: {run_name}",
        f"{len(items)} items",
        "Evaluations:",
        "  • answer_correctness",
        "  • required_entity_recall_at_5",
        "  • faithfulness",
        "  • task_error",
        "",
        "Average Scores:",
    ]
    for key in ("faithfulness", "answer_correctness", "required_entity_recall_at_5"):
        name = key if key.startswith("avg_") else key
        avg_key = f"avg_{name}" if not name.startswith("avg_") else name
        if avg_key in averages:
            lines.append(f"  • {name}: {averages[avg_key]:.3f}")
    lines.extend(["", "Run Evaluations:"])
    for key, value in averages.items():
        lines.append(f"  • {key}: {value:.3f}")
    lines.append(f"  • error_rate: {error_rate:.3f}")
    lines.extend(["", "Items:"])
    lines.extend(item_rows)

    report_path = EVALS_ROOT / "reports" / f"{run_name}.txt"
    report_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {report_path}")
    return report_path


async def main_async(config_path: Path) -> int:
    load_repo_env()
    config = RunConfig.from_yaml_path(config_path)
    check_backend_health(config.agent.api_url)
    for slug in GRAPHAG_DATASET_SLUGS:
        print(f"running {slug}...")
        await run_dataset(config=config, slug=slug, config_path=config_path)
    return 0


def main() -> int:
    config_path = EVALS_ROOT / "configs" / "graphrag-baseline.yaml"
    return asyncio.run(main_async(config_path))


if __name__ == "__main__":
    sys.exit(main())
