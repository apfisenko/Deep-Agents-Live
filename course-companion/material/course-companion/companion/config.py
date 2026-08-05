"""Конфигурация Course Companion.

Лёгкий слой поверх env: не дублируем AppConfig ментора — его конфиг
(`mentor.config.get_config`) живёт своей жизнью и сам подхватывает
vendor/ai-homework-mentor/.env. Здесь — только то, что нужно верхнему агенту.
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

PROJECT_ROOT = Path(__file__).resolve().parents[1]
WORKSPACE_DIR = PROJECT_ROOT / ".companion-workspace"

load_dotenv(PROJECT_ROOT / ".env")

DEFAULT_BASE_URL = "https://openrouter.ai/api/v1"
DEFAULT_MODEL = "google/gemini-3.5-flash"
MAX_CONTEXT_TOKENS = 128_000


def build_model(max_tokens: int = 4096, temperature: float = 0.2) -> ChatOpenAI:
    """Модель верхнего агента — тот же OpenRouter-стек, что у ментора."""
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key or api_key.startswith("sk-or-v1-..."):
        msg = "OPENAI_API_KEY не задан: скопируй .env.example в .env и заполни"
        raise ValueError(msg)
    return ChatOpenAI(
        model=os.environ.get("OPENAI_MODEL", DEFAULT_MODEL),
        api_key=api_key,
        base_url=os.environ.get("OPENAI_BASE_URL", DEFAULT_BASE_URL),
        max_tokens=max_tokens,
        temperature=temperature,
        profile={"max_input_tokens": MAX_CONTEXT_TOKENS},
    )
