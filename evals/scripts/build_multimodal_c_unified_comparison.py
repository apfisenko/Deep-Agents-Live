"""Build comparison report for method C unified embed vs B_gemini + MIRACL verdict."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
BACKEND_DIR = REPO_ROOT / "backend"
SCRIPTS_DIR = REPO_ROOT / "evals" / "scripts"
REPORTS_DIR = REPO_ROOT / "evals" / "reports"

for path in (BACKEND_DIR, SCRIPTS_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from build_multimodal_report import SEGMENT_SUFFIXES, SegmentMetrics, find_latest_run, parse_report


@dataclass(frozen=True)
class IndexCostSnapshot:
    config_id: str
    build_time_s: float | None
    index_size_mb: float | None
    est_cost_usd: float | None
    api_calls: int | None


def _load_cost(config_id: str) -> IndexCostSnapshot:
    path = REPORTS_DIR / f"{config_id}-index-cost.json"
    if not path.exists():
        return IndexCostSnapshot(config_id, None, None, None, None)
    raw = json.loads(path.read_text(encoding="utf-8"))
    return IndexCostSnapshot(
        config_id=config_id,
        build_time_s=raw.get("build_time_s"),
        index_size_mb=raw.get("index_size_mb"),
        est_cost_usd=raw.get("est_cost_usd"),
        api_calls=raw.get("api_calls"),
    )


def _segment_rows(config_id: str) -> list[SegmentMetrics]:
    rows: list[SegmentMetrics] = []
    for segment, suffix in SEGMENT_SUFFIXES.items():
        report = find_latest_run(config_id, suffix)
        if report is None:
            rows.append(SegmentMetrics(segment, "—", None, None, None, None, None))
        else:
            rows.append(parse_report(report))
    return rows


def _fmt(value: float | None) -> str:
    return f"{value:.3f}" if value is not None else "—"


def build_comparison() -> str:
    c_rows = _segment_rows("multimodal-c-unified")
    b_rows = _segment_rows("multimodal-b-caption-gemini")
    baseline = _segment_rows("multimodal-baseline")
    cost_c = _load_cost("multimodal-c-unified")
    cost_b = _load_cost("multimodal-b-caption-gemini")

    c_map = {row.segment: row for row in c_rows}
    b_map = {row.segment: row for row in b_rows}
    base_map = {row.segment: row for row in baseline}

    lines = [
        "# Method C — unified VL embed vs B (Gemini caption)",
        "",
        "**Model C:** `nvidia/llama-nemotron-embed-vl-1b-v2:free` (OpenRouter)",
        "**Reference B:** `google/gemini-2.5-flash` (best caption from task 05)",
        "",
        "## Index cost",
        "",
        "| Config | build_time_s | index_size_mb | est_cost_usd | api_calls |",
        "|--------|--------------|---------------|--------------|-----------|",
        f"| multimodal-c-unified | {cost_c.build_time_s} | {cost_c.index_size_mb} | "
        f"{cost_c.est_cost_usd} | {cost_c.api_calls} |",
        f"| multimodal-b-caption-gemini | {cost_b.build_time_s} | {cost_b.index_size_mb} | "
        f"{cost_b.est_cost_usd} | {cost_b.api_calls} |",
        "",
        "## Retrieval by segment (Group 1)",
        "",
        "| Segment | Baseline nDCG@5 | B_gemini nDCG@5 | C nDCG@5 | Δ(C−B) | C R@5 | B R@5 |",
        "|---------|-----------------|-----------------|----------|--------|-------|-------|",
    ]

    deltas: dict[str, float] = {}
    for segment in SEGMENT_SUFFIXES:
        b = b_map[segment]
        c = c_map[segment]
        base = base_map[segment]
        delta = (c.ndcg or 0.0) - (b.ndcg or 0.0) if c.ndcg is not None and b.ndcg is not None else 0.0
        if segment != "S5_unanswerable":
            deltas[segment] = delta
        lines.append(
            f"| {segment} | {_fmt(base.ndcg)} | {_fmt(b.ndcg)} | {_fmt(c.ndcg)} | "
            f"{delta:+.3f} | {_fmt(c.recall)} | {_fmt(b.recall)} |",
        )

    s1_delta = deltas.get("S1_text", 0.0)
    s2_delta = deltas.get("S2_chart", 0.0)
    s3_delta = deltas.get("S3_layout", 0.0)
    negative_count = sum(1 for key in ("S1_text", "S2_chart", "S3_layout") if deltas.get(key, 0.0) < 0)

    if negative_count >= 2:
        miracl = (
            "**Подтверждена** для этого корпуса: unified visual embed проигрывает caption+VLM "
            "на русскоязычных text/chart сегментах (MIRACL-Vision hypothesis)."
        )
    elif s3_delta > 0 and s2_delta < 0:
        miracl = (
            "**Частично:** layout (S3) OK, chart/text (S2/S1) — caption B сильнее "
            "(типичный MIRACL-Vision trade-off)."
        )
    else:
        miracl = (
            "**Не подтверждена** на этом корпусе: C не проигрывает B на ≥2 из S1/S2/S3 — "
            "смотреть item-level north-star."
        )

    lines.extend(
        [
            "",
            "## MIRACL-Vision verdict (C vs B, Russian B2B deck)",
            "",
            f"- Δ nDCG@5 S1_text (C−B): **{s1_delta:+.3f}**",
            f"- Δ nDCG@5 S2_chart (C−B): **{s2_delta:+.3f}**",
            f"- Δ nDCG@5 S3_layout (C−B): **{s3_delta:+.3f}**",
            f"- **Вывод:** {miracl}",
            "- North-star: s2-01 (49%), s2-07 (2028), s2-08 (~50%) — см. per-item runs.",
            "",
            "## Reproduce",
            "",
            "```powershell",
            ".\\make.ps1 eval-multimodal-c-unified",
            "```",
        ],
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default=str(REPORTS_DIR / "multimodal-c-unified-comparison.md"),
    )
    args = parser.parse_args()
    out_path = Path(args.out)
    out_path.write_text(build_comparison(), encoding="utf-8")
    print(f"wrote {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
