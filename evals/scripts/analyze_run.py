"""Analyze Langfuse experiment run — metrics summary and failure taxonomy (task 06)."""

from __future__ import annotations

import argparse
import statistics
import sys
from collections import Counter
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from langfuse import Langfuse

REPO_ROOT = Path(__file__).resolve().parents[2]
EVALS_ROOT = REPO_ROOT / "evals"
DEFAULT_MANIFEST = EVALS_ROOT / "datasets" / "e2e" / "e2e-qa" / "v001_2026-06-15.yaml"

if str(EVALS_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(EVALS_ROOT / "scripts"))

from error_taxonomy import (
    TAXONOMY_BY_ID,
    classify_taxonomy,
    taxonomy_counts,
    taxonomy_failure_rate,
)
from env_loader import load_repo_env, resolve_langfuse_host, resolve_langfuse_keys
from models import load_manifest


@dataclass
class ItemScores:
    answer_correctness: float | None = None
    faithfulness: float | None = None
    answer_relevancy: float | None = None
    task_error: float | None = None


@dataclass
class AnalyzedItem:
    trace_id: str
    item_id: str
    message: str
    answer: str
    contexts_count: int
    scores: ItemScores
    failure_layer: str
    failure_reason: str
    agent_trace_id: str | None = None
    tool_spans: list[str] = field(default_factory=list)
    intent: str = ""
    product_id: str = ""
    gt_quality: str = ""


def _load_env() -> None:
    load_repo_env()


def resolve_run_name(run_arg: str, reports_dir: Path) -> str:
    if run_arg:
        if run_arg.endswith(".txt"):
            return run_arg.removesuffix(".txt")
        return run_arg
    candidates = sorted(reports_dir.glob("baseline-react-inmemory--e2e-qa--*.txt"))
    if not candidates:
        msg = "No baseline report found; pass --run"
        raise FileNotFoundError(msg)
    return candidates[-1].stem


def _score_map(trace_scores: list[Any] | None) -> ItemScores:
    scores = ItemScores()
    for score in trace_scores or []:
        name = score.name
        value = float(score.value) if score.value is not None else None
        if name == "answer_correctness":
            scores.answer_correctness = value
        elif name == "faithfulness":
            scores.faithfulness = value
        elif name == "answer_relevancy":
            scores.answer_relevancy = value
        elif name == "task_error":
            scores.task_error = value
    return scores


def _facts_missing(facts: list[str], contexts: list[str]) -> list[str]:
    if not facts or not contexts:
        return facts[:3] if facts else []
    blob = "\n".join(contexts).lower()
    missing: list[str] = []
    for fact in facts:
        tokens = [t for t in fact.lower().replace("–", "-").split() if len(t) > 3]
        if tokens and not any(token in blob for token in tokens[:3]):
            missing.append(fact)
    return missing


def classify_failure(
    *,
    answer: str,
    contexts: list[str],
    scores: ItemScores,
    facts: list[str],
) -> tuple[str, str]:
    answer_lower = answer.lower()
    clarification_markers = (
        "уточните",
        "уточни",
        "о каком курсе",
        "b2c или b2b",
        "интересует ли вас",
        "можешь уточнить",
    )
    if any(marker in answer_lower for marker in clarification_markers):
        return "behavior", "Agent asked for clarification instead of answering from KB"

    if scores.task_error and scores.task_error >= 1.0:
        return "behavior", "Task failed (task_error=1)"

    if not contexts:
        return "retrieval", "No KB contexts in output (search not used or empty results)"

    missing_facts = _facts_missing(facts, contexts)
    correctness = scores.answer_correctness
    faithfulness = scores.faithfulness

    if missing_facts and (correctness is None or correctness < 0.55):
        preview = "; ".join(missing_facts[:2])
        return "kb_gap", f"Key facts absent from retrieved contexts: {preview}"

    if faithfulness is not None and faithfulness < 0.55:
        return "generation", f"Low faithfulness ({faithfulness:.2f}) vs retrieved contexts"

    if correctness is not None and correctness < 0.55:
        return "generation", f"Low answer_correctness ({correctness:.2f}) despite retrieval"

    return "generation", "Low correctness/relevancy (mixed signals)"


def get_agent_tool_spans(langfuse: Langfuse, session_id: str) -> tuple[str | None, list[str]]:
    traces = langfuse.api.trace.list(limit=100)
    agent_trace = next(
        (
            trace
            for trace in traces.data
            if trace.name == "LangGraph" and (trace.metadata or {}).get("session_id") == session_id
        ),
        None,
    )
    if agent_trace is None:
        return None, []
    full = langfuse.api.trace.get(agent_trace.id)
    tools = [obs.name for obs in (full.observations or []) if obs.type == "TOOL" and obs.name]
    return agent_trace.id, tools


def fetch_run_items(langfuse: Langfuse, run_name: str) -> list[dict[str, Any]]:
    matched: list[Any] = []
    page = 1
    while page <= 20:
        traces = langfuse.api.trace.list(limit=100, page=page, name="experiment-item-run")
        if not traces.data:
            break
        for trace in traces.data:
            experiment_run = str((trace.metadata or {}).get("experiment_run_name", ""))
            if run_name in experiment_run:
                matched.append(trace)
        page += 1
    if not matched:
        msg = f"No experiment-item-run traces for run '{run_name}'"
        raise ValueError(msg)
    items: list[dict[str, Any]] = []
    for summary in matched:
        full = langfuse.api.trace.get(summary.id)
        items.append(
            {
                "trace_id": full.id,
                "input": full.input or {},
                "output": full.output or {},
                "metadata": full.metadata or {},
                "scores": _score_map(full.scores),
            },
        )
    return items


def resolve_manifest_path(run_metadata: dict[str, Any], manifest_arg: str) -> Path:
    if manifest_arg:
        manifest_path = Path(manifest_arg)
        if not manifest_path.is_absolute():
            manifest_path = EVALS_ROOT / manifest_path
        return manifest_path
    relative = str(run_metadata.get("manifest_path", "")).strip()
    if relative:
        candidate = REPO_ROOT / relative
        if candidate.exists():
            return candidate
    return DEFAULT_MANIFEST


def assign_taxonomy(item: AnalyzedItem) -> str:
    return classify_taxonomy(
        failure_layer=item.failure_layer,
        failure_reason=item.failure_reason,
        intent=item.intent,
        scores=item.scores,
    )


def build_manifest_index(manifest_path: Path) -> dict[str, Any]:
    manifest = load_manifest(manifest_path)
    return {item.id: item for item in manifest.items}


def analyze_items(
    langfuse: Langfuse,
    raw_items: list[dict[str, Any]],
    manifest_index: dict[str, Any],
) -> list[AnalyzedItem]:
    analyzed: list[AnalyzedItem] = []
    for raw in raw_items:
        metadata = raw["metadata"]
        output = raw["output"] if isinstance(raw["output"], dict) else {}
        input_data = raw["input"] if isinstance(raw["input"], dict) else {}
        item_id = str(metadata.get("item_id", "unknown"))
        manifest_item = manifest_index.get(item_id)
        facts = list(manifest_item.metadata.facts) if manifest_item else []
        answer = str(output.get("answer", ""))
        contexts = list(output.get("contexts") or [])
        session_id = str(output.get("session_id", ""))
        scores: ItemScores = raw["scores"]
        layer, reason = classify_failure(
            answer=answer,
            contexts=contexts,
            scores=scores,
            facts=facts,
        )
        agent_trace_id, tool_spans = (
            get_agent_tool_spans(langfuse, session_id) if session_id else (None, [])
        )
        analyzed.append(
            AnalyzedItem(
                trace_id=raw["trace_id"],
                item_id=item_id,
                message=str(input_data.get("message", "")),
                answer=answer,
                contexts_count=len(contexts),
                scores=scores,
                failure_layer=layer,
                failure_reason=reason,
                agent_trace_id=agent_trace_id,
                tool_spans=tool_spans,
                intent=str(metadata.get("intent", "")),
                product_id=str(metadata.get("product_id", "")),
                gt_quality=str(metadata.get("gt_quality", "")),
            ),
        )
    analyzed.sort(
        key=lambda item: (
            item.scores.answer_correctness if item.scores.answer_correctness is not None else 1.0,
            item.scores.faithfulness if item.scores.faithfulness is not None else 1.0,
        ),
    )
    return analyzed


def _distribution(values: list[float]) -> dict[str, int]:
    buckets = {"0.00-0.30": 0, "0.30-0.50": 0, "0.50-0.75": 0, "0.75-1.00": 0}
    for value in values:
        if value < 0.30:
            buckets["0.00-0.30"] += 1
        elif value < 0.50:
            buckets["0.30-0.50"] += 1
        elif value < 0.75:
            buckets["0.50-0.75"] += 1
        else:
            buckets["0.75-1.00"] += 1
    return buckets


def _avg(values: list[float]) -> float:
    return statistics.mean(values) if values else 0.0


def _fmt_score(value: float | None) -> str:
    return f"{value:.3f}" if value is not None else "n/a"


def render_taxonomy_section(items: list[AnalyzedItem]) -> list[str]:
    counts = taxonomy_counts(items)
    total_failures = sum(counts.values())
    rates = taxonomy_failure_rate(counts, total_failures)
    lines = [
        "",
        "## Error taxonomy (K-3)",
        "",
        f"Failed items (heuristic): **{total_failures}** / {len(items)}",
        "",
        "| Category | Label | Count | Rate | Recommended action | Target dataset |",
        "|----------|-------|-------|------|--------------------|----------------|",
    ]
    for category_id, count in counts.most_common():
        meta = TAXONOMY_BY_ID.get(category_id)
        label = meta.label if meta else category_id
        action = meta.recommended_action if meta else "—"
        target = meta.target_dataset if meta else "—"
        rate = rates.get(category_id, 0.0)
        lines.append(
            f"| `{category_id}` | {label} | {count} | {rate:.0%} | {action} | `{target}` |",
        )
    lines.extend(
        [
            "",
            "### Decide & act (K-3 step 5)",
            "",
            "1. **KB alignment** — `kb_gap_*` → правки `data/b2c/programs/` (см. task 02 iter 1).",
            "2. **Retrieval prompt** — `retrieval_no_kb_context` → search-first / fallback.",
            "3. **Behavior** — `behavior_clarify_before_search` → запрет уточнений до search.",
            "4. **Emit items (K-4)** — `make eval-analyze RUN=<run> EMIT_ITEMS=1` → `edge/error-analysis-hits/v001`.",
            "",
        ],
    )
    return lines


def render_report(run_name: str, items: list[AnalyzedItem], run_metadata: dict[str, Any]) -> str:
    langfuse_ui = resolve_langfuse_host()
    correctness_vals = [
        i.scores.answer_correctness for i in items if i.scores.answer_correctness is not None
    ]
    faithfulness_vals = [i.scores.faithfulness for i in items if i.scores.faithfulness is not None]
    relevancy_vals = [
        i.scores.answer_relevancy for i in items if i.scores.answer_relevancy is not None
    ]
    layer_counts = Counter(item.failure_layer for item in items)
    worst = items[:5]
    now = datetime.now(tz=UTC).strftime("%Y-%m-%d")

    lines = [
        f"# Analysis: {run_name}",
        "",
        f"> **Generated:** {now} · **Items:** {len(items)}",
        "",
        "## Summary",
        "",
        "| Metric | Mean |",
        "|--------|------|",
        f"| avg_answer_correctness | **{_avg(correctness_vals):.3f}** |",
        f"| avg_faithfulness | **{_avg(faithfulness_vals):.3f}** |",
        f"| avg_answer_relevancy | **{_avg(relevancy_vals):.3f}** |",
        "",
        "### Run metadata (E-9)",
        "",
        f"- config_id: `{run_metadata.get('config_id', '')}`",
        f"- dataset: `{run_metadata.get('dataset_name', '')}`",
        f"- git_sha: `{run_metadata.get('git_sha', '')}`",
        f"- model: `{run_metadata.get('model_name', '')}`",
        f"- judge: `{run_metadata.get('judge_model', '')}`",
        "",
        "## Score distribution (answer_correctness)",
        "",
        "| Bucket | Count |",
        "|--------|-------|",
    ]
    for bucket, count in _distribution(correctness_vals).items():
        lines.append(f"| {bucket} | {count} |")

    lines.extend(
        [
            "",
            "## Failure layers (all items)",
            "",
            "| Layer | Count |",
            "|-------|-------|",
        ],
    )
    for layer, count in layer_counts.most_common():
        lines.append(f"| {layer} | {count} |")

    lines.extend(render_taxonomy_section(items))
    lines.extend(["", "## Top-5 worst items", ""])
    for index, item in enumerate(worst, start=1):
        corr = item.scores.answer_correctness
        faith = item.scores.faithfulness
        rel = item.scores.answer_relevancy
        tools = ", ".join(item.tool_spans) if item.tool_spans else "—"
        exp_url = f"{langfuse_ui}/trace/{item.trace_id}"
        agent_url = f"{langfuse_ui}/trace/{item.agent_trace_id}" if item.agent_trace_id else "—"
        lines.extend(
            [
                f"### {index}. `{item.item_id}` — **{item.failure_layer}**",
                "",
                f"- **Scores:** correctness={_fmt_score(corr)}, "
                f"faithfulness={_fmt_score(faith)}, "
                f"relevancy={_fmt_score(rel)}",
                f"- **Reason:** {item.failure_reason}",
                f"- **Intent / product:** {item.intent} / `{item.product_id}` · gt={item.gt_quality}",
                f"- **Contexts:** {item.contexts_count} chunks",
                f"- **Tool spans:** {tools}",
                f"- **Experiment trace:** [{item.trace_id}]({exp_url})",
                f"- **Agent trace:** [{item.agent_trace_id or 'n/a'}]({agent_url})",
                "",
                f"**Q:** {item.message[:300]}{'…' if len(item.message) > 300 else ''}",
                "",
                f"**A:** {item.answer[:400]}{'…' if len(item.answer) > 400 else ''}",
                "",
            ],
        )

    lines.extend(
        [
            "## Recommended fixes (priority)",
            "",
            "1. **KB / dataset alignment** — items tagged `kb_gap`: update `data/b2c/programs/` or soften `expected_output` where KB lacks schedule/live facts.",
            "2. **Prompt** — items tagged `behavior`: require `search_knowledge_base` before clarifying questions.",
            "3. **Generation** — items with contexts but low faithfulness/correctness: tighten anti-hallucination in prompt, consider stronger model.",
            "4. **Retrieval** — empty contexts: enforce search tool usage in ReAct prompt.",
            "",
            "## Next step",
            "",
            "Eval-fix loop (v0.2): pick 1-2 layers with highest count, implement fix, re-run experiment, compare runs.",
            "",
        ],
    )
    return "\n".join(lines)


def analyze_run(
    langfuse: Langfuse,
    *,
    run_name: str,
    manifest_path: Path,
) -> tuple[str, dict[str, Any], list[AnalyzedItem], dict[str, Any]]:
    raw_items = fetch_run_items(langfuse, run_name)
    run_metadata = raw_items[0]["metadata"] if raw_items else {}
    manifest_index = build_manifest_index(manifest_path)
    items = analyze_items(langfuse, raw_items, manifest_index)
    report = render_report(run_name, items, run_metadata)
    return report, run_metadata, items, manifest_index


def main() -> int:
    parser = argparse.ArgumentParser(description="Analyze eval experiment run")
    parser.add_argument("--run", default="", help="Experiment run name (or suffix)")
    parser.add_argument("--out", default="reports/", help="Output directory")
    parser.add_argument("--manifest", default="", help="Dataset manifest path")
    parser.add_argument(
        "--emit-items",
        action="store_true",
        help="Emit edge/error-analysis-hits manifest from taxonomy (K-4)",
    )
    args = parser.parse_args()

    _load_env()
    try:
        host, public_key, secret_key = resolve_langfuse_keys()
    except RuntimeError as exc:
        print(f"ERROR: {exc}")
        return 1

    out_dir = Path(args.out)
    if not out_dir.is_absolute():
        out_dir = EVALS_ROOT / out_dir

    try:
        run_name = resolve_run_name(args.run, out_dir)
    except FileNotFoundError as exc:
        print(f"ERROR: {exc}")
        return 1

    manifest_path = Path(args.manifest) if args.manifest else DEFAULT_MANIFEST
    if not manifest_path.is_absolute() and args.manifest:
        manifest_path = EVALS_ROOT / manifest_path

    langfuse = Langfuse(public_key=public_key, secret_key=secret_key, host=host)
    try:
        raw_preview = fetch_run_items(langfuse, run_name)
        run_metadata = raw_preview[0]["metadata"] if raw_preview else {}
        if not args.manifest:
            manifest_path = resolve_manifest_path(run_metadata, "")
        report, _meta, items, manifest_index = analyze_run(
            langfuse,
            run_name=run_name,
            manifest_path=manifest_path,
        )
    except ValueError as exc:
        print(f"ERROR: {exc}")
        return 1

    out_path = out_dir / f"analysis-{run_name}.md"
    out_path.write_text(report, encoding="utf-8")
    print(f"analysis written: {out_path}")

    if args.emit_items:
        from emit_error_items import emit_regression_manifest

        emitted_path = emit_regression_manifest(
            analyzed_items=items,
            manifest_index=manifest_index,
            run_name=run_name,
        )
        print(f"error-analysis items written: {emitted_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
