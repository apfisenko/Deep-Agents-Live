"""Write Russian markdown run reports under docs/."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path  # noqa: TC003 — used at runtime for report paths
from typing import TYPE_CHECKING

from homework_mentor.config import project_root

if TYPE_CHECKING:
    from homework_mentor.reports.models import RunReport

_NONE = "—"


def run_report_filename(*, review_mode: str, session_id: str | None = None) -> str:
    stamp = session_id or datetime.now(tz=UTC).strftime("%Y%m%dT%H%M%SZ")
    return f"run-report-{review_mode}-{stamp}.md"


def run_report_path(
    *,
    review_mode: str,
    session_id: str | None = None,
    docs_dir: Path | None = None,
) -> Path:
    directory = docs_dir or (project_root() / "docs")
    return directory / run_report_filename(review_mode=review_mode, session_id=session_id)


def _fmt(value: object | None) -> str:
    if value is None or value == "":
        return _NONE
    if isinstance(value, bool):
        return "да" if value else "нет"
    return str(value)


def _fmt_ms(ms: int | None) -> str:
    if ms is None:
        return _NONE
    seconds = ms / 1000
    return f"{ms} мс ({seconds:.2f} с)"


def render_run_report_markdown(report: RunReport) -> str:
    """Render a full Russian markdown report body."""
    params = report.params
    totals = report.totals
    timing = report.timing
    lines: list[str] = [
        f"# Отчёт прогона — {params.review_mode}",
        "",
        f"> Статус: **{report.status}**  ",
        f"> Сессия: `{_fmt(params.session_id)}`  ",
        f"> Сгенерировано: {datetime.now(tz=UTC).isoformat()}",
        "",
        "---",
        "",
    ]
    if report.error_message:
        lines.extend(
            [
                "## Ошибка",
                "",
                "```",
                report.error_message.strip(),
                "```",
                "",
                "---",
                "",
            ],
        )
    lines.extend(
        [
            "## Параметры запуска",
            "",
            "| Параметр | Значение |",
            "|----------|----------|",
            f"| Режим проверки (`review_mode`) | `{params.review_mode}` |",
            f"| Модель | `{params.model}` |",
            f"| Тема | {_fmt(params.topic)} |",
            f"| Тип источника | {_fmt(params.source_type)} |",
            f"| Источник | `{_fmt(params.source_value)}` |",
            f"| Verbose | {_fmt(params.verbose)} |",
            f"| Версия | {_fmt(params.version)} |",
            f"| OpenRouter API base | `{_fmt(params.openrouter_api_base)}` |",
            f"| Workspace | `{_fmt(params.workspace)}` |",
            f"| Окно контекста (tokens) | {_fmt(params.window_tokens)} |",
            f"| Порог summarize | {_fmt(params.summarize_threshold_tokens)} |",
            f"| Порог offload | {_fmt(params.offload_threshold_tokens)} |",
            f"| Summarize включён | {_fmt(params.summarize_enabled)} |",
            f"| Compact включён | {_fmt(params.compact_enabled)} |",
            "",
            "## Рост контекста по шагам",
            "",
        ],
    )

    if not report.context_trace:
        lines.extend(
            [
                "_Шаги контекста не зафиксированы (нет событий CE / пустой trace)._",
                "",
                (
                    "> Шаги CE относятся только к **parent** (оркестратор). "
                    "Окна reviewer-субагентов — в следующей секции."
                ),
                "",
            ],
        )
    else:
        lines.extend(
            [
                "| Шаг | Токены до | Токены после | Δ | Источник | Событие CE | Offload |",
                "|-----|-----------|--------------|---|----------|------------|---------|",
            ],
        )
        for event in report.context_trace:
            offload = event.offload_path or _NONE
            lines.append(
                f"| {event.step} | {event.tokens_before} | {event.tokens_after} | "
                f"{event.delta:+d} | {event.source} | {event.event_type} | `{offload}` |",
            )
        lines.append("")
        lines.extend(
            [
                (
                    "> Шаги выше — только **parent** (оркестратор). Окна reviewer-субагентов "
                    "в эту таблицу не входят."
                ),
                "",
            ],
        )

    lines.extend(
        [
            "## Токены субагентов",
            "",
        ],
    )
    if not report.reviewer_windows:
        lines.extend(
            [
                "_Субагенты не вызывались (режим `single` или нет handoff)._",
                "",
            ],
        )
    else:
        lines.extend(
            [
                "| Аспект | Субагент | Max окна | Σ по вызовам | Вызовы | Wall | Источник |",
                "|--------|----------|----------|--------------|--------|------|----------|",
            ],
        )
        lines.extend(
            [
                f"| {row.aspect} | `{row.subagent_name}` | {row.max_tokens} | "
                f"{row.total_tokens_estimate} | {row.model_calls} | "
                f"{_fmt_ms(row.wall_ms)} | {row.source} |"
                for row in report.reviewer_windows
            ],
        )
        lines.extend(
            [
                "",
                (
                    "> Max окна — пик размера контекста reviewer; Σ по вызовам — сумма оценок "
                    "после каждого model call (не invoice OpenRouter)."
                ),
                "",
            ],
        )

    lines.extend(
        [
            "## Итоговые метрики",
            "",
            "| Метрика | Значение |",
            "|---------|----------|",
            f"| Макс. токены родителя (parent) | {totals.max_parent_tokens} |",
            f"| Финальные токены родителя | {totals.final_parent_tokens} |",
            f"| Оценка токенов reviewers (сумма max окон) | {totals.reviewer_tokens_estimate} |",
            f"| **Всего токенов (оценка)** | **{totals.total_tokens_estimate}** |",
            f"| Summarize | {totals.summarize_count} |",
            f"| Offload | {totals.offload_count} |",
            f"| Compact | {totals.compact_count} |",
            f"| Handoffs субагентов | {totals.handoffs_count} |",
            f"| Файлов notes (`review_*.md`) | {totals.notes_count} |",
            "",
            (
                "> **Всего токенов (оценка)** = макс. parent + сумма max окон reviewers. "
                "Шаги CE — только parent; окна reviewers — в секции выше."
            ),
            "",
            "## Время выполнения",
            "",
            "| Метрика | Значение |",
            "|---------|----------|",
            f"| Wall time (вся сессия) | {_fmt_ms(timing.wall_ms)} |",
            f"| Сумма длительностей handoff | {_fmt_ms(timing.handoffs_ms)} |",
            "",
        ],
    )
    return "\n".join(lines)


def write_run_report(
    report: RunReport,
    *,
    docs_dir: Path | None = None,
    path: Path | None = None,
) -> Path:
    """Persist markdown report under ``docs/``; return written path."""
    target = path or run_report_path(
        review_mode=report.params.review_mode,
        session_id=report.params.session_id,
        docs_dir=docs_dir,
    )
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render_run_report_markdown(report), encoding="utf-8")
    return target
