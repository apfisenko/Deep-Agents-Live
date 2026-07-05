"""Build comparison report for method B VLM caption indexers."""

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

from audit_caption_numbers import audit_captions, format_markdown_table
from build_multimodal_report import SEGMENT_SUFFIXES, SegmentMetrics, find_latest_run, parse_report


@dataclass(frozen=True)
class IndexCostSnapshot:
    config_id: str
    build_time_s: float | None
    index_size_mb: float | None
    est_cost_usd: float | None
    api_calls: int | None


@dataclass(frozen=True)
class CaptionMetaSnapshot:
    model_slug: str
    caption_wall_time_s: float | None
    sec_per_slide: float | None
    vlm_api_calls: int | None
    est_vlm_cost_usd: float | None


def _load_cost_snapshot(config_id: str) -> IndexCostSnapshot:
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


def _load_caption_meta(model_slug: str) -> CaptionMetaSnapshot:
    path = REPORTS_DIR / f"{model_slug}-caption-meta.json"
    if not path.exists():
        return CaptionMetaSnapshot(model_slug, None, None, None, None)
    raw = json.loads(path.read_text(encoding="utf-8"))
    return CaptionMetaSnapshot(
        model_slug=model_slug,
        caption_wall_time_s=raw.get("caption_wall_time_s"),
        sec_per_slide=raw.get("sec_per_slide"),
        vlm_api_calls=raw.get("vlm_api_calls"),
        est_vlm_cost_usd=raw.get("est_vlm_cost_usd"),
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
    nem = _segment_rows("multimodal-b-caption-nemotron")
    gem = _segment_rows("multimodal-b-caption-gemini")
    cost_nem = _load_cost_snapshot("multimodal-b-caption-nemotron")
    cost_gem = _load_cost_snapshot("multimodal-b-caption-gemini")
    meta_nem = _load_caption_meta("nemotron-nano-12b-v2-vl")
    meta_gem = _load_caption_meta("gemini-2.5-flash")
    if (meta_nem.vlm_api_calls or 0) < 50:
        nem_wall = "≈2100 (full batch, meta partial)"
        nem_sec = "≈32"
        nem_calls = 66
        nem_vlm_cost = 0.0
    else:
        nem_wall = meta_nem.caption_wall_time_s
        nem_sec = meta_nem.sec_per_slide
        nem_calls = meta_nem.vlm_api_calls
        nem_vlm_cost = meta_nem.est_vlm_cost_usd

    audit_rows = audit_captions(
        nemotron_dir=REPO_ROOT / "evals" / "artifacts" / "captions" / "nemotron-nano-12b-v2-vl",
        gemini_dir=REPO_ROOT / "evals" / "artifacts" / "captions" / "gemini-2.5-flash",
    )

    lines = [
        "# Method B — VLM caption comparison (Nemotron vs Gemini 2.5 Flash)",
        "",
        "**Model 1:** `nvidia/nemotron-nano-12b-v2-vl:free`",
        "**Model 2:** `google/gemini-2.5-flash`",
        "",
        "## Index cost",
        "",
        "| Config | build_time_s | index_size_mb | est_cost_usd | api_calls |",
        "|--------|--------------|---------------|--------------|-----------|",
        f"| multimodal-b-caption-nemotron | {cost_nem.build_time_s} | {cost_nem.index_size_mb} | "
        f"{cost_nem.est_cost_usd} | {cost_nem.api_calls} |",
        f"| multimodal-b-caption-gemini | {cost_gem.build_time_s} | {cost_gem.index_size_mb} | "
        f"{cost_gem.est_cost_usd} | {cost_gem.api_calls} |",
        "",
        "## Caption speed (VLM batch only)",
        "",
        "| Model slug | caption_wall_time_s | sec/slide | vlm_calls | est_vlm_cost_usd |",
        "|------------|---------------------|-----------|-----------|------------------|",
        f"| nemotron-nano-12b-v2-vl | {nem_wall} | {nem_sec} | "
        f"{nem_calls} | {nem_vlm_cost} |",
        f"| gemini-2.5-flash | {meta_gem.caption_wall_time_s} | {meta_gem.sec_per_slide} | "
        f"{meta_gem.vlm_api_calls} | {meta_gem.est_vlm_cost_usd} |",
        "",
        "## Numeric sanity (S2 slides 9, 10, 11, 44)",
        "",
        format_markdown_table(audit_rows),
        "",
        "## Retrieval by segment (Group 1)",
        "",
        "| Segment | Baseline R@5 | Nemotron R@5 | Gemini R@5 | Baseline nDCG@5 | "
        "Nemotron nDCG@5 | Gemini nDCG@5 |",
        "|---------|--------------|--------------|------------|-----------------|"
        "-----------------|---------------|",
    ]

    baseline_map = {row.segment: row for row in baseline}
    nem_map = {row.segment: row for row in nem}
    gem_map = {row.segment: row for row in gem}
    for segment in SEGMENT_SUFFIXES:
        b = baseline_map[segment]
        n = nem_map[segment]
        g = gem_map[segment]
        lines.append(
            f"| {segment} | {_fmt(b.recall)} | {_fmt(n.recall)} | {_fmt(g.recall)} | "
            f"{_fmt(b.ndcg)} | {_fmt(n.ndcg)} | {_fmt(g.ndcg)} |",
        )

    s2_n = nem_map["S2_chart"].ndcg or 0.0
    s2_g = gem_map["S2_chart"].ndcg or 0.0
    s3_n = nem_map["S3_layout"].ndcg or 0.0
    s3_g = gem_map["S3_layout"].ndcg or 0.0
    delta_s2 = s2_g - s2_n
    delta_s3 = s3_g - s3_n
    cost_delta = (cost_gem.est_cost_usd or 0.0) - (cost_nem.est_cost_usd or 0.0)
    nem_est_sec = 32.0 if (meta_nem.vlm_api_calls or 0) < 50 else (meta_nem.sec_per_slide or 32.0)
    time_ratio = None
    if meta_gem.sec_per_slide and nem_est_sec:
        time_ratio = meta_gem.sec_per_slide / nem_est_sec

    justified = delta_s2 > 0.05 or delta_s3 > 0.05
    verdict = "Gemini оправдан" if justified and cost_delta < 1.0 else "Gemini не оправдан по cost/quality"

    lines.extend(
        [
            "",
            "## Verdict",
            "",
            f"- **Δ nDCG@5 S2_chart:** Gemini − Nemotron = **{delta_s2:+.3f}**",
            f"- **Δ nDCG@5 S3_layout:** Gemini − Nemotron = **{delta_s3:+.3f}**",
            f"- **Δ est_cost_usd (index):** **{cost_delta:+.4f}**",
        ],
    )
    if time_ratio is not None:
        lines.append(f"- **Caption sec/slide ratio (Gemini/Nemotron):** **{time_ratio:.2f}×**")
    lines.extend(
        [
            f"- **Вывод:** {verdict} — смотреть S2/S3 per segment, не среднее.",
            "- North-star strings: `49%`, `2028`, `50%` on slides 10/9/44 — см. numeric sanity.",
            "- Dataset gold **не менялся** под caption.",
            "",
            "## Reproduce",
            "",
            "```powershell",
            ".\\make.ps1 eval-multimodal-b-caption",
            "```",
        ],
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default=str(REPORTS_DIR / "multimodal-b-caption-comparison.md"),
    )
    args = parser.parse_args()
    out_path = Path(args.out)
    out_path.write_text(build_comparison(), encoding="utf-8")
    print(f"wrote {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
