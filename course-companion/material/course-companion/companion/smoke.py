"""Smoke-прогон скелета v0: одно сообщение → делегирование → отчёт.

Запуск: uv run python -m companion.smoke [путь-к-сдаче] [тема]
"""

from __future__ import annotations

import sys
import time

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from companion.agent import build_companion
from companion.config import PROJECT_ROOT


def main() -> int:
    submission = sys.argv[1] if len(sys.argv) > 1 else str(
        PROJECT_ROOT / "vendor" / "ai-homework-mentor" / "cli"
    )
    topic = sys.argv[2] if len(sys.argv) > 2 else "python-cli"

    agent = build_companion()
    user_text = (
        f"Привет! Проверь мою домашку, вот код: {submission} , тема: {topic}. "
        "Все данные я дал — делегируй сразу."
    )
    print(f">>> {user_text}\n")

    started = time.perf_counter()
    state = agent.invoke(
        # mode задаём напрямую: smoke бьёт в companion мимо router'а
        {"messages": [HumanMessage(content=user_text)], "mode": "homework"},
        config={"recursion_limit": 50},
    )
    elapsed = time.perf_counter() - started

    task_calls = 0
    for msg in state["messages"]:
        if isinstance(msg, AIMessage) and msg.tool_calls:
            for call in msg.tool_calls:
                args = str(call.get("args", ""))[:160]
                print(f"[tool_call] {call['name']}({args})")
                if call["name"] == "task":
                    task_calls += 1
        elif isinstance(msg, ToolMessage):
            print(f"[tool_result:{msg.name}] {str(msg.content)[:160].replace(chr(10), ' ')}")

    final = state["messages"][-1]
    final_text = final.content if isinstance(final.content, str) else str(final.content)
    print(f"\n=== Финальный ответ companion ({elapsed:.1f}s, task-вызовов: {task_calls}) ===")
    print(final_text)

    if task_calls == 0:
        print("\nFAIL: делегирование через task не произошло")
        return 1
    print("\nOK: E2E сдал→делегировал→фидбек")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
