"""E2E-прогон полного сценария (4 хода одной сессии) с записью лога.

Запуск: uv run python examples/run_session_a2.py [лог-файл]
Сценарий: вопрос по курсу → сдача домашки → разбор фидбека → снова вопрос.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

from companion.cli import stream_turn
from companion.config import PROJECT_ROOT
from companion.graph import build_graph

SUBMISSION = PROJECT_ROOT / "vendor" / "ai-homework-mentor" / "cli"

TURNS = [
    ("а", "Привет! Подскажи, что будет в теме 12 курса?"),
    (
        "б",
        f"Хочу сдать домашку. Вот код: {SUBMISSION} , тема: python-cli. "
        "Все данные дал — отправляй на проверку сразу.",
    ),
    ("в", "Разбери подробнее самое приоритетное замечание из фидбека — что именно не так и как чинить?"),
    ("г", "Спасибо! А когда по программе следующая тема после этой?"),
]


def main() -> int:
    log_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent / "session-log-a2.txt"
    lines: list[str] = []

    def emit(s: str) -> None:
        print(s)
        lines.append(s)

    graph = build_graph()
    config = {"configurable": {"thread_id": "e2e-a2"}, "recursion_limit": 80}
    ok = True
    seen: set[str] = set()

    for label, text in TURNS:
        emit(f"\n=== Ход ({label}) студент: {text}")
        started = time.perf_counter()
        answer, mode = stream_turn(graph, text, config, emit, seen_tool_calls=seen)
        elapsed = time.perf_counter() - started
        emit(f"--- режим после хода: {mode} · {elapsed:.1f}s")
        emit(f"companion: {answer}")
        if not answer:
            ok = False
            emit("!!! пустой ответ")

    log_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nЛог: {log_path}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
