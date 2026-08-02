# Summary: Task 02 — router-node

> **Дата закрытия:** 2026-08-02

---

## Что реализовано

- `src/course_companion/router/router.py` — функция `route(router_input, llm=None) → Intent`:
  - `ROUTER_SYSTEM_PROMPT` со sticky-инструкцией (`Текущий режим: {current_mode}. Если неясно — выбирай "stay"`)
  - `_build_prompt()` — форматирует system + human сообщения из `RouterInput`
  - `_get_default_llm()` — создаёт `ChatOpenAI` через OpenRouter из `Config`; вызывается только при `llm=None`
  - Fail-safe: `except Exception → Intent(decision="stay", confidence=0.0, reasoning="failsafe")`

---

## Отклонения от плана

`BaseChatModel` перенесён в `TYPE_CHECKING`-блок (ruff TC002) — не влияет на поведение при `from __future__ import annotations`.

---

## Принятые решения

| Решение | Причина |
|---------|---------|
| `llm: BaseChatModel \| None = None` | Тестируемость: mock LLM передаётся явно, без патчинга `_get_default_llm` |
| `except Exception` (не `LLMError`) | Fail-safe должен ловить любую ошибку: сеть, схема, timeout |
| Проверка `isinstance(result, Intent)` | `with_structured_output` теоретически может вернуть не тот тип |

---

## Проблемы и решения

| Проблема | Как решили |
|----------|-----------|
| ruff TC002: `BaseChatModel` в runtime-импорте | Перенесли в `TYPE_CHECKING` блок |
| ruff RUF001: кириллица в строках | Добавили `RUF001`/`RUF003` в ignore в `pyproject.toml` |
| `langchain_openai` не установлен | Добавили `langchain-openai>=0.2` в зависимости `pyproject.toml` |

---

## Итог DoD

| # | Критерий | Результат |
|---|----------|-----------|
| 1 | `route(input, llm=mock_llm)` без реального API | ✅ |
| 2 | `route(input, llm=broken_llm)` → `Intent(decision="stay")` | ✅ |
| 3 | mypy принимает сигнатуру | ✅ |
| 4 | `_get_default_llm()` вызывается только если `llm=None` | ✅ |

---

## Что дальше

- Task 03: tests
