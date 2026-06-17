"""Registry of named system prompt files (eval + production)."""

from functools import lru_cache

from app.paths import AGENT_PROMPTS_DIR

PROMPT_FILES: dict[str, str] = {
    "SYSTEM_PROMPT": "SYSTEM_PROMPT.txt",
    "SYSTEM_PROMPT_SEARCH_FIRST": "SYSTEM_PROMPT_SEARCH_FIRST.txt",
    "SYSTEM_PROMPT_SEARCH_FALLBACK": "SYSTEM_PROMPT_SEARCH_FALLBACK.txt",
}


def prompt_file_path(name: str) -> str:
    filename = PROMPT_FILES.get(name)
    if filename is None:
        msg = f"Unknown prompt name: {name}"
        raise KeyError(msg)
    return str((AGENT_PROMPTS_DIR / filename).resolve())


@lru_cache(maxsize=len(PROMPT_FILES))
def load_named_prompt(name: str) -> str:
    path = AGENT_PROMPTS_DIR / PROMPT_FILES[name]
    return path.read_text(encoding="utf-8").strip()
