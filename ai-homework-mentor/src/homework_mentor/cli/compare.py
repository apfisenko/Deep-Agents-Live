"""CLI: сравнить режимы single и subagents, записать отчёт в docs/."""

from __future__ import annotations

import argparse
import logging
import time
from datetime import UTC, datetime
from pathlib import Path  # noqa: TC003 — used at runtime
from typing import TYPE_CHECKING

from rich.console import Console
from rich.panel import Panel

from homework_mentor import __version__
from homework_mentor.cli.app import resolve_cli_input
from homework_mentor.config import (
    DEFAULT_OPENROUTER_API_BASE,
    ConfigError,
    load_runtime_settings,
    project_root,
)
from homework_mentor.errors import describe_exception
from homework_mentor.logging_setup import setup_logging
from homework_mentor.orchestrator import AgentError, ReviewError
from homework_mentor.pipeline import run_homework_session
from homework_mentor.reports import build_run_report, write_run_report
from homework_mentor.reports.compare import write_compare_modes_report

if TYPE_CHECKING:
    from homework_mentor.config import ReviewMode, RuntimeSettings
    from homework_mentor.pipeline import SessionResult
    from homework_mentor.reports.models import RunReport

logger = logging.getLogger(__name__)


def build_compare_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="homework-mentor-compare",
        description="Сравнение режимов single и subagents → docs/compare-modes-*.md",
    )
    parser.add_argument("-Message", "--message", dest="message", help="Текст submission")
    parser.add_argument("-Path", "--path", dest="path", help="Локальный путь к коду")
    parser.add_argument(
        "-Verbose",
        "--verbose",
        dest="verbose",
        action="store_true",
        help="Передаётся в оба прогона (на compare-файл не влияет)",
    )
    return parser


def _run_one_mode(  # noqa: PLR0913 — mode run wiring
    *,
    raw_text: str,
    explicit_path: Path | None,
    review_mode: ReviewMode,
    runtime: RuntimeSettings,
    verbose: bool,
    docs_dir: Path,
) -> tuple[SessionResult, RunReport, Path]:
    started = time.perf_counter()
    result = run_homework_session(
        raw_text=raw_text,
        explicit_path=explicit_path,
        settings=runtime,
        review_mode=review_mode,
    )
    wall_ms = int((time.perf_counter() - started) * 1000)
    if result.kind != "ok" or result.review is None or result.workspace is None:
        msg = f"Режим {review_mode}: нужен успешный прогон (ok), получено kind={result.kind}"
        raise ConfigError(msg)
    report = build_run_report(
        result,
        model=runtime.yaml.agent.model,
        verbose=verbose,
        wall_ms=wall_ms,
        version=__version__,
        settings=runtime,
        openrouter_api_base=runtime.openrouter_api_base or DEFAULT_OPENROUTER_API_BASE,
        status="ok",
    )
    path = write_run_report(report, docs_dir=docs_dir)
    return result, report, path


def main(argv: list[str] | None = None, *, docs_dir: Path | None = None) -> int:
    """Entry for compare-modes. Returns process exit code."""
    console = Console(legacy_windows=False)
    parser = build_compare_parser()
    args = parser.parse_args(argv)
    verbose = bool(args.verbose)
    out_docs = docs_dir or (project_root() / "docs")

    try:
        raw_text, path = resolve_cli_input(message=args.message, path=args.path)
        runtime = load_runtime_settings()
    except ConfigError as exc:
        console.print(f"[red]error:[/red] {exc}")
        return 2

    log = setup_logging(level=runtime.log_level)
    stamp = datetime.now(tz=UTC).strftime("%Y%m%dT%H%M%SZ")
    log.info("compare-modes start stamp=%s verbose=%s", stamp, verbose)

    try:
        console.print("[cyan]Прогон mode=single…[/cyan]")
        _, single_report, single_path = _run_one_mode(
            raw_text=raw_text,
            explicit_path=path,
            review_mode="single",
            runtime=runtime,
            verbose=verbose,
            docs_dir=out_docs,
        )
        console.print("[cyan]Прогон mode=subagents…[/cyan]")
        _, subagents_report, subagents_path = _run_one_mode(
            raw_text=raw_text,
            explicit_path=path,
            review_mode="subagents",
            runtime=runtime,
            verbose=verbose,
            docs_dir=out_docs,
        )
        compare_path = write_compare_modes_report(
            single=single_report,
            subagents=subagents_report,
            single_report_path=single_path,
            subagents_report_path=subagents_path,
            docs_dir=out_docs,
            stamp=stamp,
        )
    except (ConfigError, AgentError, ReviewError) as exc:
        console.print(f"[red]error:[/red] {exc}")
        logger.exception("compare-modes failed")
        return 1
    except Exception as exc:
        console.print(f"[red]unexpected error:[/red] {describe_exception(exc)}")
        logger.exception("compare-modes unexpected")
        return 1

    console.print(Panel(str(single_path), title="run-отчёт single", border_style="dim"))
    console.print(Panel(str(subagents_path), title="run-отчёт subagents", border_style="dim"))
    console.print(Panel(str(compare_path), title="сравнительный отчёт", border_style="green"))
    log.info("compare-modes done path=%s", compare_path)
    return 0


def run(argv: list[str] | None = None) -> None:
    raise SystemExit(main(argv))


if __name__ == "__main__":
    run()
