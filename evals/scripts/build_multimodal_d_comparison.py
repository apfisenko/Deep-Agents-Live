"""Build comparison report for method D Jina multivector vs B/C + cost axis."""

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
    is_multivector: bool | None


def _load_cost(config_id: str) -> IndexCostSnapshot:
    path = REPORTS_DIR / f"{config_id}-index-cost.json"
    if not path.exists():
        return IndexCostSnapshot(config_id, None, None, None, None, None)
    raw = json.loads(path.read_text(encoding="utf-8"))
    return IndexCostSnapshot(
        config_id=config_id,
        build_time_s=raw.get("build_time_s"),
        index_size_mb=raw.get("index_size_mb"),
        est_cost_usd=raw.get("est_cost_usd"),
        api_calls=raw.get("api_calls"),
        is_multivector=raw.get("is_multivector"),
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


def _load_teds_section() -> str:
    path = REPORTS_DIR / "multimodal-teds.md"
    if path.exists():
        return path.read_text(encoding="utf-8")
    return "## TEDS\n\n_(run `make run-teds-eval` first)_\n"


def build_comparison() -> str:
    d_rows = _segment_rows("multimodal-d-jina-multivector")
    b_rows = _segment_rows("multimodal-b-caption-gemini")
    c_rows = _segment_rows("multimodal-c-unified")
    cost_d = _load_cost("multimodal-d-jina-multivector")
    cost_b = _load_cost("multimodal-b-caption-gemini")
    cost_c = _load_cost("multimodal-c-unified")
    cost_base = _load_cost("multimodal-baseline")

    d_map = {row.segment: row for row in d_rows}
    b_map = {row.segment: row for row in b_rows}
    c_map = {row.segment: row for row in c_rows}

    size_ratio = None
    if cost_d.index_size_mb and cost_b.index_size_mb:
        size_ratio = cost_d.index_size_mb / cost_b.index_size_mb

    lines = [
        "# Method D — Jina v4 multivector vs B/C",
        "",
        "**Model D:** `jina-embeddings-v4` (multivector, Qdrant MAX_SIM)",
        "",
        "## Index cost (ось цены multivector)",
        "",
        "| Config | index_size_mb | build_time_s | est_cost_usd | is_multivector |",
        "|--------|---------------|--------------|--------------|----------------|",
        f"| multimodal-baseline | {cost_base.index_size_mb} | {cost_base.build_time_s} | "
        f"{cost_base.est_cost_usd} | {cost_base.is_multivector} |",
        f"| multimodal-b-caption-gemini | {cost_b.index_size_mb} | {cost_b.build_time_s} | "
        f"{cost_b.est_cost_usd} | {cost_b.is_multivector} |",
        f"| multimodal-c-unified | {cost_c.index_size_mb} | {cost_c.build_time_s} | "
        f"{cost_c.est_cost_usd} | {cost_c.is_multivector} |",
        f"| **multimodal-d-jina** | **{cost_d.index_size_mb}** | **{cost_d.build_time_s}** | "
        f"**{cost_d.est_cost_usd}** | **{cost_d.is_multivector}** |",
        "",
    ]
    if size_ratio is not None:
        lines.append(f"- **D / B index_size_mb ratio:** **{size_ratio:.1f}×**")
        lines.append("")

    lines.extend(
        [
            _load_teds_section().rstrip(),
            "",
            "## Retrieval by segment (Group 1)",
            "",
            "| Segment | B nDCG@5 | C nDCG@5 | D nDCG@5 | Δ(D−B) | Δ(D−C) |",
            "|---------|----------|----------|----------|--------|--------|",
        ],
    )

    s3_delta_b = 0.0
    s4_delta_b = 0.0
    for segment in SEGMENT_SUFFIXES:
        b = b_map[segment]
        c = c_map[segment]
        d = d_map[segment]
        delta_b = (d.ndcg or 0.0) - (b.ndcg or 0.0) if d.ndcg is not None and b.ndcg is not None else 0.0
        delta_c = (d.ndcg or 0.0) - (c.ndcg or 0.0) if d.ndcg is not None and c.ndcg is not None else 0.0
        if segment == "S3_layout":
            s3_delta_b = delta_b
        if segment == "S4_multi":
            s4_delta_b = delta_b
        lines.append(
            f"| {segment} | {_fmt(b.ndcg)} | {_fmt(c.ndcg)} | {_fmt(d.ndcg)} | "
            f"{delta_b:+.3f} | {delta_c:+.3f} |",
        )

    justified = (s3_delta_b > 0.05 or s4_delta_b > 0.05) and (size_ratio or 1) < 50
    if justified:
        verdict = "Multivector **может быть оправдан** на S3/S4 — сверить с index_size_mb ratio."
    else:
        verdict = (
            "Multivector **не оправдан по умолчанию** — прирост не перекрывает "
            "index_size_mb / build cost vs B/C."
        )

    lines.extend(
        [
            "",
            "## Verdict (antihype)",
            "",
            f"- Δ nDCG@5 S3_layout (D−B): **{s3_delta_b:+.3f}**",
            f"- Δ nDCG@5 S4_multi (D−B): **{s4_delta_b:+.3f}**",
            f"- **Вывод:** {verdict}",
            "",
            "## Reproduce",
            "",
            "```powershell",
            ".\\make.ps1 eval-multimodal-d-jina",
            "```",
        ],
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default=str(REPORTS_DIR / "multimodal-d-jina-comparison.md"),
    )
    args = parser.parse_args()
    out_path = Path(args.out)
    out_path.write_text(build_comparison(), encoding="utf-8")
    print(f"wrote {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
