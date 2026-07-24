"""Сравнительный отчёт single vs subagents (только docs/, русский)."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING

from homework_mentor.config import project_root

if TYPE_CHECKING:
    from homework_mentor.reports.models import RunReport

_NONE = "—"

_PROS_SINGLE = (
    "Один поток LLM — проще отладка и меньше окон на review",
    "Нет накладных расходов на handoff/brief субагентов",
    "Подходит для маленьких репозиториев и быстрых смоук-прогонов",
)

_CONS_SINGLE = (
    "На большом репо контекст родителя раздувается («одному агенту тесно»)",
    "Выше риск forced summarize/offload и потери деталей review",
    "Аспекты смешаны в одном потоке — хуже воспроизводимость разбора",
)

_PROS_SUBAGENTS = (
    "Изоляция аспектов: полные notes в FS, в parent — только summary",
    "Меньше «мутности» после CE: детали не обязаны жить в окне оркестратора",
    "Явное покрытие architecture / code_quality через handoff-контракт",
)

_CONS_SUBAGENTS = (
    "Больше LLM-вызовов (parent + reviewers) — суммарный bill обычно выше",
    "Сложнее отладка оркестрации (brief → summary → synthesis)",
    "Parent max tokens не обязан быть меньше, чем у демо-single с заниженными порогами CE",
)


def compare_modes_filename(*, stamp: str | None = None) -> str:
    value = stamp or datetime.now(tz=UTC).strftime("%Y%m%dT%H%M%SZ")
    return f"compare-modes-{value}.md"


def compare_modes_path(
    *,
    stamp: str | None = None,
    docs_dir: Path | None = None,
) -> Path:
    directory = docs_dir or (project_root() / "docs")
    return directory / compare_modes_filename(stamp=stamp)


def _fmt(value: object | None) -> str:
    if value is None or value == "":
        return _NONE
    return str(value)


def _fmt_ms(ms: int | None) -> str:
    if ms is None:
        return _NONE
    return f"{ms} мс ({ms / 1000:.2f} с)"


def _link(path: str | Path | None) -> str:
    if path is None:
        return _NONE
    name = Path(path).name
    return f"[`{name}`](./{name})"


def _assert_under_docs(path: Path, *, docs_dir: Path) -> None:
    resolved = path.resolve()
    docs_root = docs_dir.resolve()
    try:
        resolved.relative_to(docs_root)
    except ValueError as exc:
        msg = f"compare report must be written under docs/, got: {path}"
        raise ValueError(msg) from exc
    if resolved.parent.name == "logs":
        msg = f"compare report must not be written under logs/: {path}"
        raise ValueError(msg)


def _metric_insights(single: RunReport, subagents: RunReport) -> list[str]:
    """Короткие выводы по числам прогона."""
    lines: list[str] = []
    s_max, a_max = single.totals.max_parent_tokens, subagents.totals.max_parent_tokens
    if s_max or a_max:
        if s_max < a_max:
            winner = "single"
        elif a_max < s_max:
            winner = "subagents"
        else:
            winner = "равны"
        lines.append(
            f"- Max parent tokens: single={s_max}, subagents={a_max} → ниже у **{winner}**",
        )
    s_tot = single.totals.total_tokens_estimate
    a_tot = subagents.totals.total_tokens_estimate
    if s_tot or a_tot:
        if s_tot < a_tot:
            winner = "single"
        elif a_tot < s_tot:
            winner = "subagents"
        else:
            winner = "равны"
        lines.append(
            f"- Total tokens (оценка): single={s_tot}, subagents={a_tot} → ниже у **{winner}**",
        )
    s_wall, a_wall = single.timing.wall_ms, subagents.timing.wall_ms
    if s_wall or a_wall:
        if s_wall < a_wall:
            winner = "single"
        elif a_wall < s_wall:
            winner = "subagents"
        else:
            winner = "равны"
        lines.append(
            f"- Wall time: single={_fmt_ms(s_wall)}, subagents={_fmt_ms(a_wall)} "
            f"→ быстрее **{winner}**",
        )
    lines.append(
        f"- CE summarize/offload: single={single.totals.summarize_count}/"
        f"{single.totals.offload_count}, "
        f"subagents={subagents.totals.summarize_count}/{subagents.totals.offload_count}",
    )
    lines.append(
        f"- Handoffs / notes: single={single.totals.handoffs_count}/"
        f"{single.totals.notes_count}, "
        f"subagents={subagents.totals.handoffs_count}/{subagents.totals.notes_count}",
    )
    return lines


def render_compare_modes_markdown(
    *,
    single: RunReport,
    subagents: RunReport,
    single_report_path: str | Path | None = None,
    subagents_report_path: str | Path | None = None,
) -> str:
    """Собрать русскоязычный сравнительный markdown."""
    topic = single.params.topic or subagents.params.topic
    source = single.params.source_value or subagents.params.source_value
    model = single.params.model or subagents.params.model
    lines: list[str] = [
        "# Сравнение режимов проверки: single vs subagents",
        "",
        f"> Сгенерировано: {datetime.now(tz=UTC).isoformat()}  ",
        f"> Тема: {_fmt(topic)}  ",
        f"> Источник: `{_fmt(source)}`  ",
        f"> Модель: `{_fmt(model)}`",
        "",
        "---",
        "",
        "## Сводная таблица метрик",
        "",
        "| Метрика | single | subagents |",
        "|---------|--------|-----------|",
        f"| Wall time | {_fmt_ms(single.timing.wall_ms)} | {_fmt_ms(subagents.timing.wall_ms)} |",
        (
            f"| Total tokens (оценка) | {single.totals.total_tokens_estimate} | "
            f"{subagents.totals.total_tokens_estimate} |"
        ),
        (
            f"| Max parent tokens | {single.totals.max_parent_tokens} | "
            f"{subagents.totals.max_parent_tokens} |"
        ),
        (
            f"| Final parent tokens | {single.totals.final_parent_tokens} | "
            f"{subagents.totals.final_parent_tokens} |"
        ),
        (
            f"| Summarize / offload / compact | "
            f"{single.totals.summarize_count}/{single.totals.offload_count}/"
            f"{single.totals.compact_count} | "
            f"{subagents.totals.summarize_count}/{subagents.totals.offload_count}/"
            f"{subagents.totals.compact_count} |"
        ),
        (f"| Handoffs | {single.totals.handoffs_count} | {subagents.totals.handoffs_count} |"),
        f"| Notes (`review_*.md`) | {single.totals.notes_count} | {subagents.totals.notes_count} |",
        (
            f"| Reviewer tokens (сумма max окон) | {single.totals.reviewer_tokens_estimate} | "
            f"{subagents.totals.reviewer_tokens_estimate} |"
        ),
        "",
        "## Выводы по числам этого прогона",
        "",
        *_metric_insights(single, subagents),
        "",
        "## Плюсы и минусы",
        "",
        "### Режим `single`",
        "",
        "**Плюсы**",
        "",
        *[f"- {item}" for item in _PROS_SINGLE],
        "",
        "**Минусы**",
        "",
        *[f"- {item}" for item in _CONS_SINGLE],
        "",
        "### Режим `subagents`",
        "",
        "**Плюсы**",
        "",
        *[f"- {item}" for item in _PROS_SUBAGENTS],
        "",
        "**Минусы**",
        "",
        *[f"- {item}" for item in _CONS_SUBAGENTS],
        "",
        "## Исходные run-отчёты",
        "",
        f"- single: {_link(single_report_path)}",
        f"- subagents: {_link(subagents_report_path)}",
        "",
        (
            "> Сравнительный отчёт пишется **только** в `docs/`. "
            "Session summary в `logs/` — отдельно и не заменяет compare."
        ),
        "",
    ]
    return "\n".join(lines)


def write_compare_modes_report(  # noqa: PLR0913 — explicit compare inputs
    *,
    single: RunReport,
    subagents: RunReport,
    single_report_path: str | Path | None = None,
    subagents_report_path: str | Path | None = None,
    docs_dir: Path | None = None,
    path: Path | None = None,
    stamp: str | None = None,
) -> Path:
    """Записать compare markdown только под ``docs/``."""
    docs_root = docs_dir or (project_root() / "docs")
    target = path or compare_modes_path(stamp=stamp, docs_dir=docs_root)
    _assert_under_docs(target, docs_dir=docs_root)
    target.parent.mkdir(parents=True, exist_ok=True)
    body = render_compare_modes_markdown(
        single=single,
        subagents=subagents,
        single_report_path=single_report_path,
        subagents_report_path=subagents_report_path,
    )
    target.write_text(body, encoding="utf-8")
    return target
