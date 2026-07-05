"""Build comparison report for method A OCR engines."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
BACKEND_DIR = REPO_ROOT / "backend"
SCRIPTS_DIR = REPO_ROOT / "evals" / "scripts"
REPORTS_DIR = REPO_ROOT / "evals" / "reports"

for path in (BACKEND_DIR, SCRIPTS_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from build_multimodal_report import SEGMENT_SUFFIXES, SegmentMetrics, find_latest_run, parse_report
from run_ocr_cer import compute_cer_table, format_markdown_table


@dataclass(frozen=True)
class IndexCostSnapshot:
    config_id: str
    build_time_s: float | None
    index_size_mb: float | None
    est_cost_usd: float | None


def _load_cost_snapshot(config_id: str) -> IndexCostSnapshot:
    path = REPORTS_DIR / f"{config_id}-index-cost.json"
    if not path.exists():
        return IndexCostSnapshot(config_id, None, None, None)
    raw = json.loads(path.read_text(encoding="utf-8"))
    return IndexCostSnapshot(
        config_id=config_id,
        build_time_s=raw.get("build_time_s"),
        index_size_mb=raw.get("index_size_mb"),
        est_cost_usd=raw.get("est_cost_usd"),
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
    baseline = _segment_rows("multimodal-baseline")
    tess = _segment_rows("multimodal-a-ocr-tesseract")
    modern = _segment_rows("multimodal-a-ocr-modern")
    cost_tess = _load_cost_snapshot("multimodal-a-ocr-tesseract")
    cost_modern = _load_cost_snapshot("multimodal-a-ocr-modern")

    gold_path = REPO_ROOT / "evals" / "datasets" / "multimodal" / "ocr-gold" / "v001_2026-07-05.yaml"
    cer_rows = compute_cer_table(
        gold_path=gold_path,
        engines={
            "tesseract": REPO_ROOT / "evals" / "artifacts" / "ocr" / "tesseract",
            "modern": REPO_ROOT / "evals" / "artifacts" / "ocr" / "modern",
        },
    )
    cer_by_engine: dict[str, list[float]] = {"tesseract": [], "modern": []}
    for row in cer_rows:
        cer_by_engine[row.engine].append(row.cer)
    mean_cer = {
        engine: sum(values) / len(values) if values else float("nan")
        for engine, values in cer_by_engine.items()
    }

    lines = [
        "# Method A — OCR comparison (Tesseract vs EasyOCR)",
        "",
        "**Modern engine:** EasyOCR CPU (`ru`+`en`), Docker-first.",
        "**Gold CER:** draft — review slides 9, 10, 11 before trusting absolute numbers.",
        "",
        "## Index cost",
        "",
        "| Config | build_time_s | index_size_mb | est_cost_usd |",
        "|--------|--------------|---------------|--------------|",
        f"| multimodal-a-ocr-tesseract | {cost_tess.build_time_s} | {cost_tess.index_size_mb} | {cost_tess.est_cost_usd} |",
        f"| multimodal-a-ocr-modern | {cost_modern.build_time_s} | {cost_modern.index_size_mb} | {cost_modern.est_cost_usd} |",
        "",
        "## CER (~10 gold slides)",
        "",
        format_markdown_table(cer_rows),
        "",
        f"- Mean CER tesseract: **{mean_cer['tesseract']:.3f}**",
        f"- Mean CER modern (EasyOCR): **{mean_cer['modern']:.3f}**",
        "",
        "> CER may exceed 1.0 when OCR hallucinates extra characters.",
        "",
        "## Retrieval by segment (Group 1)",
        "",
        "| Segment | Baseline R@5 | Tesseract R@5 | Modern R@5 | Baseline nDCG@5 | Tesseract nDCG@5 | Modern nDCG@5 |",
        "|---------|--------------|---------------|------------|-----------------|--------------------|---------------|",
    ]

    baseline_map = {row.segment: row for row in baseline}
    tess_map = {row.segment: row for row in tess}
    modern_map = {row.segment: row for row in modern}
    for segment in SEGMENT_SUFFIXES:
        b = baseline_map[segment]
        t = tess_map[segment]
        m = modern_map[segment]
        lines.append(
            f"| {segment} | {_fmt(b.recall)} | {_fmt(t.recall)} | {_fmt(m.recall)} | "
            f"{_fmt(b.ndcg)} | {_fmt(t.ndcg)} | {_fmt(m.ndcg)} |",
        )

    s2_b = baseline_map["S2_chart"].recall or 0.0
    s2_t = tess_map["S2_chart"].recall or 0.0
    s2_m = modern_map["S2_chart"].recall or 0.0
    winner = "modern (EasyOCR)" if mean_cer["modern"] <= mean_cer["tesseract"] else "tesseract"
    retrieval_winner = "modern" if s2_m >= max(s2_b, s2_t) else "tesseract" if s2_t >= max(s2_b, s2_m) else "baseline"

    lines.extend(
        [
            "",
            "## Verdict (draft)",
            "",
            f"- **Lower CER on gold sample:** {winner}",
            f"- **Best S2_chart Recall@5:** {retrieval_winner} (baseline={s2_b:.3f}, tesseract={s2_t:.3f}, modern={s2_m:.3f})",
            "- Method A justified vs baseline when chart-value items (s2-01, s2-07, s2-08) gain recall after OCR.",
            "- Check north-star strings in artifacts: `49%`, `2028`, `50%` on slides 10/9.",
            "",
            "## Reproduce",
            "",
            "```powershell",
            ".\\make.ps1 eval-multimodal-a-ocr",
            "```",
        ],
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default=str(REPORTS_DIR / "multimodal-a-ocr-comparison.md"),
    )
    args = parser.parse_args()
    out_path = Path(args.out)
    out_path.write_text(build_comparison(), encoding="utf-8")
    print(f"wrote {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
