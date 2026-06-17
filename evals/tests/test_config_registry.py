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
    monkeypatch.setenv(
        "SYSTEM_PROMPT_PATH",
        "backend/app/agent/prompts/SYSTEM_PROMPT_SEARCH_FALLBACK.txt",
    )
    monkeypatch.setattr("app.agent.config_registry.load_repo_env", lambda: None)
    reset_config_registry()


def test_baseline_yaml_parses() -> None:
    path = EVALS_CONFIGS_DIR / "baseline-react-inmemory.yaml"
    cfg = RunConfig.from_yaml_path(path)
    assert cfg.config_id == "baseline-react-inmemory"
    assert cfg.retrieval.backend == "in-memory"
    assert cfg.model.name == os.environ["LLM_MODEL"]
    assert cfg.model.temperature == 0.2
    assert cfg.prompt.source == "file"
    assert cfg.prompt.name == "SYSTEM_PROMPT_SEARCH_FALLBACK"
    assert cfg.prompt.path.endswith("SYSTEM_PROMPT_SEARCH_FALLBACK.txt")
    assert cfg.extra_evaluators == ["executed_tools_count"]


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
    assert candidate.model == baseline.model
    # legacy iter-1 candidate keeps prompts.py SYSTEM_PROMPT; baseline uses .txt via env
    assert candidate.prompt.name == "SYSTEM_PROMPT"
    assert candidate.prompt.path.endswith("SYSTEM_PROMPT.txt")
    assert baseline.prompt.path.endswith("SYSTEM_PROMPT_SEARCH_FALLBACK.txt")


def test_benchmark_differs_only_in_temperature() -> None:
    baseline = get_run_config("baseline-react-inmemory")
    benchmark = get_run_config("benchmark-high-temp")
    assert benchmark.benchmark_only is True
    assert benchmark.model.temperature == 0.8
    assert baseline.model.name == benchmark.model.name
    assert baseline.agent == benchmark.agent


def test_oss_candidate_aligns_prompt_with_baseline() -> None:
    baseline = get_run_config("baseline-react-inmemory")
    oss = get_run_config("candidate-gpt-oss-120b-v001")
    assert oss.benchmark_only is True
    assert oss.prompt.name == baseline.prompt.name
    assert oss.prompt.path == baseline.prompt.path
    assert oss.extra_evaluators == ["executed_tools_count"]
