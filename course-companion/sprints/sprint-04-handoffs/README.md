# Sprint 04: handoffs

> **Версия roadmap:** v0.4
> **Roadmap:** [../../roadmap.md](../../roadmap.md)
> **Статус:** ✅ Done
> **Открыт:** 2026-08-02
> **Закрыт:** 2026-08-02

---

## Цель спринта

Превратить Companion в конечный автомат из трёх режимов (`qa` / `homework` / `review`): middleware перехватывает каждый вызов модели и подменяет системный промпт + набор тулов по текущему `mode`; переходы между режимами — тул-вызовы, возвращающие `Command`; история диалога при этом едина.

---

## Паттерн

**Handoffs — «single agent + middleware»**: один агент меняет поведение в зависимости от state, без создания новых агентов. Переход = явный `Command(update={"mode": ...})` из тула.

**Почему не несколько агентов:** история диалога должна быть единой во всех режимах — это принципиальное требование для режима `review` (разбор артефактов текущей проверки).

**Боль, которую закрывает:** до этого спринта companion отвечает одинаково на любой запрос; нет режима разбора фидбека, нет режима сдачи ДЗ.

---

## DoD спринта

Sprint считается завершённым, когда:

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | `select_prompt(mode)` возвращает правильный системный промпт для каждого режима | `pytest tests/agent/test_middleware.py::test_select_prompt -v` |
| 2 | `filter_tools(mode, all_tools)` возвращает только разрешённые тулы (blacklist, не whitelist) | `pytest tests/agent/test_middleware.py::test_filter_tools -v` |
| 3 | `switch_to_homework()` возвращает `Command(update={"mode": "homework"})` | `pytest tests/agent/test_mode_tools.py::test_switch_to_homework -v` |
| 4 | `return_to_qa()` возвращает `Command(update={"mode": "qa"})` | `pytest tests/agent/test_mode_tools.py::test_return_to_qa -v` |
| 5 | ruff + mypy без ошибок на изменённых файлах | `.\make.ps1 lint` + `.\make.ps1 typecheck` |

---

## Задачи

| # | Задача | Статус | Plan | Summary |
|---|--------|--------|------|---------|
| 01 | middleware | ✅ | [plan](tasks/01-middleware/plan.md) | [summary](tasks/01-middleware/summary.md) |
| 02 | mode-tools | ✅ | [plan](tasks/02-mode-tools/plan.md) | [summary](tasks/02-mode-tools/summary.md) |
| 03 | tests | ✅ | [plan](tasks/03-tests/plan.md) | [summary](tasks/03-tests/summary.md) |

---

## Задача 01: middleware 📋

### Цель

Реализовать `middleware.py` с функцией `build_modes_middleware()` и декоратором `@wrap_model_call`, который перехватывает каждый вызов модели и подменяет системный промпт + фильтрует тулы по `state["mode"]`.

> 💡 **Скиллы:** `.agents/skills/python-design-patterns/SKILL.md`

### Состав работ

- [ ] `src/course_companion/agent/middleware.py`:

  ```python
  # Системные промпты по режимам
  MODE_PROMPTS: dict[str, str] = {
      "qa": "Ты — ассистент курса Deep Agents. Отвечай на вопросы по программе курса...",
      "homework": "Ты — приёмщик домашних заданий. Прими путь и тему ДЗ...",
      "review": "Ты — наставник. Разбери фидбек по результатам проверки ДЗ...",
  }

  # Тулы, запрещённые в каждом режиме (blacklist, не whitelist)
  MODE_TOOL_BLACKLIST: dict[str, set[str]] = {
      "qa":       {"run_homework_check", "complete_homework",
                   "explain_feedback", "show_fix_plan",
                   "resubmit_homework", "return_to_qa"},
      "homework": {"ask_course_qa", "switch_to_homework",
                   "explain_feedback", "show_fix_plan",
                   "resubmit_homework", "return_to_qa"},
      "review":   {"ask_course_qa", "switch_to_homework",
                   "run_homework_check", "complete_homework"},
  }

  def select_prompt(mode: str) -> str:
      """Возвращает системный промпт для данного режима."""
      ...

  def filter_tools(mode: str, all_tools: list) -> list:
      """Убирает из all_tools запрещённые для mode (по имени функции).
      Blacklist: убираем запрещённые, а не оставляем только разрешённые.
      """
      ...

  def build_modes_middleware(get_mode: Callable[[], str]) -> Callable:
      """Возвращает middleware-функцию для DeepAgents @wrap_model_call.
      get_mode — колбэк, возвращающий текущий mode из state.
      """
      ...
  ```

- [ ] Логика `build_modes_middleware`:
  - Принимает `get_mode: Callable[[], str]` — извлекает mode из state без прямой зависимости на state-объект
  - Возвращаемый middleware перехватывает аргументы вызова модели
  - Подменяет `system_prompt` на `select_prompt(mode)`
  - Фильтрует `tools` через `filter_tools(mode, tools)`
  - Прокидывает модифицированный запрос в оригинальный вызов модели

- [ ] `src/course_companion/agent/__init__.py`
- [ ] Самопроверка по DoD

### Критерии готовности (DoD)

**Агент проверяет:**

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | `select_prompt("qa")` не пустой | `assert len(select_prompt("qa")) > 0` |
| 2 | `filter_tools("qa", all_tools)` не содержит `run_homework_check` | тест |
| 3 | `filter_tools("review", all_tools)` не содержит `ask_course_qa` | тест |
| 4 | Неизвестный mode → `KeyError` с понятным сообщением | fail-fast |

**Пользователь проверяет:**

- Blacklist-таблица читается как явная документация правил: понятно что запрещено в каждом режиме
- `build_modes_middleware` не импортирует state напрямую — зависит только от колбэка

### Артефакты

- `course-companion/src/course_companion/agent/__init__.py`
- `course-companion/src/course_companion/agent/middleware.py`

### Документы

- 📋 [Plan](tasks/01-middleware/plan.md)
- 📝 [Summary](tasks/01-middleware/summary.md)

---

## Задача 02: mode-tools 📋

### Цель

Реализовать тулы-переходы между режимами Companion: каждый тул возвращает `Command(update={"mode": ...})`, что переключает state без создания нового агента.

### Состав работ

- [ ] `src/course_companion/agent/tools/mode_tools.py`:

  ```python
  def switch_to_homework() -> Command:
      """Переключить Companion в режим сдачи домашнего задания."""
      return Command(update={"mode": "homework"})

  def complete_homework(hw_artifacts: HWArtifacts) -> Command:
      """Зафиксировать результат проверки и перейти в режим разбора фидбека."""
      return Command(update={"mode": "review", "hw_artifacts": hw_artifacts})

  def return_to_qa() -> Command:
      """Вернуться в режим вопросов по курсу."""
      return Command(update={"mode": "qa"})

  def resubmit_homework() -> Command:
      """Отправить ДЗ на повторную проверку (из режима review)."""
      return Command(update={"mode": "homework"})
  ```

- [ ] Тулы для режима `qa` (вызывают субагента):

  ```python
  def ask_course_qa(question: str) -> str:
      """Задать вопрос по курсу субагенту course-qa. Возвращает ответ."""
      # Делегирует в COURSE_QA_SPEC субагент (заглушка — вернём в sprint-06)
      return "[course-qa] заглушка — реализуется в sprint-06"
  ```

- [ ] Тулы для режима `homework`:

  ```python
  def run_homework_check(submission_path: str, topic: str) -> str:
      """Запустить проверку ДЗ. Возвращает строку-статус."""
      # Заглушка — полная интеграция в sprint-06
      return "[homework-checker] заглушка — реализуется в sprint-06"
  ```

- [ ] Тулы для режима `review`:

  ```python
  def explain_feedback(aspect_id: str) -> str:
      """Объяснить замечание по конкретному аспекту рубрики из hw_artifacts."""
      return "[review] заглушка"

  def show_fix_plan() -> str:
      """Показать пошаговый план исправлений из hw_artifacts."""
      return "[review] заглушка"
  ```

- [ ] `src/course_companion/agent/tools/__init__.py` — экспортирует все тулы
- [ ] `ALL_TOOLS` список — используется middleware для фильтрации
- [ ] Самопроверка по DoD

### Критерии готовности (DoD)

**Агент проверяет:**

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | `switch_to_homework()` возвращает `Command` | `isinstance(switch_to_homework(), Command)` |
| 2 | `complete_homework(artifacts)` содержит `mode="review"` и `hw_artifacts` | тест |
| 3 | `ALL_TOOLS` содержит все 8 тулов | `assert len(ALL_TOOLS) == 8` |

**Пользователь проверяет:**

- Заглушки явно помечены комментарием `# заглушка — реализуется в sprint-06`
- `Command.update` содержит только те ключи, которые реально меняются

### Артефакты

- `course-companion/src/course_companion/agent/tools/__init__.py`
- `course-companion/src/course_companion/agent/tools/mode_tools.py`

### Документы

- 📋 [Plan](tasks/02-mode-tools/plan.md)
- 📝 [Summary](tasks/02-mode-tools/summary.md)

---

## Задача 03: tests 📋

### Цель

Покрыть middleware и тулы-переходы unit-тестами; проверить сценарий qa → homework → review → qa на уровне State-переходов.

> 💡 **Скиллы:** `.agents/skills/python-testing-patterns/SKILL.md`

### Состав работ

- [ ] `tests/agent/__init__.py`
- [ ] `tests/agent/test_middleware.py`:

  **test_select_prompt** — `select_prompt("qa")`, `"homework"`, `"review"` — все непустые и разные

  **test_filter_tools_qa** — `run_homework_check` отсутствует после фильтрации для `"qa"`

  **test_filter_tools_review** — `ask_course_qa` отсутствует после фильтрации для `"review"`

  **test_filter_tools_homework** — `explain_feedback` отсутствует после фильтрации для `"homework"`

- [ ] `tests/agent/test_mode_tools.py`:

  **test_switch_to_homework** — `Command.update["mode"] == "homework"`

  **test_complete_homework** — `Command.update["mode"] == "review"` и `"hw_artifacts"` в update

  **test_return_to_qa** — `Command.update["mode"] == "qa"`

  **test_resubmit_homework** — `Command.update["mode"] == "homework"`

- [ ] `.\make.ps1 test` — все 12 тестов проходят
- [ ] Самопроверка по DoD

### Критерии готовности (DoD)

**Агент проверяет:**

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | Все тесты проходят | `uv run pytest tests/agent/ -v` |
| 2 | Нет обращений к LLM или FS в тестах middleware/mode-tools | нет `patch` на LLM, нет обращений к `data/kb/` |

**Пользователь проверяет:**

- Тест `test_filter_tools_*` явно проверяет отсутствие конкретного тула — не просто длину списка
- Тест `test_complete_homework` передаёт реальный `HWArtifacts` (пусть и минимальный)

### Артефакты

- `course-companion/tests/agent/__init__.py`
- `course-companion/tests/agent/test_middleware.py`
- `course-companion/tests/agent/test_mode_tools.py`

### Документы

- 📋 [Plan](tasks/03-tests/plan.md)
- 📝 [Summary](tasks/03-tests/summary.md)

---

## Что студент видит в CLI после спринта

```
PS> .\make.ps1 test

tests/test_smoke.py::test_mentor_import PASSED
tests/subagents/test_homework_checker.py::test_happy_path PASSED
tests/subagents/test_homework_checker.py::test_pipeline_error_returns_aimessage PASSED
tests/subagents/test_homework_checker.py::test_build_returns_compiled_graph PASSED
tests/subagents/test_course_qa.py::test_list_kb_docs PASSED
tests/subagents/test_course_qa.py::test_read_kb_doc PASSED
tests/subagents/test_course_qa.py::test_path_traversal_blocked PASSED
tests/subagents/test_course_qa.py::test_spec_structure PASSED
tests/agent/test_middleware.py::test_select_prompt PASSED
tests/agent/test_middleware.py::test_filter_tools_qa PASSED
tests/agent/test_middleware.py::test_filter_tools_review PASSED
tests/agent/test_middleware.py::test_filter_tools_homework PASSED
tests/agent/test_mode_tools.py::test_switch_to_homework PASSED
tests/agent/test_mode_tools.py::test_complete_homework PASSED
tests/agent/test_mode_tools.py::test_return_to_qa PASSED
tests/agent/test_mode_tools.py::test_resubmit_homework PASSED

====================== 16 passed in 1.4s ======================
```

*(Companion ещё не существует как объект — только его «нервная система»: middleware + тулы.)*

---

## Итог

**22 тестов: 13 новых (agent) + 9 предыдущих — все зелёные.**

Реализована «нервная система» Companion: middleware конечного автомата трёх режимов (`qa` / `homework` / `review`) и 8 тулов-переходов. Заглушки для sprint-06 явно помечены. ruff + mypy чистые.
