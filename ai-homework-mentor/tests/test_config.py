from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from homework_mentor.config import (
    ConfigError,
    load_runtime_settings,
    load_yaml_config,
    project_root,
)


def test_load_yaml_config_from_project() -> None:
    cfg = load_yaml_config()
    assert cfg.agent.model.startswith("openrouter:")
    assert cfg.output.default_mode == "compact"
    assert "Homework Mentor" in cfg.orchestrator_prompts.system_prompt
    assert "invent" in cfg.parse_submission_prompts.system_prompt.lower()
    assert "write_todos" in cfg.review_prompts.system_prompt.lower()
    assert "contradiction" in cfg.synthesis_reflection_prompts.system_prompt.lower()
    assert "criterion" in cfg.synthesis_final_prompts.system_prompt.lower()
    assert cfg.output.verbose.show_plan is True
    assert cfg.output.verbose.show_skills is True
    assert cfg.output.verbose.show_synthesis is True
    assert (project_root() / "config" / "agent.yaml").is_file()
    assert (project_root() / "config" / "skills_routing.yaml").is_file()


def test_load_yaml_config_missing_file(tmp_path: Path) -> None:
    with pytest.raises(ConfigError, match="Missing required config file"):
        load_yaml_config(root=tmp_path)


def test_load_yaml_config_invalid_field(tmp_path: Path) -> None:
    config = tmp_path / "config"
    (config / "prompts").mkdir(parents=True)
    (config / "agent.yaml").write_text(
        yaml.dump(
            {
                "model": "openrouter:test",
                "temperature": 0.1,
                "max_tokens": 100,
                "context": {"window_tokens": 1000, "summarize_threshold_tokens": 0},
            },
        ),
        encoding="utf-8",
    )
    (config / "prompts" / "orchestrator.yaml").write_text(
        "system_prompt: hi\n",
        encoding="utf-8",
    )
    (config / "prompts" / "parse_submission.yaml").write_text(
        "system_prompt: extract topic\n",
        encoding="utf-8",
    )
    (config / "prompts" / "review.yaml").write_text(
        "system_prompt: review\n"
        "feedback_json_schema: '{}'\n"
        "review_user_template: '{topic}'\n"
        "single_system_prompt: single\n"
        "single_review_user_template: '{topic}'\n",
        encoding="utf-8",
    )
    (config / "prompts" / "synthesis_reflection.yaml").write_text(
        "system_prompt: reflect\nuser_template: '{gaps}'\n",
        encoding="utf-8",
    )
    (config / "prompts" / "synthesis_final.yaml").write_text(
        "system_prompt: synthesize\nuser_template: '{topic}'\n",
        encoding="utf-8",
    )
    (config / "output.yaml").write_text(
        "default_mode: nope\n",
        encoding="utf-8",
    )
    with pytest.raises(ConfigError, match="Config validation failed"):
        load_yaml_config(root=tmp_path)


def test_runtime_settings_requires_api_key(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    with pytest.raises(ConfigError, match="OPENROUTER_API_KEY"):
        load_runtime_settings(env_file=Path("no-such.env"))


def test_runtime_settings_with_api_key(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text("OPENROUTER_API_KEY=sk-or-v1-test-key\n", encoding="utf-8")
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    settings = load_runtime_settings(env_file=env_file)
    assert settings.openrouter_api_key.get_secret_value() == "sk-or-v1-test-key"
    assert settings.yaml.agent.model


def test_openrouter_api_base_from_env(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text(
        "OPENROUTER_API_KEY=sk-or-v1-test-key\nOPENROUTER_URL=https://proxy.example/v1\n",
        encoding="utf-8",
    )
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    monkeypatch.delenv("OPENROUTER_URL", raising=False)
    monkeypatch.delenv("OPENROUTER_API_BASE", raising=False)
    settings = load_runtime_settings(env_file=env_file)
    assert settings.openrouter_api_base == "https://proxy.example/v1"


def test_openrouter_model_with_free_suffix_gets_prefix(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text(
        "OPENROUTER_API_KEY=sk-or-v1-test-key\n"
        "OPENROUTER_MODEL=nvidia/nemotron-3-nano-30b-a3b:free\n",
        encoding="utf-8",
    )
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    monkeypatch.delenv("OPENROUTER_MODEL", raising=False)
    settings = load_runtime_settings(env_file=env_file)
    assert settings.yaml.agent.model == "openrouter:nvidia/nemotron-3-nano-30b-a3b:free"
