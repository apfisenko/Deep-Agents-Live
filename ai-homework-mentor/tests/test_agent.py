from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
from langchain_core.messages import AIMessage, HumanMessage

from homework_mentor.config import load_runtime_settings
from homework_mentor.orchestrator.agent import AgentError, extract_final_text, run_agent


class _FakeAgent:
    def invoke(self, _payload: dict[str, Any]) -> dict[str, Any]:
        return {
            "messages": [
                HumanMessage(content="ping"),
                AIMessage(content="pong from stub"),
            ],
        }


def test_extract_final_text() -> None:
    text = extract_final_text(
        {
            "messages": [
                HumanMessage(content="hi"),
                AIMessage(content="hello"),
            ],
        },
    )
    assert text == "hello"


def test_run_agent_with_mock_factory(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text("OPENROUTER_API_KEY=sk-or-v1-test-key\n", encoding="utf-8")
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    settings = load_runtime_settings(env_file=env_file)

    reply = run_agent(
        "ping",
        settings=settings,
        agent_factory=lambda _settings: _FakeAgent(),
    )
    assert reply == "pong from stub"
    assert "Homework Mentor" in settings.yaml.orchestrator_prompts.system_prompt


def test_run_agent_rejects_empty_message(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text("OPENROUTER_API_KEY=sk-or-v1-test-key\n", encoding="utf-8")
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    settings = load_runtime_settings(env_file=env_file)
    with pytest.raises(AgentError, match="non-empty"):
        run_agent("   ", settings=settings, agent_factory=lambda _s: _FakeAgent())


def test_prompt_not_hardcoded_in_agent_module() -> None:
    agent_source = (
        Path(__file__).resolve().parents[1]
        / "src"
        / "homework_mentor"
        / "orchestrator"
        / "agent.py"
    ).read_text(encoding="utf-8")
    assert "You are AI Homework Mentor" not in agent_source
    assert "orchestrator_prompts.system_prompt" in agent_source
