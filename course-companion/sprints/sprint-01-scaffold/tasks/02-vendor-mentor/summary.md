# Summary — Task 02: vendor-mentor

**Статус:** ✅ Done  
**Дата:** 2026-08-02

---

## Что сделано

- `pyproject.toml`: `homework-mentor` в dependencies + `[tool.uv.sources]` editable path
- `src/mentor/__init__.py`, `src/mentor/agent/__init__.py`
- `src/mentor/agent/orchestrator.py` — `MentorOrchestrator` stub (вариант 2)
- `tests/__init__.py`, `tests/test_smoke.py`

## Решение по импорту (вариант 2)

README описывал `from mentor.agent.orchestrator import MentorOrchestrator`, но класса в `homework_mentor` нет. Создан пакет `src/mentor/` как тонкая обёртка над `homework_mentor.orchestrator`. Оба пакета (`course_companion`, `mentor`) auto-discovered `uv_build` из `src/`.

`MentorOrchestrator` в Sprint 01 — stub с ссылками на `run_review` и `ReviewRunResult`. В Sprint 02 расширяется до CompiledSubAgent-адаптера.

## DoD

| # | Критерий | Результат |
|---|----------|-----------|
| 1 | `homework-mentor` editable | ✅ `homework-mentor==0.1.0 (from file://...)` |
| 2 | Smoke-тест PASSED | ✅ `test_mentor_import PASSED` |
