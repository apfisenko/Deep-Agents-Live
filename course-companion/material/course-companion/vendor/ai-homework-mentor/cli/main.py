"""Mentor CLI entry point."""

from __future__ import annotations

import typer
from rich.console import Console

from cli.progress import LiveProgress
from cli.renderer import render_result
from mentor.agent.orchestrator import MentorOrchestrator
from mentor.agent.tools.parse import SourceType
from mentor.config import get_config
from mentor.logging_setup import setup_logging

app = typer.Typer(
    name="mentor",
    help="AI Homework Mentor — review student submissions with DeepAgents",
    no_args_is_help=True,
)
console = Console()


@app.callback()
def main_callback() -> None:
    """AI Homework Mentor CLI."""


@app.command("check")
def check(
    submission: str = typer.Argument(..., help="Path, GitHub URL, or text"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Educational verbose output"),
    topic: str | None = typer.Option(None, "--topic", help="Assignment topic override"),
    chat_only: bool = typer.Option(
        False,
        "--chat-only",
        help="S00 mode: simple LLM reply without code review",
    ),
) -> None:
    """Run homework review (or simple chat in --chat-only mode)."""
    config = get_config()
    log = setup_logging(config)
    log.info("mentor check started")

    orchestrator = MentorOrchestrator(config)

    from mentor.agent.tools.parse import parse_submission

    preview = parse_submission(submission, topic_override=topic)
    if preview.needs_topic and preview.source_type != SourceType.TEXT_ONLY and not topic:
        console.print(
            "[yellow]Could not determine topic.[/yellow] "
            'Please provide --topic, e.g. --topic "Python Telegram bot"'
        )
        raise typer.Exit(code=1)

    try:
        with LiveProgress(console, verbose=verbose) as progress:
            result = orchestrator.run(
                submission,
                topic=topic,
                enable_review=not chat_only,
                progress=progress,
            )
    except Exception as exc:
        log.exception("mentor check failed")
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(code=1) from exc

    render_result(result, verbose=verbose)
    log.info("mentor check completed in %.1fs", result.elapsed_s)


def main() -> None:
    app(prog_name="mentor")


if __name__ == "__main__":
    main()
