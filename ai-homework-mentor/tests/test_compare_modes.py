"""S8 Task 03: compare-modes report generator (RU, docs only)."""

from __future__ import annotations

from pathlib import Path

import pytest

from homework_mentor.reports.compare import (
    render_compare_modes_markdown,
    write_compare_modes_report,
)
from homework_mentor.reports.models import (
    RunReport,
    RunReportParams,
    RunReportTiming,
    RunReportTotals,
)


def _report(mode: str, *, wall_ms: int, max_parent: int, handoffs: int) -> RunReport:
    return RunReport(
        params=RunReportParams(
            review_mode=mode,  # type: ignore[arg-type]
            model="openrouter:test",
            topic="python-cli",
            source_type="local_path",
            source_value="C:/fixtures/local_hw",
            verbose=False,
            version="0.1.0",
            session_id=f"sess-{mode}",
        ),
        context_trace=[],
        totals=RunReportTotals(
            max_parent_tokens=max_parent,
            final_parent_tokens=max_parent // 2,
            total_tokens_estimate=max_parent + handoffs * 10,
            summarize_count=1 if mode == "single" else 0,
            offload_count=1 if mode == "single" else 0,
            compact_count=0,
            handoffs_count=handoffs,
            notes_count=1 if mode == "single" else 2,
            reviewer_tokens_estimate=handoffs * 10,
        ),
        timing=RunReportTiming(wall_ms=wall_ms, handoffs_ms=handoffs * 100 or None),
        status="ok",
    )


def test_render_compare_has_table_and_pros_cons() -> None:
    single = _report("single", wall_ms=1000, max_parent=900, handoffs=0)
    subagents = _report("subagents", wall_ms=2000, max_parent=500, handoffs=2)
    body = render_compare_modes_markdown(
        single=single,
        subagents=subagents,
        single_report_path="docs/run-report-single-a.md",
        subagents_report_path="docs/run-report-subagents-b.md",
    )
    assert "## Сводная таблица метрик" in body
    assert "| Wall time |" in body
    assert "| Total tokens (оценка) |" in body
    assert "| Max parent tokens |" in body
    assert "Summarize / offload" in body
    assert "| Handoffs |" in body
    assert "| Notes" in body
    assert "Reviewer tokens (сумма max окон)" in body
    assert "## Плюсы и минусы" in body
    assert "**Плюсы**" in body
    assert "**Минусы**" in body
    assert "### Режим `single`" in body
    assert "### Режим `subagents`" in body
    assert "run-report-single-a.md" in body
    assert "только** в `docs/`" in body or "только" in body


def test_write_compare_only_under_docs(tmp_path: Path) -> None:
    docs = tmp_path / "docs"
    logs = tmp_path / "logs"
    logs.mkdir()
    single = _report("single", wall_ms=100, max_parent=100, handoffs=0)
    subagents = _report("subagents", wall_ms=200, max_parent=80, handoffs=2)
    path = write_compare_modes_report(
        single=single,
        subagents=subagents,
        docs_dir=docs,
        stamp="20260724T000000Z",
    )
    assert path.is_file()
    assert path.parent == docs
    assert path.name == "compare-modes-20260724T000000Z.md"
    with pytest.raises(ValueError, match="docs"):
        write_compare_modes_report(
            single=single,
            subagents=subagents,
            docs_dir=docs,
            path=logs / "compare-modes-bad.md",
        )
