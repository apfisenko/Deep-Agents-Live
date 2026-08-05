"""Сценарные прогоны фоновой проверки (Sprint 11–12).

Запуск: uv run python examples/run_async_scenarios.py <сценарий>

Сценарии: pitfall | e2e | down

Серверы: companion — SUP_URL (default :2024), checker — CHK_URL
(co-deployed: тот же :2024; распил: :2025).
"""

from __future__ import annotations

import asyncio
import json
import sys
import time
from datetime import datetime
from os import environ

from langgraph_sdk import get_client

SUP_URL = environ.get("SUP_URL", "http://localhost:2024")
CHK_URL = environ.get("CHK_URL", SUP_URL)

HOMEWORK = (
    "Хочу сдать домашку. submission: ../ai-homework-mentor topic: multi-agent. "
    "Запусти фоновую проверку."
)
COURSE_QUESTION = "А что будет в теме 12 курса? Расскажи кратко."

T0 = time.monotonic()


def log(msg: str) -> None:
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{time.monotonic() - T0:7.1f}s {ts}] {msg}", flush=True)


def last_ai_text(values: dict) -> str:
    for m in reversed(values.get("messages", [])):
        if m.get("type") == "ai" and m.get("content") and not m.get("tool_calls"):
            c = m["content"]
            if isinstance(c, list):
                c = " ".join(p.get("text", "") for p in c if isinstance(p, dict))
            return str(c)
    return "(нет AI-ответа)"


async def ask(sup, thread_id: str, text: str) -> tuple[dict, float]:
    log(f">>> студент: {text[:120]!r}")
    started = time.monotonic()
    values = await sup.runs.wait(
        thread_id, "companion", input={"messages": [{"role": "user", "content": text}]}
    )
    took = time.monotonic() - started
    log(f"<<< companion ({took:.1f} с): {last_ai_text(values)[:300]!r}")
    return values, took


def get_task(values: dict) -> dict:
    tasks = values.get("async_tasks") or {}
    assert tasks, "async_tasks пуст — start_async_task не вызывался?"
    task = sorted(tasks.values(), key=lambda t: t["created_at"])[-1]
    log(
        "задача в стейте companion: "
        + json.dumps(
            {k: task[k] for k in ("task_id", "agent_name", "status", "run_id")},
            ensure_ascii=False,
        )
    )
    return task


async def wait_checker_done(chk, thread_id: str, timeout_s: int = 600) -> str:
    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        runs = await chk.runs.list(thread_id)
        statuses = {r["status"] for r in runs}
        if statuses and statuses <= {"success", "error", "interrupted"}:
            return sorted(statuses)[-1]
        await asyncio.sleep(5)
    return "timeout"


async def scenario_pitfall() -> None:
    sup = get_client(url=SUP_URL)
    th = await sup.threads.create()
    log(f"тред companion: {th['thread_id']}")
    values, _ = await ask(sup, th["thread_id"], HOMEWORK)
    get_task(values)
    _, qa_took = await ask(sup, th["thread_id"], COURSE_QUESTION)
    if qa_took < 30:
        log(f"pitfall: PASS — QA ответил за {qa_took:.1f} с (< 30)")
    else:
        log(f"pitfall: FAIL — QA занял {qa_took:.1f} с (ожидали < 30)")
        sys.exit(1)


async def scenario_e2e() -> None:
    sup, chk = get_client(url=SUP_URL), get_client(url=CHK_URL)
    th = await sup.threads.create()
    log(f"тред companion: {th['thread_id']}")

    values, _ = await ask(sup, th["thread_id"], HOMEWORK)
    task = get_task(values)
    _, qa_took = await ask(sup, th["thread_id"], COURSE_QUESTION)
    log(f"QA параллельно check: {qa_took:.1f} с")

    status = await wait_checker_done(chk, task["thread_id"])
    log(f"чекер досчитал: {status}")
    values, _ = await ask(
        sup, th["thread_id"], f"Проверка {task['task_id']} завершена? Забери фидбек через check_async_task."
    )
    final = last_ai_text(values)
    if len(final) > 50:
        log(f"e2e: PASS — фидбек получен ({len(final)} символов)")
    else:
        log(f"e2e: FAIL — короткий ответ: {final!r}")
        sys.exit(1)


async def scenario_down() -> None:
    """Чекер-сервер должен быть ОСТАНОВЛЕН (распил, ступень 3)."""
    sup = get_client(url=SUP_URL)
    th = await sup.threads.create()
    values, _ = await ask(sup, th["thread_id"], HOMEWORK)
    log(f"async_tasks: {json.dumps(values.get('async_tasks') or {}, ensure_ascii=False)}")
    _, qa_took = await ask(sup, th["thread_id"], COURSE_QUESTION)
    log(f"down: QA ответил за {qa_took:.1f} с — companion жив")
    if values.get("async_tasks"):
        log("down: FAIL — phantom async_tasks при недоступном checker")
        sys.exit(1)
    log("down: DONE")


if __name__ == "__main__":
    scenario = sys.argv[1] if len(sys.argv) > 1 else "pitfall"
    asyncio.run(globals()[f"scenario_{scenario}"]())
