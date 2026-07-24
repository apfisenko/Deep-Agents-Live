"""Configuration schemas and YAML/env loading (fail-fast)."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Literal

import yaml
from dotenv import load_dotenv
from pydantic import BaseModel, Field, SecretStr, ValidationError


class ConfigError(RuntimeError):
    """Raised when configuration files or secrets are invalid/missing."""


class ContextLimits(BaseModel):
    window_tokens: int = Field(gt=0)
    summarize_threshold_tokens: int = Field(ge=0)
    offload_threshold_tokens: int = Field(default=0, ge=0)
    summarize_enabled: bool = True
    compact_enabled: bool = True
    keep_messages: int = Field(default=20, gt=0)


class CodeFetchConfig(BaseModel):
    ignore_names: list[str] = Field(default_factory=list)
    clone_timeout_seconds: int = Field(default=120, gt=0)


class AgentConfig(BaseModel):
    model: str = Field(min_length=1)
    temperature: float = Field(ge=0.0, le=2.0)
    max_tokens: int = Field(gt=0)
    context: ContextLimits
    code_fetch: CodeFetchConfig = Field(default_factory=CodeFetchConfig)


class OrchestratorPrompts(BaseModel):
    system_prompt: str = Field(min_length=1)


class ParseSubmissionPrompts(BaseModel):
    system_prompt: str = Field(min_length=1)


class ReviewPrompts(BaseModel):
    system_prompt: str = Field(min_length=1)
    feedback_json_schema: str = Field(min_length=1)
    review_user_template: str = Field(min_length=1)


class VerboseOutput(BaseModel):
    show_config: bool = True
    show_plan: bool = False
    show_workspace: bool = False
    show_subagents: bool = False
    show_context_metrics: bool = False


class OutputConfig(BaseModel):
    default_mode: Literal["compact", "verbose"] = "compact"
    verbose: VerboseOutput = Field(default_factory=VerboseOutput)


class YamlConfig(BaseModel):
    agent: AgentConfig
    orchestrator_prompts: OrchestratorPrompts
    parse_submission_prompts: ParseSubmissionPrompts
    review_prompts: ReviewPrompts
    output: OutputConfig


class RuntimeSettings(BaseModel):
    """YAML config plus required runtime secrets from the environment."""

    yaml: YamlConfig
    openrouter_api_key: SecretStr
    log_level: str = "INFO"


def project_root() -> Path:
    """Return `ai-homework-mentor/` root (parent of `src/`)."""
    return Path(__file__).resolve().parents[2]


def config_dir() -> Path:
    return project_root() / "config"


def _read_yaml(path: Path) -> dict[str, object]:
    if not path.is_file():
        msg = f"Missing required config file: {path}"
        raise ConfigError(msg)
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        msg = f"Invalid YAML in {path}: {exc}"
        raise ConfigError(msg) from exc
    if not isinstance(raw, dict):
        msg = f"Config root must be a mapping: {path}"
        raise ConfigError(msg)
    return raw


def load_yaml_config(*, root: Path | None = None) -> YamlConfig:
    """Load and validate YAML configs. Does not require API key."""
    base = (root or project_root()) / "config"
    agent_raw = _read_yaml(base / "agent.yaml")
    prompts_raw = _read_yaml(base / "prompts" / "orchestrator.yaml")
    parse_raw = _read_yaml(base / "prompts" / "parse_submission.yaml")
    review_raw = _read_yaml(base / "prompts" / "review.yaml")
    output_raw = _read_yaml(base / "output.yaml")
    try:
        return YamlConfig(
            agent=AgentConfig.model_validate(agent_raw),
            orchestrator_prompts=OrchestratorPrompts.model_validate(prompts_raw),
            parse_submission_prompts=ParseSubmissionPrompts.model_validate(parse_raw),
            review_prompts=ReviewPrompts.model_validate(review_raw),
            output=OutputConfig.model_validate(output_raw),
        )
    except ValidationError as exc:
        msg = f"Config validation failed: {exc}"
        raise ConfigError(msg) from exc


def load_runtime_settings(
    *,
    root: Path | None = None,
    env_file: Path | None = None,
) -> RuntimeSettings:
    """Load YAML + `.env`. Fails if `OPENROUTER_API_KEY` is missing/empty."""
    project = root or project_root()
    dotenv_path = env_file if env_file is not None else project / ".env"
    if dotenv_path.is_file():
        load_dotenv(dotenv_path, override=False)

    yaml_cfg = load_yaml_config(root=project)
    api_key = os.getenv("OPENROUTER_API_KEY", "").strip()
    if not api_key:
        msg = "OPENROUTER_API_KEY is missing or empty. Copy .env.example to .env and set the key."
        raise ConfigError(msg)

    log_level = os.getenv("LOG_LEVEL", "INFO").strip() or "INFO"
    return RuntimeSettings(
        yaml=yaml_cfg,
        openrouter_api_key=SecretStr(api_key),
        log_level=log_level,
    )
