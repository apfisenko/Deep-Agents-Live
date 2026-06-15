"""Config registry unit tests."""

from unittest.mock import MagicMock, patch

import pytest
from app.agent.config_registry import get_run_config, reset_config_registry
from app.agent.react_agent import ReactAgentRunner, reset_agent_runner
from app.exceptions import ConfigNotFoundError


@pytest.fixture(autouse=True)
def _eval_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LLM_MODEL", "openai/gpt-4o-mini")
    monkeypatch.setenv("LLM_TEMPERATURE", "0.2")
    monkeypatch.setenv("EVAL_JUDGE_MODEL", "google/gemini-2.5-flash-lite")
    monkeypatch.setenv("EVAL_JUDGE_TEMPERATURE", "0.0")
    reset_config_registry()
    reset_agent_runner()


def test_unknown_config_raises() -> None:
    with pytest.raises(ConfigNotFoundError) as exc_info:
        get_run_config("missing-config")
    assert exc_info.value.config_id == "missing-config"


def test_runners_use_different_temperatures() -> None:
    with (
        patch("app.agent.react_agent.create_chat_model") as mock_create,
        patch("app.agent.react_agent.create_react_agent") as mock_graph,
    ):
        mock_create.return_value = MagicMock()
        mock_graph.return_value = MagicMock()
        ReactAgentRunner(get_run_config("baseline-react-inmemory"))
        ReactAgentRunner(get_run_config("benchmark-high-temp"))

    temps = [call.kwargs["temperature"] for call in mock_create.call_args_list]
    assert temps == [0.2, 0.8]
