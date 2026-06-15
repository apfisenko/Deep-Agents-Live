"""Eval test fixtures — env placeholders for run configs."""

from __future__ import annotations

import pytest


@pytest.fixture(autouse=True)
def _eval_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LLM_MODEL", "openai/gpt-4o-mini")
    monkeypatch.setenv("LLM_TEMPERATURE", "0.2")
    monkeypatch.setenv("EVAL_JUDGE_MODEL", "google/gemini-2.5-flash-lite")
    monkeypatch.setenv("EVAL_JUDGE_TEMPERATURE", "0.0")
    monkeypatch.setenv("EMBEDDING_MODEL", "openai/text-embedding-3-small")
