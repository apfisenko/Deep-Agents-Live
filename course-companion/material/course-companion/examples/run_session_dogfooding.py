"""Dogfooding-прогон с записью лога: сдаём companion'у его собственный код.

Запуск: uv run python examples/run_session_dogfooding.py [лог-файл]
Система проверяет пакет companion/ по рубрике multi-agent — домашку по теме,
частью которой сама является.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

from companion.cli import stream_turn
from companion.config import PROJECT_ROOT
from companion.graph import build_graph

SUBMISSION = PROJECT_ROOT / "companion"

TURN = (
    f'Хочу сдать домашку по теме "мультиагентные паттерны". '
    f"Код лежит тут: {SUBMISSION} — все данные дал, отправляй на проверку сразу."
)


def main() -> int:
    log_path = (
        Path(sys.argv[1])
        if len(sys.argv) > 1
        else Path(__file__).parent / "session-log-dogfooding.txt"
    )
    lines: list[str] = []

    def emit(s: str) -> None:
        print(s)
        lines.append(s)

    graph = build_graph()
    config = {"configurable": {"thread_id": "e2e-dogfooding"}, "recursion_limit": 80}

    emit(f"=== студент: {TURN}")
    started = time.perf_counter()
    answer, mode = stream_turn(graph, TURN, config, emit, seen_tool_calls=set())
    elapsed = time.perf_counter() - started
    emit(f"--- режим после хода: {mode} · {elapsed:.1f}s")
    emit(f"companion: {answer}")

    log_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    ok = mode == "homework" and bool(answer)
    print(f"\n{'OK' if ok else 'FAIL'}: лог → {log_path}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
