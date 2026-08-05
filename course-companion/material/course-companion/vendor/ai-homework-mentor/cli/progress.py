"""Live terminal progress for mentor check (S05 Task 03)."""

from __future__ import annotations

import time
from typing import TYPE_CHECKING

from rich.console import Console
from rich.status import Status

if TYPE_CHECKING:
    from types import TracebackType

_PHASE_LABELS: dict[str, str] = {
    "parse": "Parsing submission",
    "acquire-code": "Acquiring student code",
    "select-rubric": "Selecting rubric",
    "materialize-skills": "Loading skills into workspace",
    "agent-review": "Running review agent",
    "synthesize": "Synthesizing feedback",
    "chat": "Chatting with mentor",
}


class LiveProgress:
    """TTY-aware phase reporter; degrades to line prints when piped."""

    def __init__(self, console: Console, *, verbose: bool = False) -> None:
        self._console = console
        self._verbose = verbose
        self._interactive = console.is_terminal
        self._started = time.perf_counter()
        self._phase = "init"
        self._status: Status | None = None
        self._current_detail = ""

    def __enter__(self) -> LiveProgress:
        if self._interactive:
            self._status = Status("", console=self._console, spinner="dots")
            self._status.start()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        if self._status is not None:
            elapsed = time.perf_counter() - self._started
            if exc is None:
                self._status.update(f"[green]Done[/green] ({elapsed:.1f}s)")
            else:
                self._status.update(f"[red]Failed[/red] ({elapsed:.1f}s)")
            self._status.stop()

    def phase(self, name: str) -> None:
        self._phase = name
        self._current_detail = ""
        self._render()

    def tool(self, tool_name: str, detail: str = "") -> None:
        if not self._verbose:
            return
        self._current_detail = f" → {tool_name}"
        if detail:
            self._current_detail += f" ({detail})"
        self._render()

    def _render(self) -> None:
        elapsed = time.perf_counter() - self._started
        label = _PHASE_LABELS.get(self._phase, self._phase)
        message = f"{label}{self._current_detail}… [{elapsed:.0f}s]"
        if self._status is not None:
            self._status.update(message)
        else:
            self._console.print(f"[dim]{message}[/dim]")
