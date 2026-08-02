"""CLI REPL для Course Companion.

Запуск: uv run companion
Выход: Ctrl+C или Ctrl+D
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING
from uuid import uuid4

from langchain_core.messages import HumanMessage

if TYPE_CHECKING:
    from langgraph.graph.state import CompiledStateGraph


def _print_router_update(update: dict) -> None:  # type: ignore[type-arg]
    if "router" in update:
        mode = update["router"].get("mode", "?")
        print(f"[router] → {mode}", flush=True)  # noqa: T201


def _print_tools_update(update: dict) -> None:  # type: ignore[type-arg]
    for msg in update.get("messages", []):
        name = getattr(msg, "name", None)
        if name:
            print(f"[tool]   {name}", flush=True)  # noqa: T201


def _print_agent_update(update: dict) -> None:  # type: ignore[type-arg]
    for msg in update.get("messages", []):
        content = getattr(msg, "content", "")
        tool_calls = getattr(msg, "tool_calls", None)
        if content and not tool_calls:
            print(content, flush=True)  # noqa: T201


def _print_chunk(chunk: tuple) -> None:  # type: ignore[type-arg]
    """Форматирует событие графа в строку с тегом.

    Формат chunk при stream_mode="updates", subgraphs=True:
        (namespace_tuple, update_dict)

    LangGraph может вернуть два варианта расположения данных:
    - namespace=("companion",), update={"agent": {...}}    — inner node в ключе update
    - namespace=("companion","agent"), update={...}        — inner node в конце namespace

    Оба варианта обрабатываются.
    """
    namespace, update = chunk

    if not isinstance(update, dict):
        return

    if not namespace:
        _print_router_update(update)
        return

    last_node = namespace[-1]

    if last_node == "agent":
        _print_agent_update(update)
    elif last_node == "tools":
        _print_tools_update(update)
    else:
        # Субграф-обёртка: inner-узлы в ключах update
        if "agent" in update:
            _print_agent_update(update["agent"])
        if "tools" in update:
            _print_tools_update(update["tools"])


def stream_events(graph: CompiledStateGraph, message: str, thread_id: str) -> None:
    """Стримит события графа и выводит теги в реальном времени."""
    config = {"configurable": {"thread_id": thread_id}}
    state = {"messages": [HumanMessage(content=message)]}
    for chunk in graph.stream(  # type: ignore[call-overload]
        state,
        config,
        stream_mode="updates",
        subgraphs=True,
    ):
        _print_chunk(chunk)


def main() -> None:
    """Точка входа REPL."""
    from course_companion.config import Config  # noqa: PLC0415
    from course_companion.graph.graph import build_graph  # noqa: PLC0415

    cfg = Config()
    logging.basicConfig(level=cfg.log_level, format="%(levelname)s %(name)s: %(message)s")

    graph = build_graph()
    thread_id = str(uuid4())
    print("Course Companion v0.1 | Ctrl+C для выхода\n")  # noqa: T201
    while True:
        try:
            user_input = input("Вы: ").strip()
        except (KeyboardInterrupt, EOFError):
            print()  # noqa: T201
            break
        if not user_input:
            continue
        stream_events(graph, user_input, thread_id)
        print()  # noqa: T201
