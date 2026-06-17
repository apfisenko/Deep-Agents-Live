"""Tests for prompt resolution from run config."""

from app.agent.prompt_registry import load_named_prompt
from app.agent.prompt_resolver import resolve_prompt
from app.agent.run_config import PromptSection
from app.paths import AGENT_PROMPTS_DIR, DEFAULT_SYSTEM_PROMPT_PATH


def test_resolve_default_prompt_by_name() -> None:
    section = PromptSection(
        source="file",
        name="SYSTEM_PROMPT",
        path="backend/app/agent/prompts/SYSTEM_PROMPT.txt",
    )
    assert resolve_prompt(section) == load_named_prompt("SYSTEM_PROMPT")


def test_resolve_search_first_prompt() -> None:
    section = PromptSection(
        source="file",
        name="SYSTEM_PROMPT_SEARCH_FIRST",
        path="backend/app/agent/prompts/SYSTEM_PROMPT_SEARCH_FIRST.txt",
    )
    text = resolve_prompt(section)
    assert text == load_named_prompt("SYSTEM_PROMPT_SEARCH_FIRST")
    assert "search_knowledge_base" in text
    assert "уточняющие вопросы" in text


def test_resolve_search_fallback_prompt() -> None:
    section = PromptSection(
        source="file",
        name="SYSTEM_PROMPT_SEARCH_FALLBACK",
        path="backend/app/agent/prompts/SYSTEM_PROMPT_SEARCH_FALLBACK.txt",
    )
    text = resolve_prompt(section)
    assert text == load_named_prompt("SYSTEM_PROMPT_SEARCH_FALLBACK")
    assert "list_b2c_products" in text
    assert "search_knowledge_base" in text


def test_resolve_system_prompt_txt_file() -> None:
    section = PromptSection(
        source="file",
        name="SYSTEM_PROMPT_SEARCH_FALLBACK",
        path="backend/app/agent/prompts/SYSTEM_PROMPT_SEARCH_FALLBACK.txt",
    )
    text = resolve_prompt(section)
    assert "search_knowledge_base" in text
    assert "list_b2c_products" in text
    assert text == DEFAULT_SYSTEM_PROMPT_PATH.read_text(encoding="utf-8").strip()
    assert AGENT_PROMPTS_DIR.is_dir()
