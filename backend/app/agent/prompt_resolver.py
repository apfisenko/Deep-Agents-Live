"""Resolve system prompt text from run config."""

from app.agent.prompts import (
    SYSTEM_PROMPT,
    SYSTEM_PROMPT_SEARCH_FALLBACK,
    SYSTEM_PROMPT_SEARCH_FIRST,
)
from app.agent.run_config import PromptSection
from app.exceptions import ConfigNotFoundError

_FILE_PROMPTS: dict[str, str] = {
    "SYSTEM_PROMPT": SYSTEM_PROMPT,
    "SYSTEM_PROMPT_SEARCH_FIRST": SYSTEM_PROMPT_SEARCH_FIRST,
    "SYSTEM_PROMPT_SEARCH_FALLBACK": SYSTEM_PROMPT_SEARCH_FALLBACK,
}


def resolve_prompt(prompt: PromptSection) -> str:
    if prompt.source == "file":
        if prompt.name in _FILE_PROMPTS:
            return _FILE_PROMPTS[prompt.name]
        msg = f"Unknown file prompt name: {prompt.name}"
        raise ConfigNotFoundError(msg, config_id=prompt.name)
    msg = "Langfuse prompt source is not implemented yet (E-10)"
    raise ConfigNotFoundError(msg, config_id=prompt.name)
