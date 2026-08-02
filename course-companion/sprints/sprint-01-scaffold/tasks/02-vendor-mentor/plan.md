# Plan — Task 02: vendor-mentor

**Sprint:** sprint-01-scaffold  
**Статус:** 🚧 In Progress  
**Дата:** 2026-08-02

---

## Цель

Вендорить `ai-homework-mentor` как editable path-зависимость; создать `MentorOrchestrator` stub и smoke-тест.

---

## Решение по импорту

README описывает `from mentor.agent.orchestrator import MentorOrchestrator`, но фактический пакет — `homework_mentor` без такого класса.

**Выбранный вариант 2:** создать `src/mentor/agent/orchestrator.py` — тонкую обёртку над `homework_mentor.orchestrator`. Smoke-тест использует оригинальный путь из README: `from mentor.agent.orchestrator import MentorOrchestrator`.

`uv_build` auto-discovers оба пакета в `src/`.

---

## Состав работ

- [ ] В `pyproject.toml` добавить зависимость `homework-mentor` + `[tool.uv.sources]`
- [ ] `src/mentor/__init__.py`
- [ ] `src/mentor/agent/__init__.py`
- [ ] `src/mentor/agent/orchestrator.py` — `MentorOrchestrator` stub
- [ ] `tests/__init__.py`
- [ ] `tests/test_smoke.py`
- [ ] `uv sync` без ошибок

---

## DoD

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | Editable dep виден | `uv pip list \| findstr homework` |
| 2 | Smoke-тест PASSED | `uv run pytest tests/test_smoke.py -v` |
