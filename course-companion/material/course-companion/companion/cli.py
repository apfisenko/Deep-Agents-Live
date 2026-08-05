"""CLI-чат Course Companion: REPL со стримингом делегирований.

Запуск: `uv run companion` (или `uv run python -m companion.cli`).
Выход: /exit. В приглашении виден текущий режим; по ходу видно решения
роутера, переключения режимов и работу субагентов.

Стриминг — `stream_mode="updates", subgraphs=True`: стабильный низкоуровневый
API LangGraph; апдейты внешних узлов (router) приходят с пустым namespace,
внутренности companion — с namespace подграфа. Внутренний агент ментора свои
события не стримит (он вызывается внутри узла адаптера без прокидывания
стрим-конфига) — виден как один длинный task-вызов, это ожидаемо.
"""

from __future__ import annotations

import uuid
from typing import Callable

from langchain_core.messages import AIMessage, ToolMessage
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from companion.graph import build_graph
from companion.modes import DEFAULT_MODE

_TRANSITION_TOOLS = {"enter_review", "back_to_qa"}


def stream_turn(
    graph,
    user_text: str,
    config: dict,
    emit: Callable[[str], None],
    seen_tool_calls: set[str] | None = None,
) -> tuple[str, str]:
    """Прогнать один ход через граф, эмитя события; вернуть (ответ, режим).

    `seen_tool_calls` передавай один на сессию: финальный update внешнего узла
    companion несёт полную историю messages (add_messages подграфа), без
    сквозного дедупа события прошлых ходов печатались бы заново.
    """
    seen_tool_calls = set() if seen_tool_calls is None else seen_tool_calls
    for namespace, chunk in graph.stream(
        {"messages": [("user", user_text)]},
        config=config,
        stream_mode="updates",
        subgraphs=True,
    ):
        for node, update in chunk.items():
            if not isinstance(update, dict):
                continue
            if not namespace:
                # внешний уровень: router рисуем, финальный дамп companion — нет
                if node == "router":
                    emit(f"[router] режим → {update.get('mode', '?')}")
                continue
            for msg in update.get("messages", []) or []:
                if isinstance(msg, AIMessage) and msg.tool_calls:
                    for call in msg.tool_calls:
                        if call["id"] in seen_tool_calls:
                            continue
                        seen_tool_calls.add(call["id"])
                        name = call["name"]
                        args = call.get("args", {})
                        if name == "task":
                            emit(
                                f"[task] → субагент {args.get('subagent_type', '?')}: "
                                f"{str(args.get('description', ''))[:100]}…"
                            )
                        elif name in _TRANSITION_TOOLS:
                            emit(f"[handoff] {name}")
                        else:
                            emit(f"[tool] {name}")
                elif isinstance(msg, ToolMessage) and msg.name == "task":
                    emit("[task] ✓ субагент вернул результат")

    state = graph.get_state(config)
    mode = state.values.get("mode", DEFAULT_MODE)
    answer = ""
    for msg in reversed(state.values.get("messages", [])):
        if isinstance(msg, AIMessage) and not msg.tool_calls:
            answer = msg.content if isinstance(msg.content, str) else str(msg.content)
            break
    return answer, mode


def main() -> None:
    console = Console()
    graph = build_graph()
    thread_id = uuid.uuid4().hex[:8]
    config = {"configurable": {"thread_id": thread_id}, "recursion_limit": 80}
    mode = DEFAULT_MODE
    seen: set[str] = set()

    console.print(
        Panel(
            "Course Companion — ассистент студента курса Deep Agents.\n"
            "Задавай вопросы по курсу или сдавай домашку. Выход: /exit",
            title="companion",
        )
    )
    while True:
        try:
            user_text = console.input(f"[bold cyan]{mode}>[/] ")
        except (EOFError, KeyboardInterrupt):
            break
        if not user_text.strip():
            continue
        if user_text.strip() in {"/exit", "/quit"}:
            break
        with console.status("[dim]думаю…[/]"):
            answer, mode = stream_turn(
                graph,
                user_text,
                config,
                emit=lambda s: console.print(s, style="dim", markup=False),
                seen_tool_calls=seen,
            )
        console.print(Panel(Markdown(answer or "(пустой ответ)"), border_style="cyan"))

    console.print("[dim]Пока![/]")


if __name__ == "__main__":
    main()
