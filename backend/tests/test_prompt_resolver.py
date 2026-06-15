"""Tests for prompt resolution from run config."""

from app.agent.prompt_resolver import resolve_prompt
from app.agent.prompts import SYSTEM_PROMPT, SYSTEM_PROMPT_SEARCH_FIRST
from app.agent.run_config import PromptSection


def test_resolve_default_prompt() -> None:
    section = PromptSection(
        source="file",
        name="SYSTEM_PROMPT",
        path="backend/app/agent/prompts.py",
    )
    assert resolve_prompt(section) == SYSTEM_PROMPT


def test_resolve_search_first_prompt() -> None:
    section = PromptSection(
        source="file",
        name="SYSTEM_PROMPT_SEARCH_FIRST",
        path="backend/app/agent/prompts.py",
    )
    text = resolve_prompt(section)
    assert text == SYSTEM_PROMPT_SEARCH_FIRST
    assert "search_knowledge_base" in text
    assert "уточняющие вопросы" in text
