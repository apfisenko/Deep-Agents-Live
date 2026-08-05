"""Configuration for AI Homework Mentor."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = PROJECT_ROOT / "config"


def _load_env_files() -> None:
    load_dotenv(PROJECT_ROOT / ".env")
    load_dotenv(PROJECT_ROOT.parent / ".env")


def load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        msg = f"Config file not found: {path}"
        raise FileNotFoundError(msg)
    with path.open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    if not isinstance(data, dict):
        msg = f"Invalid YAML config (expected mapping): {path}"
        raise ValueError(msg)
    return data


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=None,
        extra="ignore",
    )

    openai_api_key: str = Field(validation_alias="OPENAI_API_KEY")
    openai_base_url: str = Field(
        default="https://openrouter.ai/api/v1",
        validation_alias="OPENAI_BASE_URL",
    )
    openai_model: str = Field(
        default="google/gemini-3.5-flash",
        validation_alias="OPENAI_MODEL",
    )
    log_level: str = Field(default="INFO", validation_alias="LOG_LEVEL")

    @field_validator("openai_api_key")
    @classmethod
    def api_key_required(cls, value: str) -> str:
        if not value or value.startswith("sk-or-v1-..."):
            msg = (
                "OPENAI_API_KEY is missing or placeholder. "
                "Set it in ai-homework-mentor/.env or repo root .env"
            )
            raise ValueError(msg)
        return value


class AppConfig:
    def __init__(self, settings_path: Path | None = None) -> None:
        _load_env_files()
        self.settings = Settings()
        self.yaml = load_yaml(settings_path or CONFIG_DIR / "settings.yaml")
        self.project_root = PROJECT_ROOT
        self.config_dir = CONFIG_DIR

    @property
    def max_tokens(self) -> int:
        return int(self.yaml.get("llm", {}).get("max_tokens", 4096))

    @property
    def temperature(self) -> float:
        return float(self.yaml.get("llm", {}).get("temperature", 0.2))

    @property
    def workspace_base(self) -> Path:
        rel = self.yaml.get("workspace", {}).get("base_dir", ".mentor-workspace")
        return PROJECT_ROOT / rel

    @property
    def summarization_trigger_fraction(self) -> float:
        return float(self.yaml.get("context", {}).get("summarization_trigger_fraction", 0.55))

    @property
    def max_context_tokens(self) -> int:
        return int(self.yaml.get("context", {}).get("max_context_tokens", 128_000))

    @property
    def s03_single_agent_peak_tokens(self) -> int:
        return int(self.yaml.get("context", {}).get("s03_single_agent_peak_tokens", 9000))

    @property
    def log_format(self) -> str:
        return str(self.yaml.get("logging", {}).get("format", "human"))

    def load_prompt(self, name: str) -> str:
        path = CONFIG_DIR / "prompts" / f"{name}.yaml"
        data = load_yaml(path)
        prompt = data.get("system")
        if not isinstance(prompt, str) or not prompt.strip():
            msg = f"Prompt 'system' missing in {path}"
            raise ValueError(msg)
        return prompt.strip()

    def list_rubrics(self) -> list[Path]:
        return sorted((CONFIG_DIR / "rubrics").glob("*.yaml"))


@lru_cache(maxsize=1)
def get_config() -> AppConfig:
    return AppConfig()
