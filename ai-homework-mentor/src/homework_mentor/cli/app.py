"""Rich CLI for AI Homework Mentor."""

from __future__ import annotations

import argparse
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
    render_feedback,
    render_rubric_panel,
    render_todo_table,
    render_workspace_tree,
)
from homework_mentor.code_fetch import CodeFetchError
from homework_mentor.config import ConfigError, load_yaml_config
from homework_mentor.logging_setup import setup_logging
from homework_mentor.orchestrator import AgentError
from homework_mentor.pipeline import SessionResult, run_homework_session

if TYPE_CHECKING:
    from collections.abc import Callable

    from homework_mentor.code_fetch import FetchResult
    from homework_mentor.submission import Submission

_IGNORE_PREVIEW = 8
_MANIFEST_PREVIEW = 15


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="homework-mentor",
        description="AI Homework Mentor — workspace review with rubric and todo plan (Sprint 02)",
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
) -> None:
    yaml_cfg = load_yaml_config()
    mode = "verbose" if verbose else yaml_cfg.output.default_mode
    console.print(
        Panel.fit(
            f"[bold]AI Homework Mentor[/bold] v{__version__}\nmode={mode}",
            title="session",
            border_style="cyan",
        ),
    )
    console.print(Panel(submission.raw_text or "(empty)", title="input", border_style="blue"))
    if verbose:
        _print_parse_table(console, submission)
    question = submission.clarification_question or "Need more details."
    console.print(Panel(question, title="clarification", border_style="yellow"))


def render_success(
    *,
    console: Console,
    result: SessionResult,
    verbose: bool,
) -> None:
    yaml_cfg = load_yaml_config()
    mode = "verbose" if verbose else yaml_cfg.output.default_mode
    submission = result.submission
    fetch = result.fetch
    review = result.review
    if fetch is None or review is None or result.workspace is None or result.rubric is None:
        msg = "Internal error: ok session without review artifacts"
        raise ConfigError(msg)

    console.print(
        Panel.fit(
            f"[bold]AI Homework Mentor[/bold] v{__version__}\nmode={mode}",
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
        note_files = [
            path for path in result.workspace.list_relative_files() if path.startswith("notes/")
        ]
        if note_files:
            console.print(Panel("\n".join(note_files), title="notes files", border_style="dim"))
    else:
        render_current_todo(console, review.todos)
        if yaml_cfg.output.verbose.show_context_metrics:
            render_context_compact(console, review.context_trace.events)

    render_feedback(console, review.feedback, verbose=verbose)
    if verbose and result.reply:
        console.print(Panel(result.reply, title="assistant", border_style="green"))


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


def main(
    argv: list[str] | None = None,
    *,
    session_runner: Callable[..., SessionResult] | None = None,
    review_runner: Callable[..., object] | None = None,
    console: Console | None = None,
) -> int:
    """CLI entry. Returns process exit code."""
    out = console or Console(legacy_windows=False)
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        raw_text, path = resolve_cli_input(message=args.message, path=args.path)
    except ConfigError as exc:
        out.print(f"[red]error:[/red] {exc}")
        return 2

    setup_logging()

    try:
        if session_runner is not None:
            result = session_runner(raw_text=raw_text, explicit_path=path)
        else:
            result = run_homework_session(
                raw_text=raw_text,
                explicit_path=path,
                review_runner=review_runner,
            )
    except (ConfigError, AgentError, CodeFetchError) as exc:
        out.print(f"[red]error:[/red] {exc}")
        return 1
    except Exception as exc:  # noqa: BLE001 — top-level CLI boundary
        out.print(f"[red]unexpected error:[/red] {exc}")
        return 1

    if result.kind == "clarification":
        render_clarification(
            console=out,
            submission=result.submission,
            verbose=bool(args.verbose),
        )
        return 2

    render_success(console=out, result=result, verbose=bool(args.verbose))
    return 0


def run(argv: list[str] | None = None) -> None:
    raise SystemExit(main(argv))


if __name__ == "__main__":
    run()
