"""AsyncSubAgent — фоновая проверка ДЗ через Agent Protocol.

Co-deployed: оба графа в одном langgraph.json, без url — in-process транспорт.
Распил: env CHECKER_URL=http://localhost:2025 — HTTP-транспорт.
"""

from __future__ import annotations

import os

from deepagents import AsyncSubAgent, CompiledSubAgent

from course_companion.subagents.homework_checker import build_homework_checker_graph

CHECKER_DESCRIPTION = (
    "Проверяет домашку студента по рубрике курса. Работает автономно "
    "несколько минут. В description передай СТРОГО две строки:\n"
    "submission: <локальный путь или GitHub URL>\n"
    "topic: <тема домашки>"
)

ASYNC_CHECKER_DESCRIPTION = (
    "Фоновая проверка домашки студента по рубрике курса (несколько минут, "
    "с пользователем не разговаривает). В description передай СТРОГО "
    "две строки:\n"
    "submission: <локальный путь или GitHub URL>\n"
    "topic: <тема домашки>"
)


def build_homework_checker_subagent() -> CompiledSubAgent:
    """Синхронный CompiledSubAgent для CLI (блокирует ход до вердикта)."""
    return CompiledSubAgent(
        name="homework-checker",
        description=CHECKER_DESCRIPTION,
        runnable=build_homework_checker_graph(),
    )


def build_async_checker() -> AsyncSubAgent:
    """AsyncSubAgent — ссылка на граф checker в langgraph.json."""
    checker = AsyncSubAgent(
        name="homework-checker-async",
        description=ASYNC_CHECKER_DESCRIPTION,
        graph_id="checker",
    )
    url = os.environ.get("CHECKER_URL")
    if url:
        checker["url"] = url
    return checker
