# Task 02: transport-adaptations

> **Sprint:** [../../README.md](../../README.md)
> **Тип:** feat
> **Ветка:** `feat/course-companion-10-transport-adaptations`
> **Spec:** без spec — эталон `material/course-companion/companion/router.py` (тег `nostream`)

---

## Цель

Адаптации **транспорта** (не бизнес-логики) для Agent Server: router не стримит служебный JSON классификатора; граф совместим с async-вызовами платформы.

---

## Состав работ

- [ ] Router (`router/router.py`): после `with_structured_output(Intent)` — `.with_config({"tags": ["nostream"]})`
- [ ] Async smoke: `tests/server/test_async_invoke.py`
  - собрать граф с mock router + mock companion (без LLM/API)
  - `await graph.ainvoke(...)` — не падает
- [ ] Регрессия router: `tests/router/test_router.py` — mock обновить под цепочку `with_structured_output().with_config().invoke()`
- [ ] **Не делаем** миграцию на `AgentMiddleware` — текущий `create_react_agent` + `dynamic_model` достаточен для S1 (см. README спринта)
- [ ] Самопроверка по DoD

---

## Критерии готовности (DoD)

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | Router LLM помечен `nostream` | grep `nostream` в `router/router.py`; unit-тест mock |
| 2 | `ainvoke` на mock-графе проходит | `tests/server/test_async_invoke.py` |
| 3 | Router-тесты зелёные | `uv run pytest tests/router/ -v` |
| 4 | Полный CI | `.\make.ps1 ci` |

---

## Артефакты

- `src/course_companion/router/router.py` — тег `nostream`
- `tests/server/test_async_invoke.py` — async smoke
- `tests/router/test_router.py` — обновление mock-цепочки

---

## Scope

**Трогаем:** только файлы из списка «Арteфакты».

**НЕ трогаем:**
- `middleware.py` / `companion.py` — без рефакторинга на `AgentMiddleware` (S11+ при необходимости)
- Frontend, langgraph.json, Makefile

---

## Риски и допущения

- **Допущение:** `create_react_agent` с `dynamic_model` уже поддерживает async path LangGraph — достаточно smoke `ainvoke`.
- **Риск:** mock в router-тестах сломается из-за `.with_config()` — поправить `_make_mock_llm`.
- **Грабля эталона:** без `nostream` веб-чат показывает `{"decision":"qa"}` — mitigation обязателен.

---

## Открытые вопросы

- Нет блокирующих.
