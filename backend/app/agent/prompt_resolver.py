"""Resolve system prompt text from run config."""

from pathlib import Path

from app.agent.prompt_registry import PROMPT_FILES, load_named_prompt
from app.agent.run_config import PromptSection
from app.exceptions import ConfigNotFoundError
from app.paths import REPO_ROOT


def _resolve_repo_path(path_str: str) -> Path:
    path = Path(path_str)
    if not path.is_absolute():
        path = REPO_ROOT / path
    return path.resolve()


def _load_prompt_file(path_str: str) -> str:
    path = _resolve_repo_path(path_str)
    if not path.is_file():
        msg = f"Prompt file not found: {path}"
        raise ConfigNotFoundError(msg, config_id=path_str)
    return path.read_text(encoding="utf-8").strip()


def resolve_prompt(prompt: PromptSection) -> str:
    if prompt.source == "file":
        if prompt.path:
            resolved = _resolve_repo_path(prompt.path)
            if resolved.is_file() and resolved.suffix != ".py":
                return _load_prompt_file(prompt.path)
        if prompt.name in PROMPT_FILES:
            return load_named_prompt(prompt.name)
        msg = f"Unknown file prompt name: {prompt.name}"
        raise ConfigNotFoundError(msg, config_id=prompt.name)
    msg = "Langfuse prompt source is not implemented yet (E-10)"
    raise ConfigNotFoundError(msg, config_id=prompt.name)
