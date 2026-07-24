from __future__ import annotations

from pathlib import Path

import pytest
from rich.console import Console

from homework_mentor.cli.session_log import SessionLogMeta, summary_log_path, write_summary_log
from homework_mentor.config import load_runtime_settings


def test_openrouter_model_env_override(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text(
        "OPENROUTER_API_KEY=sk-or-v1-test-key\nOPENROUTER_MODEL=openai/gpt-4o-mini\n",
        encoding="utf-8",
    )
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    monkeypatch.delenv("OPENROUTER_MODEL", raising=False)
    settings = load_runtime_settings(env_file=env_file)
    assert settings.yaml.agent.model == "openrouter:openai/gpt-4o-mini"


def test_write_summary_log(tmp_path: Path) -> None:
    console = Console(width=100, record=True)
    console.print("hello session")
    meta = SessionLogMeta(
        session_id="20260724T120000Z",
        model="openrouter:test",
        verbose=True,
        exit_code=0,
        logs_dir=tmp_path,
    )
    path = write_summary_log(console=console, meta=meta)
    assert path == tmp_path / "summary_log_20260724T120000Z.md"
    text = path.read_text(encoding="utf-8")
    assert "20260724T120000Z" in text
    assert "hello session" in text
    assert "openrouter:test" in text


def test_summary_log_path() -> None:
    assert summary_log_path("abc").name == "summary_log_abc.md"
