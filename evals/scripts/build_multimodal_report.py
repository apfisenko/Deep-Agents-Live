"""Build multimodal segment report from local txt runs."""

from __future__ import annotations

import argparse
import re
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

from env_loader import load_repo_env
from multimodal_config import MultimodalEvalConfig

SEGMENT_SUFFIXES: dict[str, str] = {
    "S1_text": "multimodal-s1-text",
    "S2_chart": "multimodal-s2-chart",
    "S3_layout": "multimodal-s3-layout",
    "S4_multi": "multimodal-s4-multi",
    "S5_unanswerable": "multimodal-s5-unanswerable",
}

METRIC_PATTERNS: dict[str, re.Pattern[str]] = {
    "gold_page_recall_at_5": re.compile(r"avg_gold_page_recall_at_5:\s*([0-9.]+)"),
    "ndcg_at_5": re.compile(r"avg_ndcg_at_5:\s*([0-9.]+)"),
    "mrr": re.compile(r"avg_mrr:\s*([0-9.]+)"),
    "gold_page_set_recall_at_5": re.compile(r"avg_gold_page_set_recall_at_5:\s*([0-9.]+)"),
    "unanswerable_refusal_rate": re.compile(r"avg_unanswerable_refusal_rate:\s*([0-9.]+)"),
}


@dataclass(frozen=True)
class SegmentMetrics:
    segment: str
    run_name: str
    recall: float | None
    ndcg: float | None
    mrr: float | None
    set_recall: float | None
    refusal: float | None


def parse_report(path: Path) -> SegmentMetrics:
    text = path.read_text(encoding="utf-8")
    segment = "unknown"
    for seg, suffix in SEGMENT_SUFFIXES.items():
        if suffix in path.name:
            segment = seg
            break

    parsed: dict[str, float | None] = {}
    for key, pattern in METRIC_PATTERNS.items():
        match = pattern.search(text)
        parsed[key] = float(match.group(1)) if match else None

    return SegmentMetrics(
        segment=segment,
        run_name=path.name,
        recall=parsed.get("gold_page_recall_at_5"),
        ndcg=parsed.get("ndcg_at_5"),
        mrr=parsed.get("mrr"),
        set_recall=parsed.get("gold_page_set_recall_at_5"),
        refusal=parsed.get("unanswerable_refusal_rate"),
    )


def find_latest_run(config_id: str, slug_suffix: str) -> Path | None:
    pattern = f"{config_id}--{slug_suffix}--*.txt"
    matches = sorted(REPORTS_DIR.glob(pattern), key=lambda p: p.stat().st_mtime)
    return matches[-1] if matches else None


def build_markdown(cfg: MultimodalEvalConfig) -> str:
    rows: list[SegmentMetrics] = []
    for segment, suffix in SEGMENT_SUFFIXES.items():
        report = find_latest_run(cfg.config_id, suffix)
        if report is None:
            rows.append(
                SegmentMetrics(segment, "—", None, None, None, None, None),
            )
        else:
            rows.append(parse_report(report))

    lines = [
        f"# Multimodal eval — segment report ({cfg.config_id})",
        "",
        f"**Config:** `{cfg.config_id}` · **Method:** `{cfg.indexer.method}`",
        f"**Corpus:** `{cfg.indexer.corpus_dir}`",
        f"**Collection:** `{cfg.vector_db.collection}` · **Embed:** `{cfg.vector_db.embedding_model}`",
        "",
        "## Group 1 — Retrieval (per segment, не усреднять)",
        "",
        "| Сегмент | Recall@5 | nDCG@5 | MRR | Set-recall@5 (S4) | Refusal (S5) |",
        "|---------|----------|--------|-----|-------------------|--------------|",
    ]
    for row in rows:
        def fmt(v: float | None) -> str:
            return f"{v:.3f}" if v is not None else "—"

        lines.append(
            f"| {row.segment} | {fmt(row.recall)} | {fmt(row.ndcg)} | {fmt(row.mrr)} | "
            f"{fmt(row.set_recall)} | {fmt(row.refusal)} |",
        )

    if cfg.config_id == "multimodal-baseline":
        lines.extend(
            [
                "",
                "## Вывод «боль» baseline",
                "",
            ],
        )
        for row in rows:
            if row.segment == "S1_text" and row.recall is not None:
                lines.append(
                    f"- **S1_text** Recall@5={row.recall:.3f} — заголовки из notes частично матчат, "
                    "но большинство текстовых фактов (URL, цифры) не в naive corpus.",
                )
            if row.segment == "S2_chart" and row.recall is not None:
                lines.append(
                    f"- **S2_chart** Recall@5={row.recall:.3f} — числа на барах/осях отсутствуют; "
                    "retrieval цепляется за семантику заголовков, не за chart values.",
                )
                lines.extend(
                    [
                        "  - **s2-01** (gold 10, 49% Support): R@5=0 — нет bar values в corpus.",
                        "  - **s2-07** (gold 9, 2028): R@5=0 — нет точек кривой.",
                        "  - **s2-08** (gold 9, ~50% Google): R@5=0 — нет chart numbers.",
                    ],
                )
            if row.segment == "S3_layout" and row.recall is not None:
                lines.append(
                    f"- **S3_layout** Recall@5={row.recall:.3f} — layout-вопросы частично резолвятся "
                    "по title/slide-number; без OCR стрелки/pipeline не восстановить.",
                )
            if row.segment == "S4_multi" and row.set_recall is not None:
                lines.append(
                    f"- **S4_multi** set-recall@5={row.set_recall:.3f} — multi-page: редко все gold_pages в top-5.",
                )
            if row.segment == "S5_unanswerable":
                lines.append(
                    "- **S5** — retrieval-метрики не применяются; "
                    "`unanswerable_refusal_rate` только в generation (`--with-generation`).",
                )

    lines.extend(
        [
            "",
            "## Group 2 — Ingestion-quality (задачи 04/07)",
            "",
            "- **CER** — метод A, ~10 слайдов.",
            "- **TEDS** — табличные слайды 10/11, метод D.",
            "",
            "## Group 3 — Generation (опционально)",
            "",
            "- `answer_correctness`, `faithfulness` — при `--with-generation` через agent+judge.",
            "- **S5:** `unanswerable_refusal_rate` — поведенческий отказ, не nDCG.",
            "",
            "## Воспроизведение",
            "",
            "```powershell",
            ".\\make.ps1 eval-multimodal CONFIG=evals/configs/multimodal-baseline.yaml",
            "```",
            "",
            "```bash",
            "make eval-multimodal CONFIG=evals/configs/multimodal-baseline.yaml",
            "```",
        ],
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        default=str(REPO_ROOT / "evals" / "configs" / "multimodal-baseline.yaml"),
    )
    parser.add_argument(
        "--out",
        default="",
        help="Output markdown path (default: evals/reports/<config_id>.md)",
    )
    args = parser.parse_args()
    load_repo_env()
    cfg = MultimodalEvalConfig.from_yaml_path(Path(args.config))
    out_path = Path(args.out) if args.out else REPORTS_DIR / f"{cfg.config_id}.md"
    out_path.write_text(build_markdown(cfg), encoding="utf-8")
    print(f"wrote {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
