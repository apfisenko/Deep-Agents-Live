"""Build graphrag-final.md with decision log from eval report txt files."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
REPORTS_DIR = REPO_ROOT / "evals" / "reports"
SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from build_graphrag_baseline_report import (  # noqa: E402
    RunMetrics,
    fmt,
    load_segment_metrics,
    pick_failure_examples,
)

BASELINE_ID = "graphrag-baseline"
V001_ID = "graphrag-v001"
FINAL_ID = "graphrag-final"


def segment_row(metrics: dict[str, RunMetrics]) -> tuple[float | None, ...]:
    sh = metrics["single-hop"]
    mh = metrics["multi-hop"]
    gl = metrics["global"]
    return (
        sh.answer_correctness,
        sh.entity_recall,
        sh.faithfulness,
        mh.answer_correctness,
        mh.entity_recall,
        mh.faithfulness,
        gl.answer_correctness,
        gl.entity_recall,
        gl.faithfulness,
    )


def delta(final: float | None, base: float | None) -> str:
    if final is None or base is None:
        return "—"
    return f"{final - base:+.3f}"


def build_markdown(
    *,
    final_metrics: dict[str, RunMetrics],
    baseline_metrics: dict[str, RunMetrics],
    v001_metrics: dict[str, RunMetrics],
    failure_examples: list,
) -> str:
    fb = segment_row(final_metrics)
    bb = segment_row(baseline_metrics)
    v1 = segment_row(v001_metrics)

    lines = [
        "# GraphRAG final — agent routing (task 08)",
        "",
        f"> **Config:** `{FINAL_ID}` · routing: search_vector / search_graph / "
        f"search_global / search_text2cypher",
        f"> **Baseline:** `{BASELINE_ID}` · **Intermediate:** `{V001_ID}` (hybrid RRF)",
        "",
        "## Прогоны",
        "",
        "| Сегмент | Run |",
        "|---------|-----|",
    ]
    for segment in ("single-hop", "multi-hop", "global"):
        run = final_metrics[segment].run_name
        lines.append(f"| {segment} | `{run}` |")

    lines.extend(
        [
            "",
            "## Сравнение по сегментам",
            "",
            "| Mode | sh·corr | sh·ent@5 | sh·faith | mh·corr | mh·ent@5 | mh·faith | "
            "gl·corr | gl·ent@5 | gl·faith |",
            "|------|--------:|---------:|---------:|--------:|---------:|---------:|"
            "--------:|---------:|---------:|",
            (
                f"| qdrant_hybrid (baseline) | {fmt(bb[0])} | {fmt(bb[1])} | {fmt(bb[2])} | "
                f"{fmt(bb[3])} | {fmt(bb[4])} | {fmt(bb[5])} | {fmt(bb[6])} | {fmt(bb[7])} | "
                f"{fmt(bb[8])} |"
            ),
            (
                f"| graph_hybrid (v001) | {fmt(v1[0])} | {fmt(v1[1])} | {fmt(v1[2])} | "
                f"{fmt(v1[3])} | {fmt(v1[4])} | {fmt(v1[5])} | {fmt(v1[6])} | {fmt(v1[7])} | "
                f"{fmt(v1[8])} |"
            ),
            (
                f"| **agent_router (final)** | **{fmt(fb[0])}** | **{fmt(fb[1])}** | "
                f"**{fmt(fb[2])}** | **{fmt(fb[3])}** | **{fmt(fb[4])}** | "
                f"**{fmt(fb[5])}** | **{fmt(fb[6])}** | **{fmt(fb[7])}** | "
                f"**{fmt(fb[8])}** |"
            ),
            (
                f"| Δ final − baseline | {delta(fb[0], bb[0])} | {delta(fb[1], bb[1])} | "
                f"{delta(fb[2], bb[2])} | {delta(fb[3], bb[3])} | {delta(fb[4], bb[4])} | "
                f"{delta(fb[5], bb[5])} | {delta(fb[6], bb[6])} | {delta(fb[7], bb[7])} | "
                f"{delta(fb[8], bb[8])} |"
            ),
            "",
            "## Decision log",
            "",
            "### Single-hop",
            "",
            _segment_decision(
                segment="single-hop",
                final=final_metrics["single-hop"],
                baseline=baseline_metrics["single-hop"],
                v001=v001_metrics["single-hop"],
                helped="search_vector без graph/global — убирает шум hybrid RRF на локальных фактах.",
                cost="Доп. шаг классификации tool; latency ≈ vector-only + один ReAct hop.",
            ),
            "",
            "### Multi-hop",
            "",
            _segment_decision(
                segment="multi-hop",
                final=final_metrics["multi-hop"],
                baseline=baseline_metrics["multi-hop"],
                v001=v001_metrics["multi-hop"],
                helped="search_graph подтягивает COVERS / RECOMMENDED_BEFORE / REQUIRES → entity@5.",
                cost="Neo4j + Qdrant anchor; faithfulness может просесть при длинном контексте.",
            ),
            "",
            "### Global",
            "",
            _segment_decision(
                segment="global",
                final=final_metrics["global"],
                baseline=baseline_metrics["global"],
                v001=v001_metrics["global"],
                helped="search_global для обзоров; search_text2cypher для gl-04 (pricing COUNT/SUM).",
                cost="text2cypher + LLM Cypher generation; выше latency на числовых items.",
            ),
            "",
            "### Routing observability (representative items)",
            "",
            "| Item | Expected tool | Segment |",
            "|------|---------------|---------|",
            "| graphrag-sh-01 | search_vector | single-hop |",
            "| graphrag-mh-10 | search_graph | multi-hop |",
            "| graphrag-gl-01 | search_global | global |",
            "| graphrag-gl-04 | search_text2cypher | global |",
            "",
            "Проверка: Langfuse traces → tool_call name на каждом item.",
            "",
            "## Провальные примеры (final run)",
            "",
        ],
    )

    if not failure_examples:
        lines.append("_Нет items с correctness < 0.40 в multi/global._")
    else:
        for idx, example in enumerate(failure_examples, start=1):
            lines.extend(
                [
                    f"### {idx}. `{example.item_id}` ({example.segment})",
                    "",
                    f"**Вопрос:** {example.question}",
                    "",
                    f"- answer_correctness={example.correctness:.3f}, "
                    f"entity@5={example.entity_recall:.3f}, "
                    f"faithfulness={example.faithfulness:.3f}",
                    "",
                ],
            )

    lines.extend(
        [
            "## Воспроизведение",
            "",
            "```powershell",
            ".\\make.ps1 up",
            ".\\make.ps1 graph-index",
            ".\\make.ps1 dev-backend",
            "$env:CONFIG='evals/configs/graphrag-final.yaml'",
            "$env:DATASET='all'",
            ".\\make.ps1 eval-experiment",
            "uv run python evals/scripts/build_graphrag_final_report.py",
            "```",
            "",
        ],
    )
    return "\n".join(lines)


def _segment_decision(
    *,
    segment: str,
    final: RunMetrics,
    baseline: RunMetrics,
    v001: RunMetrics,
    helped: str,
    cost: str,
) -> str:
    corr_delta = delta(final.answer_correctness, baseline.answer_correctness)
    ent_delta = delta(final.entity_recall, baseline.entity_recall)
    return (
        f"- **Что помогло:** {helped}\n"
        f"- **Метрики:** correctness {fmt(final.answer_correctness)} "
        f"(Δ baseline {corr_delta}), entity@5 {fmt(final.entity_recall)} "
        f"(Δ baseline {ent_delta})\n"
        f"- **vs v001 hybrid:** correctness {fmt(v001.answer_correctness)} → "
        f"{fmt(final.answer_correctness)}\n"
        f"- **Цена:** {cost}"
    )


def patch_baseline_md(agent_row: tuple[float | None, ...]) -> None:
    baseline_path = REPORTS_DIR / "graphrag-baseline.md"
    if not baseline_path.exists():
        return
    text = baseline_path.read_text(encoding="utf-8")
    agent_line = (
        f"| agent_router | {fmt(agent_row[0])} | {fmt(agent_row[1])} | {fmt(agent_row[2])} | "
        f"{fmt(agent_row[3])} | {fmt(agent_row[4])} | {fmt(agent_row[5])} | "
        f"{fmt(agent_row[6])} | {fmt(agent_row[7])} | {fmt(agent_row[8])} |"
    )
    if "| agent_router |" in text:
        lines = text.splitlines()
        for i, line in enumerate(lines):
            if line.startswith("| agent_router |"):
                lines[i] = agent_line
                break
        baseline_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"updated agent_router row in {baseline_path}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build graphrag-final.md from eval reports")
    parser.add_argument("--config-id", default=FINAL_ID)
    parser.add_argument(
        "--out",
        default=str(REPORTS_DIR / "graphrag-final.md"),
    )
    args = parser.parse_args()

    final_metrics, final_items = load_segment_metrics(args.config_id)
    baseline_metrics, _ = load_segment_metrics(BASELINE_ID)
    v001_metrics, _ = load_segment_metrics(V001_ID)

    missing = [s for s, m in final_metrics.items() if m.answer_correctness is None]
    if missing:
        print(f"warn: no reports for segments: {missing}", file=sys.stderr)

    markdown = build_markdown(
        final_metrics=final_metrics,
        baseline_metrics=baseline_metrics,
        v001_metrics=v001_metrics,
        failure_examples=pick_failure_examples(final_items),
    )
    out_path = Path(args.out)
    out_path.write_text(markdown, encoding="utf-8")
    print(f"wrote {out_path}")

    patch_baseline_md(segment_row(final_metrics))
    return 0


if __name__ == "__main__":
    sys.exit(main())
