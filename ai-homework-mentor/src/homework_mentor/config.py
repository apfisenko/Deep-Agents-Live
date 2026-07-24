"""Configuration schemas and YAML/env loading (fail-fast)."""

from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal

import yaml
from dotenv import load_dotenv
from pydantic import BaseModel, Field, SecretStr, ValidationError

if TYPE_CHECKING:
    from langchain_core.language_models import BaseChatModel

DEFAULT_OPENROUTER_API_BASE = "https://openrouter.ai/api/v1"

ReviewMode = Literal["single", "subagents"]
DEFAULT_REVIEW_MODE: ReviewMode = "subagents"
REVIEW_MODE_VALUES: tuple[ReviewMode, ...] = ("single", "subagents")


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
    single_system_prompt: str = Field(min_length=1)
    single_review_user_template: str = Field(min_length=1)


class SynthesisReflectionPrompts(BaseModel):
    system_prompt: str = Field(min_length=1)
    user_template: str = Field(min_length=1)


class SynthesisFinalPrompts(BaseModel):
    system_prompt: str = Field(min_length=1)
    user_template: str = Field(min_length=1)


class VerboseOutput(BaseModel):
    show_config: bool = True
    show_plan: bool = False
    show_workspace: bool = False
    show_subagents: bool = False
    show_context_metrics: bool = False
    show_skills: bool = False
    show_synthesis: bool = True


class OutputConfig(BaseModel):
    default_mode: Literal["compact", "verbose"] = "compact"
    verbose: VerboseOutput = Field(default_factory=VerboseOutput)


class YamlConfig(BaseModel):
    agent: AgentConfig
    orchestrator_prompts: OrchestratorPrompts
    parse_submission_prompts: ParseSubmissionPrompts
    review_prompts: ReviewPrompts
    synthesis_reflection_prompts: SynthesisReflectionPrompts
    synthesis_final_prompts: SynthesisFinalPrompts
    output: OutputConfig


class RuntimeSettings(BaseModel):
    """YAML config plus required runtime secrets from the environment."""

    yaml: YamlConfig
    openrouter_api_key: SecretStr
    openrouter_api_base: str | None = None
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
    reflection_raw = _read_yaml(base / "prompts" / "synthesis_reflection.yaml")
    final_raw = _read_yaml(base / "prompts" / "synthesis_final.yaml")
    output_raw = _read_yaml(base / "output.yaml")
    try:
        return YamlConfig(
            agent=AgentConfig.model_validate(agent_raw),
            orchestrator_prompts=OrchestratorPrompts.model_validate(prompts_raw),
            parse_submission_prompts=ParseSubmissionPrompts.model_validate(parse_raw),
            review_prompts=ReviewPrompts.model_validate(review_raw),
            synthesis_reflection_prompts=SynthesisReflectionPrompts.model_validate(
                reflection_raw,
            ),
            synthesis_final_prompts=SynthesisFinalPrompts.model_validate(final_raw),
            output=OutputConfig.model_validate(output_raw),
        )
    except ValidationError as exc:
        msg = f"Config validation failed: {exc}"
        raise ConfigError(msg) from exc


def _resolve_openrouter_api_base() -> str | None:
    """Read OpenRouter base URL from `.env` (`OPENROUTER_API_BASE` or `OPENROUTER_URL`)."""
    for key in ("OPENROUTER_API_BASE", "OPENROUTER_URL"):
        value = os.getenv(key, "").strip()
        if value:
            return value.rstrip("/")
    return None


def apply_openrouter_process_env(settings: RuntimeSettings) -> None:
    """Sync OpenRouter client env vars for SDKs that read process environment."""
    os.environ["OPENROUTER_API_KEY"] = settings.openrouter_api_key.get_secret_value()
    if settings.openrouter_api_base:
        os.environ["OPENROUTER_API_BASE"] = settings.openrouter_api_base


def init_openrouter_chat_model(
    settings: RuntimeSettings,
    *,
    temperature: float | None = None,
    max_tokens: int | None = None,
) -> BaseChatModel:
    """Build chat model from runtime settings and optional per-call overrides."""
    from langchain.chat_models import init_chat_model  # noqa: PLC0415 — lazy import

    agent_cfg = settings.yaml.agent
    kwargs: dict[str, Any] = {
        "api_key": settings.openrouter_api_key.get_secret_value(),
        "temperature": agent_cfg.temperature if temperature is None else temperature,
        "max_tokens": agent_cfg.max_tokens if max_tokens is None else max_tokens,
    }
    if settings.openrouter_api_base:
        kwargs["base_url"] = settings.openrouter_api_base
    return init_chat_model(agent_cfg.model, **kwargs)


def _normalize_openrouter_model(model: str) -> str:
    """Ensure OpenRouter model id includes provider prefix for LangChain."""
    cleaned = model.strip()
    if not cleaned or cleaned.startswith("openrouter:"):
        return cleaned
    return f"openrouter:{cleaned}"


def _apply_env_agent_overrides(cfg: YamlConfig) -> YamlConfig:
    """Optional overrides from `.env` (OPENROUTER_MODEL, temperature, max_tokens)."""
    updates: dict[str, object] = {}
    model = os.getenv("OPENROUTER_MODEL", "").strip()
    if model:
        updates["model"] = _normalize_openrouter_model(model)
    temperature = os.getenv("OPENROUTER_TEMPERATURE", "").strip()
    if temperature:
        updates["temperature"] = float(temperature)
    max_tokens = os.getenv("OPENROUTER_MAX_TOKENS", "").strip()
    if max_tokens:
        updates["max_tokens"] = int(max_tokens)
    if not updates:
        return cfg
    agent = cfg.agent.model_copy(update=updates)
    return cfg.model_copy(update={"agent": agent})


def resolve_review_mode(cli_value: str | None = None) -> ReviewMode:
    """Resolve review mode: CLI > env ``REVIEW_MODE`` > default ``subagents``."""
    raw = (cli_value or "").strip() or os.getenv("REVIEW_MODE", "").strip()
    if not raw:
        return DEFAULT_REVIEW_MODE
    normalized = raw.lower()
    for mode in REVIEW_MODE_VALUES:
        if normalized == mode:
            return mode
    allowed = ", ".join(REVIEW_MODE_VALUES)
    msg = f"Invalid review mode {raw!r}. Allowed: {allowed}"
    raise ConfigError(msg)


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

    yaml_cfg = _apply_env_agent_overrides(load_yaml_config(root=project))
    api_key = os.getenv("OPENROUTER_API_KEY", "").strip()
    if not api_key:
        msg = "OPENROUTER_API_KEY is missing or empty. Copy .env.example to .env and set the key."
        raise ConfigError(msg)

    log_level = os.getenv("LOG_LEVEL", "INFO").strip() or "INFO"
    return RuntimeSettings(
        yaml=yaml_cfg,
        openrouter_api_key=SecretStr(api_key),
        openrouter_api_base=_resolve_openrouter_api_base(),
        log_level=log_level,
    )
