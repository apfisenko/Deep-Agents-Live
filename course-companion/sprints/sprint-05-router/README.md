# Sprint 05: router

> **Версия roadmap:** v0.5
> **Roadmap:** [../../roadmap.md](../../roadmap.md)
> **Статус:** ✅ Done
> **Открыт:** 2026-08-02
> **Закрыт:** 2026-08-02

---

## Цель спринта

Реализовать Router — детерминированный LLM-узел с Pydantic structured output, sticky-логикой и fail-safe: он видит хвост диалога + текущий `mode`, классифицирует интент пользователя и возвращает решение, которое граф использует для конфигурации Companion.

---

## Паттерн

**Router «classify → configure»** — отдельная детерминированная позиция в графе; LLM внутри, но результат — фиксированный Pydantic-объект `Intent`.

Ключевые свойства:
- `review` **не входит** в `Literal` — это состояние флоу, не интент пользователя; Router не знает о режиме разбора
- **Sticky**: при неясном интенте возвращает `stay` (сохраняет текущий `mode`)
- **Fail-safe**: любое исключение при вызове LLM → `stay`; граф не падает

**Боль, которую закрывает:** до этого спринта нет механизма определить, в каком режиме обслуживать новое сообщение пользователя.

---

## DoD спринта

Sprint считается завершённым, когда:

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | `route("хочу сдать ДЗ", mode="qa")` → `Intent(decision="homework")` | `pytest tests/router/test_router.py::test_homework_intent -v` |
| 2 | `route("расскажи о теме 3", mode="qa")` → `Intent(decision="qa")` | `pytest tests/router/test_router.py::test_qa_intent -v` |
| 3 | `route("да, подтверждаю", mode="homework")` → `Intent(decision="stay")` | `pytest tests/router/test_router.py::test_stay_intent -v` |
| 4 | LLM-сбой → `Intent(decision="stay")`, исключение не поднимается | `pytest tests/router/test_router.py::test_failsafe -v` |
| 5 | `"review"` отсутствует в допустимых значениях `Literal` | тест на схему Pydantic-модели |
| 6 | ruff + mypy без ошибок | `.\make.ps1 lint` + `.\make.ps1 typecheck` |

---

## Задачи

| # | Задача | Статус | Plan | Summary |
|---|--------|--------|------|---------|
| 01 | intent-model | ✅ | [plan](tasks/01-intent-model/plan.md) | [summary](tasks/01-intent-model/summary.md) |
| 02 | router-node | ✅ | [plan](tasks/02-router-node/plan.md) | [summary](tasks/02-router-node/summary.md) |
| 03 | tests | ✅ | [plan](tasks/03-tests/plan.md) | [summary](tasks/03-tests/summary.md) |

---

## Задача 01: intent-model 📋

### Цель

Определить Pydantic-модели `Intent` и `RouterInput` — типизированный контракт Router; `review` явно исключён из допустимых значений.

> 💡 **Скиллы:** `.agents/skills/modern-python/SKILL.md`

### Состав работ

- [ ] `src/course_companion/router/intent.py`:

  ```python
  from typing import Literal
  from pydantic import BaseModel, Field

  RouteDecision = Literal["qa", "homework", "stay"]
  # Намеренно: "review" отсутствует — это состояние флоу, не интент пользователя

  class Intent(BaseModel):
      decision: RouteDecision
      confidence: float = Field(ge=0.0, le=1.0, default=1.0)
      reasoning: str = Field(default="", description="Краткое обоснование классификации")

  class RouterInput(BaseModel):
      recent_messages: list[str]   # хвост диалога (последние 3 сообщения, только content)
      current_mode: str            # текущий mode из state
  ```

- [ ] `src/course_companion/router/__init__.py`
- [ ] Самопроверка: `Intent(decision="review")` → `ValidationError` от Pydantic

### Критерии готовности (DoD)

**Агент проверяет:**

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | `Intent(decision="qa")` создаётся без ошибок | `uv run python -c "from course_companion.router.intent import Intent; Intent(decision='qa')"` |
| 2 | `Intent(decision="review")` → `ValidationError` | `pytest` ловит исключение |
| 3 | mypy принимает файл | `uv run mypy src/course_companion/router/intent.py` |

**Пользователь проверяет:**

- Комментарий «`review` отсутствует — это состояние флоу, не интент» явно присутствует в коде

### Артефакты

- `course-companion/src/course_companion/router/__init__.py`
- `course-companion/src/course_companion/router/intent.py`

### Документы

- 📋 [Plan](tasks/01-intent-model/plan.md)
- 📝 [Summary](tasks/01-intent-model/summary.md)

---

## Задача 02: router-node 📋

### Цель

Реализовать `router.py` — LLM-узел с structured output, sticky-промптом и fail-safe; функция `route()` принимает `RouterInput`, возвращает `Intent` — всегда, даже при ошибке LLM.

### Состав работ

- [ ] `src/course_companion/router/router.py`:

  ```python
  ROUTER_SYSTEM_PROMPT = """
  Ты — классификатор интента студента. Определи, что хочет сделать студент:
  - "qa": задать вопрос о курсе (расписание, программа, FAQ)
  - "homework": сдать домашнее задание (есть путь к коду или явное желание проверить)
  - "stay": продолжить текущий диалог (уточнение, ответ на вопрос, неясный интент)

  Текущий режим: {current_mode}
  Если неясно — выбирай "stay".
  """

  def route(router_input: RouterInput, llm: BaseChatModel | None = None) -> Intent:
      """Классифицирует интент. При любом исключении возвращает Intent(decision='stay').
      llm: передаётся явно для тестируемости; если None — создаётся из конфига.
      """
      try:
          structured_llm = (llm or _get_default_llm()).with_structured_output(Intent)
          prompt = _build_prompt(router_input)
          return structured_llm.invoke(prompt)
      except Exception:
          return Intent(decision="stay", confidence=0.0, reasoning="failsafe")
  ```

- [ ] `_build_prompt(router_input)` — форматирует sticky-промпт: вставляет `current_mode` и последние 3 сообщения
- [ ] `_get_default_llm()` — создаёт LLM из `Config` (OpenRouter); вызывается только при `llm=None`
- [ ] Sticky-логика реализована в промпте, не в коде: `"Текущий режим: {current_mode}. Если неясно — выбирай 'stay'"`
- [ ] Самопроверка по DoD

### Критерии готовности (DoD)

**Агент проверяет:**

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | `route(input, llm=mock_llm)` работает без реального API | тест с mock LLM |
| 2 | `route(input, llm=broken_llm)` → `Intent(decision="stay")` | тест fail-safe |
| 3 | mypy принимает сигнатуру `llm: BaseChatModel \| None = None` | `uv run mypy src/course_companion/router/router.py` |

**Пользователь проверяет:**

- `_get_default_llm()` вызывается только если `llm` не передан — тестируемость изолирована
- Fail-safe покрывает `Exception`, не только `LLMError` — любое исключение дропается в `stay`

### Артефакты

- `course-companion/src/course_companion/router/router.py`

### Документы

- 📋 [Plan](tasks/02-router-node/plan.md)
- 📝 [Summary](tasks/02-router-node/summary.md)

---

## Задача 03: tests 📋

### Цель

Покрыть Router unit-тестами с mock LLM: четыре сценария классификации + тест на схему Intent.

> 💡 **Скиллы:** `.agents/skills/python-testing-patterns/SKILL.md`

### Состав работ

- [ ] `tests/router/__init__.py`
- [ ] `tests/router/test_router.py`:

  **test_homework_intent:**
  ```python
  # mock LLM возвращает Intent(decision="homework")
  # route(RouterInput(recent_messages=["хочу сдать ДЗ"], current_mode="qa"), llm=mock)
  # → result.decision == "homework"
  ```

  **test_qa_intent:**
  ```python
  # mock LLM возвращает Intent(decision="qa")
  # recent_messages=["расскажи о теме 3"], current_mode="qa"
  # → result.decision == "qa"
  ```

  **test_stay_intent:**
  ```python
  # mock LLM возвращает Intent(decision="stay")
  # recent_messages=["да, подтверждаю"], current_mode="homework"
  # → result.decision == "stay"
  ```

  **test_failsafe:**
  ```python
  # mock LLM raises RuntimeError("API error")
  # route(...) → Intent(decision="stay")  — исключение НЕ поднимается
  ```

  **test_review_not_in_literal:**
  ```python
  # Intent(decision="review") → pytest.raises(ValidationError)
  ```

- [ ] Фикстура `mock_llm(return_value)` — патчит `with_structured_output`, возвращает нужный `Intent`
- [ ] Фикстура `broken_llm` — `with_structured_output(...).invoke(...)` raises `RuntimeError`
- [ ] Самопроверка по DoD

### Критерии готовности (DoD)

**Агент проверяет:**

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | Все 5 тестов проходят | `uv run pytest tests/router/ -v` |
| 2 | Нет реальных вызовов к OpenRouter API | все вызовы к LLM замокированы |

**Пользователь проверяет:**

- `test_failsafe` явно проверяет, что исключение не поднимается (не просто что результат `stay`)
- `test_review_not_in_literal` — самодокументирующий: ясно почему `review` запрещён

### Артефакты

- `course-companion/tests/router/__init__.py`
- `course-companion/tests/router/test_router.py`

### Документы

- 📋 [Plan](tasks/03-tests/plan.md)
- 📝 [Summary](tasks/03-tests/summary.md)

---

## Что студент видит в CLI после спринта

```
PS> .\make.ps1 test

tests/test_smoke.py::test_mentor_import PASSED
tests/subagents/test_homework_checker.py  3 passed
tests/subagents/test_course_qa.py         4 passed
tests/agent/test_middleware.py            4 passed
tests/agent/test_mode_tools.py            4 passed
tests/router/test_router.py::test_homework_intent PASSED
tests/router/test_router.py::test_qa_intent PASSED
tests/router/test_router.py::test_stay_intent PASSED
tests/router/test_router.py::test_failsafe PASSED
tests/router/test_router.py::test_review_not_in_literal PASSED

====================== 21 passed in 1.7s ======================
```

*(Все компоненты протестированы изолированно. Граф и CLI — в следующем спринте.)*

---

## Итог

**Закрыт:** 2026-08-02

Реализован Router-узел — детерминированная LLM-позиция в графе с Pydantic structured output:
- `Intent` / `RouterInput` — контракт маршрутизации; `"review"` намеренно исключён
- `route()` — sticky-промпт, fail-safe через `except Exception`
- 5 unit-тестов с mock LLM; **27 passed** общий счёт
- Добавлена зависимость `langchain-openai>=0.2`
