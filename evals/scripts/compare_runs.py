"""Compare two experiment runs — run-level deltas and item regressions (E-16, E-18)."""

from __future__ import annotations

import argparse
import os
import re
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from langfuse import Langfuse

REPO_ROOT = Path(__file__).resolve().parents[2]
EVALS_ROOT = REPO_ROOT / "evals"
DEFAULT_MANIFEST = EVALS_ROOT / "datasets" / "e2e" / "e2e-qa" / "v001_2026-06-15.yaml"

if str(EVALS_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(EVALS_ROOT / "scripts"))

from analyze_run import fetch_run_items
from env_loader import load_repo_env, resolve_langfuse_keys

RUN_LEVEL_METRICS = (
    "avg_answer_correctness",
    "avg_faithfulness",
    "avg_answer_relevancy",
    "error_rate",
)
ITEM_METRICS = ("answer_correctness", "faithfulness", "answer_relevancy")
GUARD_THRESHOLDS = {
    "avg_faithfulness": 0.85,
    "avg_answer_relevancy": 0.80,
    "error_rate": 0.05,
}
MAIN_THRESHOLD = 0.75


def _load_env() -> None:
    load_repo_env()


def _normalize_run_name(run_arg: str) -> str:
    return run_arg.removesuffix(".txt").removesuffix(".json")


def _parse_txt_report(path: Path) -> dict[str, float]:
    text = path.read_text(encoding="utf-8")
    scores: dict[str, float] = {}
    for line in text.splitlines():
        match = re.match(r"\s*•\s+([\w_]+):\s+([\d.]+)", line)
        if match:
            scores[match.group(1)] = float(match.group(2))
    for metric in RUN_LEVEL_METRICS:
        if metric not in scores and metric.removeprefix("avg_") in scores:
            scores[metric] = scores[metric.removeprefix("avg_")]
    return scores


def _resolve_report_path(run_name: str, reports_dir: Path) -> Path:
    for suffix in (".txt", ".json"):
        path = reports_dir / f"{run_name}{suffix}"
        if path.exists():
            return path
    msg = f"Report not found for run '{run_name}' in {reports_dir}"
    raise FileNotFoundError(msg)


def _item_score_map(raw_items: list[dict[str, Any]]) -> dict[str, dict[str, float | None]]:
    by_id: dict[str, dict[str, float | None]] = {}
    for raw in raw_items:
        item_id = str((raw.get("metadata") or {}).get("item_id", "unknown"))
        scores = raw["scores"]
        by_id[item_id] = {
            "answer_correctness": scores.answer_correctness,
            "faithfulness": scores.faithfulness,
            "answer_relevancy": scores.answer_relevancy,
        }
    return by_id


def _fmt_delta(a: float | None, b: float | None) -> str:
    if a is None or b is None:
        return "n/a"
    delta = b - a
    sign = "+" if delta >= 0 else ""
    return f"{sign}{delta:.3f}"


def _guard_ok(metric: str, value: float | None) -> bool | None:
    if value is None:
        return None
    threshold = GUARD_THRESHOLDS.get(metric)
    if threshold is None:
        return None
    if metric == "error_rate":
        return value <= threshold
    return value >= threshold


def _verdict(
    *,
    main_a: float | None,
    main_b: float | None,
    guards_b: dict[str, bool | None],
) -> str:
    if main_a is None or main_b is None:
        return "inconclusive"
    if main_b <= main_a:
        return "rejected"
    if any(ok is False for ok in guards_b.values()):
        return "rejected"
    return "accepted"


def _compare_items(
    langfuse: Langfuse,
    run_a: str,
    run_b: str,
) -> tuple[dict[str, Any], dict[str, Any], list[str], list[str]]:
    raw_a = fetch_run_items(langfuse, run_a)
    raw_b = fetch_run_items(langfuse, run_b)
    meta_a = raw_a[0]["metadata"] if raw_a else {}
    meta_b = raw_b[0]["metadata"] if raw_b else {}
    version_a = meta_a.get("dataset_version", "")
    version_b = meta_b.get("dataset_version", "")
    if version_a and version_b and version_a != version_b:
        msg = f"Dataset version mismatch: {version_a} vs {version_b} (E-16)"
        raise ValueError(msg)

    items_a = _item_score_map(raw_a)
    items_b = _item_score_map(raw_b)
    item_changes: list[str] = []
    regressions: list[str] = []
    for item_id in sorted(set(items_a) | set(items_b)):
        sa = items_a.get(item_id, {})
        sb = items_b.get(item_id, {})
        ca = sa.get("answer_correctness")
        cb = sb.get("answer_correctness")
        if ca is None or cb is None:
            continue
        delta = cb - ca
        if abs(delta) >= 0.05:
            direction = "↑" if delta > 0 else "↓"
            item_changes.append(
                f"- `{item_id}`: correctness {ca:.3f} → {cb:.3f} ({direction}{abs(delta):.3f})",
            )
        if ca >= MAIN_THRESHOLD and cb < MAIN_THRESHOLD:
            regressions.append(f"- `{item_id}`: {ca:.3f} → {cb:.3f}")
    return meta_a, meta_b, item_changes, regressions


def compare_runs(
    *,
    run_a: str,
    run_b: str,
    reports_dir: Path,
    langfuse: Langfuse | None = None,
) -> str:
    path_a = _resolve_report_path(run_a, reports_dir)
    path_b = _resolve_report_path(run_b, reports_dir)
    if path_a.suffix != ".txt" or path_b.suffix != ".txt":
        msg = "Only .txt reports are supported in v0.2 compare"
        raise ValueError(msg)

    scores_a = _parse_txt_report(path_a)
    scores_b = _parse_txt_report(path_b)

    meta_a: dict[str, Any] = {}
    meta_b: dict[str, Any] = {}
    item_changes: list[str] = []
    regressions: list[str] = []

    if langfuse is not None:
        try:
            meta_a, meta_b, item_changes, regressions = _compare_items(langfuse, run_a, run_b)
        except ValueError as exc:
            print(f"WARN: item-level compare skipped: {exc}")

    now = datetime.now(tz=UTC).strftime("%Y-%m-%d")
    guards_b = {m: _guard_ok(m, scores_b.get(m)) for m in GUARD_THRESHOLDS}
    verdict = _verdict(
        main_a=scores_a.get("avg_answer_correctness"),
        main_b=scores_b.get("avg_answer_correctness"),
        guards_b=guards_b,
    )

    lines = [
        f"# Compare: {run_a} vs {run_b}",
        "",
        f"> **Generated:** {now}",
        "",
        "## Run-level metrics (E-18)",
        "",
        "| Metric | Role | Baseline (A) | Candidate (B) | Delta |",
        "|--------|------|--------------|---------------|---|",
    ]
    roles = {
        "avg_answer_correctness": "**главная**",
        "avg_faithfulness": "guard",
        "avg_answer_relevancy": "guard",
        "error_rate": "guard",
    }
    for metric in RUN_LEVEL_METRICS:
        a_val = scores_a.get(metric)
        b_val = scores_b.get(metric)
        a_str = f"{a_val:.3f}" if a_val is not None else "n/a"
        b_str = f"{b_val:.3f}" if b_val is not None else "n/a"
        lines.append(
            f"| {metric} | {roles.get(metric, '')} | {a_str} | {b_str} | {_fmt_delta(a_val, b_val)} |",
        )

    lines.extend(
        [
            "",
            f"**Вердикт (E-18):** `{verdict}` — главная выросла: "
            f"{_fmt_delta(scores_a.get('avg_answer_correctness'), scores_b.get('avg_answer_correctness'))}",
            "",
            "### Guard check (candidate)",
            "",
        ],
    )
    for metric, ok in guards_b.items():
        status = "🟢" if ok else ("🔴" if ok is False else "—")
        lines.append(f"- {metric}: {status}")

    if item_changes:
        lines.extend(["", "## Items с заметным сдвигом (|Δ correctness| ≥ 0.05)", ""])
        lines.extend(item_changes)
    if regressions:
        lines.extend(["", "## Регрессии (зелёные → красные)", ""])
        lines.extend(regressions)

    lines.extend(
        [
            "",
            "## Config diff",
            "",
            f"- A config_id: `{meta_a.get('config_id', run_a.split('--')[0])}`",
            f"- B config_id: `{meta_b.get('config_id', run_b.split('--')[0])}`",
            f"- A prompt: `{meta_a.get('prompt_name', 'n/a')}`",
            f"- B prompt: `{meta_b.get('prompt_name', 'n/a')}`",
            "",
        ],
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare eval runs")
    parser.add_argument("--a", required=True, help="Baseline run name")
    parser.add_argument("--b", required=True, help="Candidate run name")
    parser.add_argument("--out", default="reports/", help="Output directory")
    args = parser.parse_args()

    _load_env()
    out_dir = Path(args.out)
    if not out_dir.is_absolute():
        out_dir = EVALS_ROOT / out_dir

    run_a = _normalize_run_name(args.a)
    run_b = _normalize_run_name(args.b)

    langfuse: Langfuse | None = None
    try:
        host, public_key, secret_key = resolve_langfuse_keys()
        langfuse = Langfuse(public_key=public_key, secret_key=secret_key, host=host)
    except RuntimeError as exc:
        print(f"WARN: Langfuse item compare skipped: {exc}")

    try:
        report = compare_runs(run_a=run_a, run_b=run_b, reports_dir=out_dir, langfuse=langfuse)
    except (FileNotFoundError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 1

    out_path = out_dir / f"compare-{run_a}-vs-{run_b}.md"
    out_path.write_text(report, encoding="utf-8")
    print(out_path)
    print(f"compare written: {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
