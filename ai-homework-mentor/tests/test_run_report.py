"""S8 Task 02: Russian run report (params, context, totals, timing)."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from pydantic import SecretStr

from homework_mentor import __version__
from homework_mentor.code_fetch.models import FetchResult
from homework_mentor.config import RuntimeSettings, load_yaml_config
from homework_mentor.context.collector import ContextTraceCollector
from homework_mentor.context.models import ContextMetricEvent
from homework_mentor.orchestrator.review import ReviewRunResult
from homework_mentor.pipeline import SessionResult
from homework_mentor.reports import (
    build_run_report,
    render_run_report_markdown,
    write_run_report,
)
from homework_mentor.reviewers.collector import SubagentHandoffCollector, SubagentHandoffEvent
from homework_mentor.rubric.loader import select_rubric
from homework_mentor.submission import SourceType
from homework_mentor.submission.models import Submission
from homework_mentor.workspace import create_session

_REQUIRED_SECTIONS = (
    "## Параметры запуска",
    "## Рост контекста по шагам",
    "## Токены субагентов",
    "## Итоговые метрики",
    "## Время выполнения",
)


def _sample_result(tmp_path: Path) -> SessionResult:
    session = create_session(root=tmp_path, session_id="runrep01")
    (session.notes_dir / "review_architecture.md").write_text("# arch\n", encoding="utf-8")
    rubric = select_rubric("python-cli", session=session)
    trace = ContextTraceCollector()
    trace.events = [
        ContextMetricEvent(
            step=0,
            tokens_before=0,
            tokens_after=100,
            source="estimate",
            event_type="none",
        ),
        ContextMetricEvent(
            step=1,
            tokens_before=100,
            tokens_after=250,
            source="estimate",
            event_type="summarize",
        ),
        ContextMetricEvent(
            step=2,
            tokens_before=250,
            tokens_after=180,
            source="estimate",
            event_type="offload",
            offload_path="/notes/offload.md",
        ),
    ]
    handoffs = SubagentHandoffCollector()
    started = datetime(2026, 7, 24, 12, 0, 0, tzinfo=UTC)
    completed = datetime(2026, 7, 24, 12, 0, 2, tzinfo=UTC)
    handoffs.events.append(
        SubagentHandoffEvent(
            aspect="architecture",
            subagent_name="reviewer_architecture",
            brief="check",
            summary="A" * 40,
            note_path="/notes/review_architecture.md",
            started_at=started,
            completed_at=completed,
            max_window_tokens=1200,
            total_window_tokens_estimate=3000,
            model_calls=3,
            window_metric_source="estimate",
        ),
    )
    review = ReviewRunResult(
        reply="done",
        context_trace=trace,
        subagent_handoffs=handoffs,
        review_mode="subagents",
    )
    return SessionResult(
        kind="ok",
        submission=Submission(
            source_type=SourceType.LOCAL_PATH,
            source_value=str(tmp_path / "hw"),
            topic="python-cli",
            raw_text="Тема: python-cli",
        ),
        fetch=FetchResult(source="local", staging_dir=session.code_dir, files=["a.py"]),
        workspace=session,
        rubric=rubric,
        review=review,
        reply="done",
        review_mode="subagents",
    )


def test_render_run_report_has_russian_sections(tmp_path: Path) -> None:
    result = _sample_result(tmp_path)
    settings = RuntimeSettings(
        yaml=load_yaml_config(),
        openrouter_api_key=SecretStr("test-key"),
    )
    report = build_run_report(
        result,
        model="openrouter:test",
        verbose=True,
        wall_ms=1500,
        version=__version__,
        settings=settings,
        openrouter_api_base="https://openrouter.ai/api/v1",
    )
    body = render_run_report_markdown(report)
    for section in _REQUIRED_SECTIONS:
        assert section in body
    assert "review_mode" in body
    assert "python-cli" in body
    assert "openrouter:test" in body
    assert str(settings.yaml.agent.context.summarize_threshold_tokens) in body
    assert "| 0 |" in body
    assert "| 1 |" in body
    assert "1500 мс" in body
    assert report.totals.max_parent_tokens == 250
    assert report.totals.summarize_count == 1
    assert report.totals.offload_count == 1
    assert report.totals.handoffs_count == 1
    assert report.totals.notes_count == 1
    assert report.totals.reviewer_tokens_estimate == 1200
    assert report.totals.total_tokens_estimate == 250 + 1200
    assert len(report.reviewer_windows) == 1
    assert report.reviewer_windows[0].aspect == "architecture"
    assert report.reviewer_windows[0].max_tokens == 1200
    assert "Токены субагентов" in body
    assert "reviewer_architecture" in body
    assert "только **parent**" in body
    assert "сумма max окон" in body


def test_write_run_report_to_docs_dir(tmp_path: Path) -> None:
    result = _sample_result(tmp_path)
    docs = tmp_path / "docs"
    report = build_run_report(
        result,
        model="openrouter:test",
        verbose=False,
        wall_ms=100,
        version="0.1.0",
    )
    path = write_run_report(report, docs_dir=docs)
    assert path.is_file()
    assert path.parent == docs
    assert path.name.startswith("run-report-subagents-")
    text = path.read_text(encoding="utf-8")
    assert "## Параметры запуска" in text
    assert "## Итоговые метрики" in text


def test_build_run_report_single_mode_zero_handoffs(tmp_path: Path) -> None:
    result = _sample_result(tmp_path)
    result = SessionResult(
        kind="ok",
        submission=result.submission,
        fetch=result.fetch,
        workspace=result.workspace,
        rubric=result.rubric,
        review=ReviewRunResult(
            reply="single",
            context_trace=result.review.context_trace if result.review else ContextTraceCollector(),
            review_mode="single",
        ),
        reply="single",
        review_mode="single",
    )
    report = build_run_report(
        result,
        model="m",
        verbose=False,
        wall_ms=10,
        version="0.1.0",
    )
    assert report.params.review_mode == "single"
    assert report.totals.handoffs_count == 0
    assert report.totals.reviewer_tokens_estimate == 0
    assert report.totals.total_tokens_estimate == report.totals.max_parent_tokens
    assert report.reviewer_windows == []
    body = render_run_report_markdown(report)
    assert "Субагенты не вызывались" in body


def test_reviewer_window_metrics_fallback_to_summary_chars(tmp_path: Path) -> None:
    result = _sample_result(tmp_path)
    assert result.review is not None
    event = result.review.subagent_handoffs.events[0]
    event.max_window_tokens = None
    event.total_window_tokens_estimate = None
    event.model_calls = None
    event.window_metric_source = None
    report = build_run_report(
        result,
        model="m",
        verbose=False,
        wall_ms=10,
        version="0.1.0",
    )
    assert report.reviewer_windows[0].source == "summary_chars"
    assert report.reviewer_windows[0].max_tokens == 10  # 40 chars // 4
    assert report.totals.reviewer_tokens_estimate == 10
