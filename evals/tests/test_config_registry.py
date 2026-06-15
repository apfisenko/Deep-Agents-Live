"""Eval config tests — require env vars for ${...} placeholders."""

import os

import pytest

from app.agent.config_registry import get_run_config, list_config_ids, reset_config_registry
from app.agent.run_config import RunConfig
from app.paths import EVALS_CONFIGS_DIR


@pytest.fixture(autouse=True)
def _eval_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LLM_MODEL", "openai/gpt-4o-mini")
    monkeypatch.setenv("LLM_TEMPERATURE", "0.2")
    monkeypatch.setenv("EVAL_JUDGE_MODEL", "google/gemini-2.5-flash-lite")
    monkeypatch.setenv("EVAL_JUDGE_TEMPERATURE", "0.0")
    reset_config_registry()


def test_baseline_yaml_parses() -> None:
    path = EVALS_CONFIGS_DIR / "baseline-react-inmemory.yaml"
    cfg = RunConfig.from_yaml_path(path)
    assert cfg.config_id == "baseline-react-inmemory"
    assert cfg.retrieval.backend == "in-memory"
    assert cfg.model.name == os.environ["LLM_MODEL"]
    assert cfg.model.temperature == 0.2
    assert cfg.prompt.source == "file"


def test_registry_lists_configs() -> None:
    ids = list_config_ids()
    assert "baseline-react-inmemory" in ids
    assert "benchmark-high-temp" in ids
    assert "candidate-search-first-prompt" in ids
    assert "candidate-search-fallback-prompt" in ids
    assert "candidate-kb-alignment-v001" in ids
    assert "candidate-kb-alignment-search-fallback-v001" in ids


def test_kb_alignment_differs_only_in_config_id() -> None:
    baseline = get_run_config("baseline-react-inmemory")
    candidate = get_run_config("candidate-kb-alignment-v001")
    assert candidate.benchmark_only is True
    assert candidate.prompt == baseline.prompt
    assert candidate.model == baseline.model


def test_benchmark_differs_only_in_temperature() -> None:
    baseline = get_run_config("baseline-react-inmemory")
    benchmark = get_run_config("benchmark-high-temp")
    assert benchmark.benchmark_only is True
    assert benchmark.model.temperature == 0.8
    assert baseline.model.name == benchmark.model.name
    assert baseline.agent == benchmark.agent
