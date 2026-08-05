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


def _find_mode_in_update(obj: object) -> str | None:
    """Извлечь mode из nested update dict (router, tools Command, subgraph)."""
    if not isinstance(obj, dict):
        return None
    mode = obj.get("mode")
    if isinstance(mode, str):
        return mode
    for value in obj.values():
        found = _find_mode_in_update(value)
        if found is not None:
            return found
    return None


class _ModeTracker:
    """Отслеживает смену mode между ходами и внутри stream-чанков."""

    def __init__(self, initial: str = "qa") -> None:
        self._mode = initial

    @property
    def mode(self) -> str:
        return self._mode

    def observe(self, update: dict) -> None:  # type: ignore[type-arg]
        new_mode = _find_mode_in_update(update)
        if new_mode is None or new_mode == self._mode:
            return
        print(f"[mode]   {self._mode} → {new_mode}", flush=True)  # noqa: T201
        self._mode = new_mode


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


def _print_chunk(chunk: tuple, mode_tracker: _ModeTracker) -> None:  # type: ignore[type-arg]
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

    mode_tracker.observe(update)

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


def _initial_mode(graph: CompiledStateGraph, config: dict) -> str:  # type: ignore[type-arg]
    snapshot = graph.get_state(config)  # type: ignore[arg-type]
    if snapshot.values:
        return str(snapshot.values.get("mode") or "qa")
    return "qa"


def stream_events(
    graph: CompiledStateGraph,
    message: str,
    thread_id: str,
    mode_tracker: _ModeTracker | None = None,
) -> _ModeTracker:
    """Стримит события графа и выводит теги в реальном времени."""
    config = {"configurable": {"thread_id": thread_id}}
    tracker = mode_tracker or _ModeTracker(_initial_mode(graph, config))
    state = {"messages": [HumanMessage(content=message)]}
    for chunk in graph.stream(  # type: ignore[call-overload]
        state,
        config,
        stream_mode="updates",
        subgraphs=True,
    ):
        _print_chunk(chunk, tracker)
    return tracker


def main() -> None:
    """Точка входа REPL."""
    from course_companion.config import Config  # noqa: PLC0415
    from course_companion.graph.graph import build_graph  # noqa: PLC0415

    cfg = Config()
    logging.basicConfig(level=cfg.log_level, format="%(levelname)s %(name)s: %(message)s")

    graph = build_graph()
    thread_id = str(uuid4())
    mode_tracker: _ModeTracker | None = None
    print("Course Companion v0.1 | Ctrl+C для выхода\n")  # noqa: T201
    while True:
        try:
            user_input = input("Вы: ").strip()
        except (KeyboardInterrupt, EOFError):
            print()  # noqa: T201
            break
        if not user_input:
            continue
        mode_tracker = stream_events(graph, user_input, thread_id, mode_tracker)
        print()  # noqa: T201
