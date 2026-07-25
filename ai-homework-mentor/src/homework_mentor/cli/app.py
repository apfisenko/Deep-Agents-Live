"""Rich CLI for AI Homework Mentor."""

from __future__ import annotations

import argparse
import logging
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from homework_mentor import __version__
from homework_mentor.cli.display import (
    render_context_compact,
    render_context_trace,
    render_current_todo,
    render_delegation_compact,
    render_feedback,
    render_rubric_panel,
    render_skills_compact,
    render_skills_panel,
    render_subagents_panel,
    render_todo_table,
    render_workspace_tree,
)
from homework_mentor.cli.session_log import SessionLogMeta, write_summary_log
from homework_mentor.code_fetch import CodeFetchError
from homework_mentor.config import (
    DEFAULT_OPENROUTER_API_BASE,
    DEFAULT_REVIEW_MODE,
    ConfigError,
    ReviewMode,
    RuntimeSettings,
    load_runtime_settings,
    load_yaml_config,
    resolve_review_mode,
)
from homework_mentor.errors import describe_exception
from homework_mentor.logging_setup import setup_logging
from homework_mentor.orchestrator import AgentError, ReviewError
from homework_mentor.pipeline import SessionResult, run_homework_session
from homework_mentor.reports import (
    build_failed_run_report,
    build_run_report,
    write_partial_review_report,
    write_review_report,
    write_run_report,
)

if TYPE_CHECKING:
    from collections.abc import Callable

    from homework_mentor.code_fetch import FetchResult
    from homework_mentor.submission import Submission

logger = logging.getLogger(__name__)

_IGNORE_PREVIEW = 8
_MANIFEST_PREVIEW = 15


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="homework-mentor",
        description="AI Homework Mentor — review modes single|subagents (S8)",
    )
    parser.add_argument(
        "-Message",
        "--message",
        dest="message",
        help="Free-text submission (may include GitHub URL and topic)",
    )
    parser.add_argument(
        "-Path",
        "--path",
        dest="path",
        help="Local directory with student code",
    )
    parser.add_argument(
        "-Mode",
        "--mode",
        dest="mode",
        choices=["single", "subagents"],
        default=None,
        help="Review mode: single agent or reviewer subagents (default: subagents)",
    )
    parser.add_argument(
        "-Verbose",
        "--verbose",
        dest="verbose",
        action="store_true",
        help="Show workspace, rubric, todo plan, and fetch details",
    )
    return parser


def resolve_cli_input(*, message: str | None, path: str | None) -> tuple[str, Path | None]:
    """Return (raw_text, explicit_path)."""
    resolved: Path | None = None
    if path is not None:
        resolved = Path(path).expanduser().resolve()
        if not resolved.exists():
            msg = f"Path does not exist: {resolved}"
            raise ConfigError(msg)

    if message and message.strip():
        return message.strip(), resolved
    if resolved is not None:
        return str(resolved), resolved

    msg = "Provide -Message and/or -Path"
    raise ConfigError(msg)


resolve_agent_input = resolve_cli_input


def render_clarification(
    *,
    console: Console,
    submission: Submission,
    verbose: bool,
    review_mode: ReviewMode = DEFAULT_REVIEW_MODE,
) -> None:
    yaml_cfg = load_yaml_config()
    mode = "verbose" if verbose else yaml_cfg.output.default_mode
    console.print(
        Panel.fit(
            f"[bold]AI Homework Mentor[/bold] v{__version__}\n"
            f"mode={mode}\nreview_mode={review_mode}",
            title="session",
            border_style="cyan",
        ),
    )
    console.print(Panel(submission.raw_text or "(empty)", title="input", border_style="blue"))
    if verbose:
        _print_parse_table(console, submission)
    question = submission.clarification_question or "Need more details."
    console.print(Panel(question, title="clarification", border_style="yellow"))


def render_success(  # noqa: C901, PLR0912 — verbose layout branches
    *,
    console: Console,
    result: SessionResult,
    verbose: bool,
    model: str | None = None,
) -> None:
    yaml_cfg = load_yaml_config()
    mode = "verbose" if verbose else yaml_cfg.output.default_mode
    submission = result.submission
    fetch = result.fetch
    review = result.review
    if fetch is None or review is None or result.workspace is None or result.rubric is None:
        msg = "Internal error: ok session without review artifacts"
        raise ConfigError(msg)

    session_header = (
        f"[bold]AI Homework Mentor[/bold] v{__version__}\n"
        f"mode={mode}\nreview_mode={result.review_mode}"
    )
    if model:
        session_header += f"\nmodel={model}"
    console.print(
        Panel.fit(
            session_header,
            title="session",
            border_style="cyan",
        ),
    )
    console.print(Panel(submission.raw_text or "(empty)", title="input", border_style="blue"))

    summary = (
        f"source: {submission.source_type.value} -> {submission.source_value}\n"
        f"topic: {submission.topic}\n"
        f"code received: {fetch.file_count} files\n"
        f"workspace: {result.workspace.root}"
    )
    console.print(Panel(summary, title="submission", border_style="magenta"))

    if verbose:
        _print_parse_table(console, submission)
        _print_fetch_table(console, fetch, ignore_names=yaml_cfg.agent.code_fetch.ignore_names)
        render_rubric_panel(console, result.rubric)
        if yaml_cfg.output.verbose.show_skills:
            render_skills_panel(console, result.skills or review.skills)
        if yaml_cfg.output.verbose.show_workspace:
            render_workspace_tree(
                console,
                result.workspace,
                events=review.events.events,
            )
        if yaml_cfg.output.verbose.show_plan and review.todos:
            render_todo_table(console, review.todos)
        if yaml_cfg.output.verbose.show_context_metrics:
            render_context_trace(console, review.context_trace.events)
        if yaml_cfg.output.verbose.show_subagents and result.review_mode == "subagents":
            parent_max = (
                max((event.tokens_after for event in review.context_trace.events), default=0)
                or None
            )
            render_subagents_panel(
                console,
                review.subagent_handoffs.events,
                parent_max_tokens=parent_max,
            )
        note_files = [
            path for path in result.workspace.list_relative_files() if path.startswith("notes/")
        ]
        if note_files:
            console.print(Panel("\n".join(note_files), title="notes files", border_style="dim"))
    else:
        render_current_todo(console, review.todos)
        if result.review_mode == "subagents":
            render_delegation_compact(console, review.subagent_handoffs.delegated_aspects())
        render_skills_compact(console, result.skills or review.skills)
        if yaml_cfg.output.verbose.show_context_metrics:
            render_context_compact(console, review.context_trace.events)

    render_feedback(
        console,
        review.final_feedback,
        verbose=verbose and yaml_cfg.output.verbose.show_synthesis,
        fix_plan=review.fix_plan,
        reflection=review.reflection,
        artifact_hints=[
            "output/final_feedback.json",
            "output/final_feedback.md",
            "output/fix_plan.json",
            "output/fix_plan.md",
            "docs/review-report-*.md",
        ],
    )
    if verbose and result.reply:
        console.print(Panel(result.reply, title="ответ оркестратора", border_style="green"))


def _print_parse_table(console: Console, submission: Submission) -> None:
    table = Table(title="parse result", show_header=True, header_style="bold")
    table.add_column("key")
    table.add_column("value")
    table.add_row("source_type", submission.source_type.value)
    table.add_row("source_value", submission.source_value or "")
    table.add_row("topic", submission.topic or "")
    table.add_row("needs_clarification", str(submission.needs_clarification))
    console.print(table)


def _print_fetch_table(
    console: Console,
    fetch: FetchResult,
    *,
    ignore_names: list[str],
) -> None:
    table = Table(title="fetch / staging", show_header=True, header_style="bold")
    table.add_column("key")
    table.add_column("value")
    table.add_row("staging", str(fetch.staging_dir))
    table.add_row("files", str(fetch.file_count))
    table.add_row(
        "ignore_names",
        ", ".join(ignore_names[:_IGNORE_PREVIEW])
        + ("..." if len(ignore_names) > _IGNORE_PREVIEW else ""),
    )
    console.print(table)
    sample = "\n".join(fetch.files[:_MANIFEST_PREVIEW]) or "(no files)"
    console.print(Panel(sample, title="manifest (first files)", border_style="dim"))


def _persist_summary_log(*, console: Console, meta: SessionLogMeta) -> Path:
    path = write_summary_log(console=console, meta=meta)
    setup_logging().info("summary log written path=%s", path)
    return path


def _persist_run_report(  # noqa: PLR0913 — CLI report wiring
    *,
    console: Console,
    result: SessionResult,
    model: str,
    verbose: bool,
    wall_ms: int,
    runtime: RuntimeSettings | None,
    status: str = "ok",
    docs_dir: Path | None = None,
) -> Path | None:
    """Write Russian run report to docs/; return path or None on skip/failure."""
    if result.kind != "ok" or result.workspace is None or result.review is None:
        return None
    try:
        report = build_run_report(
            result,
            model=model,
            verbose=verbose,
            wall_ms=wall_ms,
            version=__version__,
            settings=runtime,
            openrouter_api_base=(
                runtime.openrouter_api_base if runtime is not None else DEFAULT_OPENROUTER_API_BASE
            ),
            status=status,
        )
        path = write_run_report(report, docs_dir=docs_dir)
        console.print(Panel(str(path), title="отчёт прогона", border_style="dim"))
        setup_logging().info("run report written path=%s", path)
    except Exception:
        logger.exception("failed to write run report")
        return None
    else:
        return path


def _persist_review_report(
    *,
    console: Console,
    result: SessionResult,
    model: str,
    docs_dir: Path | None = None,
) -> Path | None:
    """Write full Russian review recommendations report to docs/."""
    if result.kind != "ok" or result.review is None:
        return None
    try:
        path = write_review_report(result, model=model, docs_dir=docs_dir)
        if path is None:
            return None
        console.print(Panel(str(path), title="отчёт проверки", border_style="dim"))
        setup_logging().info("review report written path=%s", path)
    except Exception:
        logger.exception("failed to write review report")
        return None
    else:
        return path


def _persist_failed_session_reports(  # noqa: PLR0913 — error-path persist wiring
    *,
    console: Console,
    session_id: str,
    model: str,
    verbose: bool,
    wall_ms: int,
    review_mode: ReviewMode,
    error_message: str,
    runtime: RuntimeSettings | None,
    docs_dir: Path | None = None,
    project_root_override: Path | None = None,
) -> tuple[Path | None, Path | None]:
    """Write partial run/review reports after ReviewError; return (run, review) paths."""
    run_path: Path | None = None
    review_path: Path | None = None
    try:
        report = build_failed_run_report(
            session_id=session_id,
            model=model,
            verbose=verbose,
            wall_ms=wall_ms,
            version=__version__,
            error_message=error_message,
            review_mode=review_mode,
            settings=runtime,
            openrouter_api_base=(
                runtime.openrouter_api_base if runtime is not None else DEFAULT_OPENROUTER_API_BASE
            ),
            project_root_override=project_root_override,
            status="failed",
        )
        run_path = write_run_report(report, docs_dir=docs_dir)
        console.print(Panel(str(run_path), title="отчёт прогона (partial)", border_style="yellow"))
        setup_logging().info("failed run report written path=%s", run_path)
    except Exception:
        logger.exception("failed to write partial run report session=%s", session_id)

    try:
        review_path = write_partial_review_report(
            session_id=session_id,
            review_mode=review_mode,
            error_message=error_message,
            model=model,
            docs_dir=docs_dir,
            project_root_override=project_root_override,
        )
        if review_path is not None:
            console.print(
                Panel(str(review_path), title="отчёт проверки (partial)", border_style="yellow"),
            )
            setup_logging().info("partial review report written path=%s", review_path)
    except Exception:
        logger.exception("failed to write partial review report session=%s", session_id)

    return run_path, review_path


def _log_if_recording(*, console: Console, record: bool, meta: SessionLogMeta) -> None:
    if record:
        _persist_summary_log(console=console, meta=meta)


def _fallback_session_id() -> str:
    return datetime.now(tz=UTC).strftime("%Y%m%dT%H%M%SZ")


def _resolve_runtime_model(
    session_runner: object | None,
) -> tuple[str, RuntimeSettings | None]:
    if session_runner is not None:
        return load_yaml_config().agent.model, None
    runtime = load_runtime_settings()
    return runtime.yaml.agent.model, runtime


def _session_log_meta(  # noqa: PLR0913
    session_id: str,
    model: str,
    *,
    verbose: bool,
    exit_code: int,
    runtime: RuntimeSettings | None = None,
    result: SessionResult | None = None,
) -> SessionLogMeta:
    return SessionLogMeta(
        session_id=session_id,
        model=model,
        verbose=verbose,
        exit_code=exit_code,
        result=result,
        openrouter_api_base=runtime.openrouter_api_base if runtime else None,
    )


def main(  # noqa: C901, PLR0915 — CLI orchestration
    argv: list[str] | None = None,
    *,
    session_runner: Callable[..., SessionResult] | None = None,
    review_runner: Callable[..., object] | None = None,
    console: Console | None = None,
) -> int:
    """CLI entry. Returns process exit code."""
    record = console is None
    out = console or Console(legacy_windows=False, record=True)
    parser = build_parser()
    args = parser.parse_args(argv)
    verbose = bool(args.verbose)
    model = load_yaml_config().agent.model
    runtime = None
    review_mode: ReviewMode = DEFAULT_REVIEW_MODE

    try:
        raw_text, path = resolve_cli_input(message=args.message, path=args.path)
        review_mode = resolve_review_mode(args.mode)
    except ConfigError as exc:
        out.print(f"[red]error:[/red] {exc}")
        _log_if_recording(
            console=out,
            record=record,
            meta=_session_log_meta(
                _fallback_session_id(), model, verbose=verbose, exit_code=2, runtime=runtime
            ),
        )
        return 2

    try:
        model, runtime = _resolve_runtime_model(session_runner)
    except ConfigError as exc:
        out.print(f"[red]error:[/red] {exc}")
        _log_if_recording(
            console=out,
            record=record,
            meta=_session_log_meta(_fallback_session_id(), model, verbose=verbose, exit_code=2),
        )
        return 2

    log = setup_logging(level=runtime.log_level if runtime else "INFO")
    api_base = runtime.openrouter_api_base if runtime else DEFAULT_OPENROUTER_API_BASE
    log.info(
        "cli start model=%s api_base=%s verbose=%s review_mode=%s",
        model,
        api_base,
        verbose,
        review_mode,
    )
    started = time.perf_counter()

    try:
        if session_runner is not None:
            try:
                result = session_runner(
                    raw_text=raw_text,
                    explicit_path=path,
                    review_mode=review_mode,
                )
            except TypeError:
                # Test doubles may not accept review_mode.
                result = session_runner(raw_text=raw_text, explicit_path=path)
        else:
            result = run_homework_session(
                raw_text=raw_text,
                explicit_path=path,
                settings=runtime,
                review_runner=review_runner,
                review_mode=review_mode,
            )
    except (ConfigError, AgentError, CodeFetchError) as exc:
        out.print(f"[red]error:[/red] {exc}")
        session_id = (
            exc.session_id
            if isinstance(exc, ReviewError) and exc.session_id
            else _fallback_session_id()
        )
        wall_ms = int((time.perf_counter() - started) * 1000)
        log.exception("cli failed session=%s", session_id)
        if record and isinstance(exc, ReviewError) and exc.session_id:
            _persist_failed_session_reports(
                console=out,
                session_id=exc.session_id,
                model=model,
                verbose=verbose,
                wall_ms=wall_ms,
                review_mode=review_mode,
                error_message=str(exc),
                runtime=runtime,
            )
        _log_if_recording(
            console=out,
            record=record,
            meta=_session_log_meta(
                session_id, model, verbose=verbose, exit_code=1, runtime=runtime
            ),
        )
        return 1
    except Exception as exc:
        detail = describe_exception(exc)
        out.print(f"[red]unexpected error:[/red] {detail}")
        log.exception("cli unexpected error: %s", detail)
        _log_if_recording(
            console=out,
            record=record,
            meta=_session_log_meta(
                _fallback_session_id(), model, verbose=verbose, exit_code=1, runtime=runtime
            ),
        )
        return 1

    wall_ms = int((time.perf_counter() - started) * 1000)

    if result.kind == "clarification":
        render_clarification(
            console=out,
            submission=result.submission,
            verbose=verbose,
            review_mode=result.review_mode,
        )
        _log_if_recording(
            console=out,
            record=record,
            meta=_session_log_meta(
                _fallback_session_id(),
                model,
                verbose=verbose,
                exit_code=2,
                runtime=runtime,
                result=result,
            ),
        )
        return 2

    exit_code = 0
    try:
        render_success(console=out, result=result, verbose=verbose, model=model)
    except Exception as exc:  # noqa: BLE001 — Rich render on legacy Windows consoles
        out.print(f"[red]render error:[/red] {exc}")
        exit_code = 1

    if record:
        report_status = "ok" if exit_code == 0 else "partial"
        _persist_run_report(
            console=out,
            result=result,
            model=model,
            verbose=verbose,
            wall_ms=wall_ms,
            runtime=runtime,
            status=report_status,
        )
        _persist_review_report(console=out, result=result, model=model)
        if result.workspace is not None:
            _persist_summary_log(
                console=out,
                meta=_session_log_meta(
                    result.workspace.session_id,
                    model,
                    verbose=verbose,
                    exit_code=exit_code,
                    runtime=runtime,
                    result=result,
                ),
            )
    return exit_code


def run(argv: list[str] | None = None) -> None:
    raise SystemExit(main(argv))


if __name__ == "__main__":
    run()
