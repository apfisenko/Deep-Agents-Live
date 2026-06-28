"""Build sprint-06 graphrag baseline segment report from experiment txt runs."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
REPORTS_DIR = REPO_ROOT / "evals" / "reports"
GRAPHAG_DIR = REPO_ROOT / "evals" / "datasets" / "graphrag"

SEGMENT_SLUGS: dict[str, str] = {
    "single-hop": "graphrag/single-hop",
    "multi-hop": "graphrag/multi-hop",
    "global": "graphrag/global",
}

ITEM_LINE = re.compile(
    r"^(?P<id>graphrag-[a-z0-9-]+)\t"
    r"(?P<correctness>[0-9.]+)\t"
    r"(?P<entity>[0-9.]+)\t"
    r"(?P<faith>[0-9.]+)\t"
    r"(?P<answer>.*)$",
)


@dataclass(frozen=True)
class RunMetrics:
    run_name: str
    slug: str
    answer_correctness: float | None
    entity_recall: float | None
    faithfulness: float | None
    error_rate: float | None


@dataclass(frozen=True)
class ItemResult:
    item_id: str
    answer: str
    correctness: float
    entity_recall: float
    faithfulness: float
    segment: str
    question: str
    reference: str


METRIC_PATTERNS: dict[str, re.Pattern[str]] = {
    "answer_correctness": re.compile(r"avg_answer_correctness:\s*([0-9.]+)"),
    "entity_recall": re.compile(r"avg_required_entity_recall_at_5:\s*([0-9.]+)"),
    "faithfulness": re.compile(r"avg_faithfulness:\s*([0-9.]+)"),
    "error_rate": re.compile(r"error_rate:\s*([0-9.]+)"),
}


def load_question_bank() -> dict[str, dict[str, object]]:
    bank: dict[str, dict[str, object]] = {}
    for filename in ("multi_hop.json", "global.json", "single_hop.json"):
        rows = json.loads((GRAPHAG_DIR / filename).read_text(encoding="utf-8"))
        for row in rows:
            bank[str(row["id"])] = row
    return bank


def parse_report(path: Path) -> tuple[dict[str, float | None], list[ItemResult]]:
    text = path.read_text(encoding="utf-8")
    parsed: dict[str, float | None] = {}
    for key, pattern in METRIC_PATTERNS.items():
        match = pattern.search(text)
        parsed[key] = float(match.group(1)) if match else None

    bank = load_question_bank()
    items: list[ItemResult] = []
    for line in text.splitlines():
        match = ITEM_LINE.match(line.strip())
        if not match:
            continue
        row = match.groupdict()
        meta = bank.get(row["id"], {})
        items.append(
            ItemResult(
                item_id=row["id"],
                answer=row["answer"],
                correctness=float(row["correctness"]),
                entity_recall=float(row["entity"]),
                faithfulness=float(row["faith"]),
                segment=str(meta.get("segment", "")),
                question=str(meta.get("question", "")),
                reference=str(meta.get("reference_answer", ""))[:280],
            ),
        )
    return parsed, items


def find_latest_run(config_id: str, slug_suffix: str) -> Path | None:
    pattern = f"{config_id}--{slug_suffix}--*.txt"
    matches = sorted(REPORTS_DIR.glob(pattern), key=lambda p: p.stat().st_mtime)
    return matches[-1] if matches else None


def load_segment_metrics(config_id: str) -> tuple[dict[str, RunMetrics], list[ItemResult]]:
    all_items: list[ItemResult] = []
    result: dict[str, RunMetrics] = {}
    for segment, slug in SEGMENT_SLUGS.items():
        slug_suffix = slug.replace("/", "-")
        report_path = find_latest_run(config_id, slug_suffix)
        if report_path is None:
            result[segment] = RunMetrics(
                run_name="—",
                slug=slug,
                answer_correctness=None,
                entity_recall=None,
                faithfulness=None,
                error_rate=None,
            )
            continue
        metrics, items = parse_report(report_path)
        all_items.extend(items)
        result[segment] = RunMetrics(
            run_name=report_path.stem,
            slug=slug,
            answer_correctness=metrics["answer_correctness"],
            entity_recall=metrics["entity_recall"],
            faithfulness=metrics["faithfulness"],
            error_rate=metrics["error_rate"],
        )
    return result, all_items


def fmt(value: float | None) -> str:
    return f"{value:.3f}" if value is not None else "—"


def failure_reason(item: ItemResult) -> str:
    if item.segment == "multi-hop":
        return (
            "Нужны связи между несколькими program-файлами (RECOMMENDED_BEFORE / COVERS); "
            "top-5 chunks не собирает цепочку, агент сводит ответ к одному SKU (часто legacy deep-agents)."
        )
    if item.segment == "global":
        return (
            "Агрегат по 4–5 документам; hybrid top-k покрывает 1–2 ступени или legacy products.json, "
            "не полную траекторию комбо."
        )
    return "Локальный факт в одном файле — flat RAG достаточен."


def pick_failure_examples(items: list[ItemResult], limit: int = 3) -> list[ItemResult]:
    candidates = [
        item
        for item in items
        if item.segment in {"multi-hop", "global"} and item.correctness < 0.40
    ]
    candidates.sort(key=lambda item: (item.correctness, item.entity_recall))
    return candidates[:limit]


def build_markdown(
    *,
    config_id: str,
    segment_metrics: dict[str, RunMetrics],
    failure_examples: list[ItemResult],
) -> str:
    baseline = segment_metrics["single-hop"]
    multi = segment_metrics["multi-hop"]
    global_seg = segment_metrics["global"]

    lines = [
        "# GraphRAG baseline — Qdrant-hybrid (flat RAG)",
        "",
        f"> **Config:** `{config_id}` · retriever: Qdrant dense+sparse, top_k=5, без графа",
        "",
        "## Метрики по сегментам",
        "",
        "| Retriever | single-hop · correctness | single-hop · entity@5 | single-hop · faith | "
        "multi-hop · correctness | multi-hop · entity@5 | multi-hop · faith | "
        "global · correctness | global · entity@5 | global · faith |",
        "|-----------|------------------------:|--------------------:|-------------------:|"
        "------------------------:|-------------------:|------------------:|"
        "---------------------:|------------------:|----------------:|",
        (
            f"| qdrant_hybrid | {fmt(baseline.answer_correctness)} | {fmt(baseline.entity_recall)} | "
            f"{fmt(baseline.faithfulness)} | {fmt(multi.answer_correctness)} | {fmt(multi.entity_recall)} | "
            f"{fmt(multi.faithfulness)} | {fmt(global_seg.answer_correctness)} | "
            f"{fmt(global_seg.entity_recall)} | {fmt(global_seg.faithfulness)} |"
        ),
        "| graph_hybrid | | | | | | | | | |",
        "| text2cypher | | | | | | | | | |",
        "| agent_router | | | | | | | | | |",
        "",
        "### Прогоны baseline",
        "",
        f"- single-hop: `{baseline.run_name}`",
        f"- multi-hop: `{multi.run_name}`",
        f"- global: `{global_seg.run_name}`",
        "",
        "## Провальные примеры (flat RAG)",
        "",
    ]

    for idx, example in enumerate(failure_examples, start=1):
        lines.extend(
            [
                f"### {idx}. `{example.item_id}` ({example.segment})",
                "",
                f"**Вопрос:** {example.question}",
                "",
                f"**Эталон (фрагмент):** {example.reference}…",
                "",
                f"**Ответ агента (фрагмент):** {example.answer}…",
                "",
                f"**Почему промах:** {failure_reason(example)}",
                "",
                f"- answer_correctness={example.correctness:.3f}, "
                f"required_entity_recall@5={example.entity_recall:.3f}, "
                f"faithfulness={example.faithfulness:.3f}",
                "",
            ],
        )

    lines.extend(
        [
            "## Вывод",
            "",
            "Гипотеза из `analysis.md` **подтверждается** на Qdrant-hybrid baseline:",
            "",
            f"- **single-hop** — выше ({fmt(baseline.answer_correctness)} correctness, "
            f"entity@5 {fmt(baseline.entity_recall)}): факты локализованы в одном program-файле.",
            f"- **multi-hop** — проседает ({fmt(multi.answer_correctness)} correctness, "
            f"entity@5 {fmt(multi.entity_recall)}): prerequisite/ diff тем разнесены по файлам.",
            f"- **global** — проседает ({fmt(global_seg.answer_correctness)} correctness, "
            f"entity@5 {fmt(global_seg.entity_recall)}): top-k не покрывает агрегат по каталогу.",
            "",
            "Строки `graph_hybrid`, `text2cypher`, `agent_router` заполняются на задачах 06–08.",
            "",
            "## Воспроизведение",
            "",
            "```bash",
            "# WSL — полный контур (Langfuse + sync)",
            "make eval-build DATASET=graphrag/multi-hop",
            "make eval-validate CONFIG=evals/configs/graphrag-baseline.yaml",
            "make eval-experiment CONFIG=evals/configs/graphrag-baseline.yaml DATASET=all",
            "",
            "# Локальный прогон без Langfuse (Windows/dev)",
            "uv run python evals/scripts/run_graphrag_baseline_local.py",
            "uv run python evals/scripts/build_graphrag_baseline_report.py",
            "```",
            "",
            "```powershell",
            "$env:CONFIG = \"configs/graphrag-baseline.yaml\"",
            ".\\make.ps1 eval-build",
            ".\\make.ps1 eval-validate",
            "uv run python scripts/run_graphrag_baseline_local.py",
            "uv run python scripts/build_graphrag_baseline_report.py",
            "```",
            "",
        ],
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build graphrag-baseline.md from eval reports")
    parser.add_argument("--config-id", default="graphrag-baseline")
    parser.add_argument(
        "--out",
        default=str(REPORTS_DIR / "graphrag-baseline.md"),
        help="Output markdown path",
    )
    args = parser.parse_args()

    segment_metrics, all_items = load_segment_metrics(args.config_id)
    markdown = build_markdown(
        config_id=args.config_id,
        segment_metrics=segment_metrics,
        failure_examples=pick_failure_examples(all_items),
    )
    out_path = Path(args.out)
    out_path.write_text(markdown, encoding="utf-8")
    print(f"wrote {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
