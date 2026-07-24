from __future__ import annotations

from io import StringIO
from pathlib import Path

import pytest
from rich.console import Console

from homework_mentor.cli.app import main, resolve_agent_input
from homework_mentor.config import ConfigError


def test_resolve_message_only() -> None:
    text, path = resolve_agent_input(message="ping", path=None)
    assert text == "ping"
    assert path is None


def test_resolve_path_only(tmp_path: Path) -> None:
    text, path = resolve_agent_input(message=None, path=str(tmp_path))
    assert path == tmp_path.resolve()
    assert text == str(tmp_path.resolve())


def test_resolve_missing_path() -> None:
    with pytest.raises(ConfigError, match="does not exist"):
        resolve_agent_input(message=None, path="C:/no/such/homework-path-xyz")


def test_cli_requires_input() -> None:
    buffer = StringIO()
    console = Console(file=buffer, force_terminal=True, width=80, highlight=False)
    code = main([], console=console)
    assert code == 2
