"""Сценарные прогоны фоновой проверки (ступени 2–3). Логи — в examples/phase2/.

Запуск: uv run python examples/run_async_scenarios.py <сценарий>

Сценарии:
  pitfall  — грабля слотов воркера: сдал домашку → сразу вопрос о курсе.
             На дефолтном dev-сервере (1 слот!) вопрос висит, пока чекер
             не освободит слот; с --n-jobs-per-worker 10 — отвечает сразу.
  e2e      — сдал → вопрос о курсе (чат свободен) → дождались чекера →
             забрали фидбек.
  steering — дослать инструкцию бегущей проверке (update = ПЕРЕЗАПУСК
             рана на том же треде с полной историей).
  cancel   — отменить бегущую проверку; показать маппинг статусов на шве
             (чекер: interrupted, companion: cancelled).
  down     — чекер-сервер остановлен: старт задачи возвращает текстовую
             ошибку, companion жив (мягкий отказ распределёнки).

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
    "Сдаю домашку: код в vendor/ai-homework-mentor/cli, тема python-cli. "
    "Запусти проверку."
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


async def ask(sup, thread_id: str, text: str) -> dict:
    """Сообщение companion'у + ожидание конца рана; печатает длительность."""
    log(f">>> студент: {text[:120]!r}")
    started = time.monotonic()
    values = await sup.runs.wait(
        thread_id, "companion", input={"messages": [{"role": "user", "content": text}]}
    )
    took = time.monotonic() - started
    log(f"<<< companion ({took:.1f} с): {last_ai_text(values)[:300]!r}")
    return values


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


async def checker_run_statuses(chk, thread_id: str) -> list[dict]:
    runs = await chk.runs.list(thread_id)
    out = [{"run_id": r["run_id"][-12:], "status": r["status"]} for r in runs]
    log(f"раны на сервере чекера (тред …{thread_id[-12:]}): {json.dumps(out)}")
    return out


async def wait_checker_done(chk, thread_id: str, timeout_s: int = 600) -> str:
    """Подождать терминального статуса последнего рана чекера."""
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
    values = await ask(sup, th["thread_id"], HOMEWORK)
    get_task(values)
    # Сразу спрашиваем о курсе. Если ответ приходит за секунды — слотов
    # хватает; если висит до конца проверки — async выродился в sync.
    await ask(sup, th["thread_id"], COURSE_QUESTION)
    log("pitfall: DONE (смотри длительность второго ответа)")


async def scenario_e2e() -> None:
    sup, chk = get_client(url=SUP_URL), get_client(url=CHK_URL)
    th = await sup.threads.create()
    log(f"тред companion: {th['thread_id']}")

    values = await ask(sup, th["thread_id"], HOMEWORK)
    task = get_task(values)
    await checker_run_statuses(chk, task["thread_id"])

    # чат свободен, пока чекер работает
    await ask(sup, th["thread_id"], COURSE_QUESTION)

    status = await wait_checker_done(chk, task["thread_id"])
    log(f"чекер досчитал: {status}")
    values = await ask(sup, th["thread_id"], "Как там проверка? Покажи фидбек.")
    log("e2e: DONE")


async def scenario_steering() -> None:
    sup, chk = get_client(url=SUP_URL), get_client(url=CHK_URL)
    th = await sup.threads.create()
    values = await ask(sup, th["thread_id"], HOMEWORK)
    task = get_task(values)
    run_before = task["run_id"]

    await asyncio.sleep(15)  # проверка в разгаре
    await checker_run_statuses(chk, task["thread_id"])
    values = await ask(
        sup,
        th["thread_id"],
        f"Дошли проверяющему инструкцию к задаче {task['task_id']}: "
        "оценивай строго по PEP8 и обязательно включи слово БАНАН в вердикт.",
    )
    task2 = get_task(values)
    log(
        f"run_id до: …{run_before[-12:]}, после: …{task2['run_id'][-12:]} "
        f"(тот же тред: {task2['thread_id'] == task['thread_id']}) — "
        "update = перезапуск рана, проверка начинается заново"
    )
    await checker_run_statuses(chk, task["thread_id"])

    status = await wait_checker_done(chk, task["thread_id"])
    log(f"новый ран досчитал: {status}")
    values = await ask(
        sup, th["thread_id"], "Проверь статус и покажи финальный вердикт проверки."
    )
    final = last_ai_text(values)
    log(f"steering: слово БАНАН в ответе: {'БАНАН' in final.upper()}")
    log("steering: DONE")


async def scenario_cancel() -> None:
    sup, chk = get_client(url=SUP_URL), get_client(url=CHK_URL)
    th = await sup.threads.create()
    values = await ask(sup, th["thread_id"], HOMEWORK)
    task = get_task(values)

    await asyncio.sleep(10)
    values = await ask(
        sup, th["thread_id"], f"Отмени проверку {task['task_id']}, она не нужна."
    )
    get_task(values)  # companion: cancelled
    await asyncio.sleep(2)
    # на сервере чекера тот же ран — interrupted: статусы расходятся на шве
    await checker_run_statuses(chk, task["thread_id"])
    await ask(sup, th["thread_id"], "Покажи список всех задач с их статусами.")
    log("cancel: DONE")


async def scenario_down() -> None:
    """Чекер-сервер должен быть ОСТАНОВЛЕН (распил, ступень 3)."""
    sup = get_client(url=SUP_URL)
    th = await sup.threads.create()
    values = await ask(sup, th["thread_id"], HOMEWORK)
    log(f"async_tasks: {json.dumps(values.get('async_tasks') or {}, ensure_ascii=False)}")
    # companion жив: обычный вопрос отвечается как ни в чём не бывало
    await ask(sup, th["thread_id"], COURSE_QUESTION)
    log("down: DONE")


if __name__ == "__main__":
    scenario = sys.argv[1] if len(sys.argv) > 1 else "e2e"
    asyncio.run(globals()[f"scenario_{scenario}"]())
