# Sprint 03: course-qa

> **Версия roadmap:** v0.3
> **Roadmap:** [../../roadmap.md](../../roadmap.md)
> **Статус:** ✅ Done
> **Открыт:** 2026-08-02
> **Закрыт:** 2026-08-02

---

## Цель спринта

Реализовать `course-qa` как DeclarativeSubAgent (dict-спека) с тулами чтения `data/kb/*.md`, наполнить базу знаний тестовыми файлами курса и защитить тулы от path-traversal — companion впервые знает что-то о курсе.

---

## Паттерн

**DeclarativeSubAgent** (dict-спека) — когда субагент описывается промптом + списком тулов; DeepAgents компилирует агента самостоятельно.

Контраст со sprint-02: `homework-checker` собирался в runtime как `CompiledSubAgent` потому что рубрика и workspace неизвестны заранее. `course-qa` всегда одинаков — достаточно dict-спеки.

**Боль, которую закрывает:** companion ничего не знает о курсе; нет базы знаний и нет агента для её чтения.

---

## DoD спринта

Sprint считается завершённым, когда:

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | `list_kb_docs()` возвращает список заголовков md-файлов из `data/kb/` | `uv run pytest tests/subagents/test_course_qa.py::test_list_kb_docs -v` |
| 2 | `read_kb_doc("schedule.md")` возвращает содержимое файла | `uv run pytest tests/subagents/test_course_qa.py::test_read_kb_doc -v` |
| 3 | `read_kb_doc("../secret.md")` → `PermissionError` (path-traversal заблокирован) | `uv run pytest tests/subagents/test_course_qa.py::test_path_traversal_blocked -v` |
| 4 | dict-спека корректно формируется (`name`, `system_prompt`, `tools` заполнены) | `uv run pytest tests/subagents/test_course_qa.py::test_spec_structure -v` |
| 5 | ruff + mypy без ошибок на изменённых файлах | `.\make.ps1 lint` + `.\make.ps1 typecheck` |

---

## Задачи

| # | Задача | Статус | Plan | Summary |
|---|--------|--------|------|---------|
| 01 | kb-setup | ✅ | [plan](tasks/01-kb-setup/plan.md) | — |
| 02 | dict-subagent | ✅ | [plan](tasks/02-dict-subagent/plan.md) | — |

---

## Задача 01: kb-setup 📋

### Цель

Создать `data/kb/` с тестовыми md-файлами курса Deep Agents: достаточно чтобы тесты и демо-сценарий имели реалистичный контент.

### Состав работ

- [ ] Директория `data/kb/` в корне `course-companion/`
- [ ] `data/kb/schedule.md` — расписание курса (темы, даты, форматы занятий; placeholder-данные)
- [ ] `data/kb/syllabus.md` — программа курса (8 тем, описание каждой; placeholder-данные)
- [ ] `data/kb/faq.md` — FAQ (10–15 вопросов; placeholder-данные)
- [ ] `data/kb/homework.md` — описания домашних заданий (номера, темы, требования; placeholder-данные)
- [ ] Каждый файл начинается с H1-заголовка (`# Расписание курса Deep Agents` и т.д.)
- [ ] Самопроверка: все четыре файла существуют и содержат реалистичный текст

### Критерии готовности (DoD)

**Агент проверяет:**

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | Все 4 файла существуют | `ls data/kb/` показывает 4 файла |
| 2 | Каждый файл начинается с `# ` | `uv run python -c "import pathlib; [print(p.read_text()[:50]) for p in pathlib.Path('data/kb').glob('*.md')]"` |

**Пользователь проверяет:**

- Контент файлов правдоподобен — студент мог бы задать реальный вопрос по этому расписанию
- В `faq.md` есть хотя бы один вопрос про дедлайны и один — про формат сдачи ДЗ

### Артефакты

- `course-companion/data/kb/schedule.md`
- `course-companion/data/kb/syllabus.md`
- `course-companion/data/kb/faq.md`
- `course-companion/data/kb/homework.md`

### Документы

- 📋 [Plan](tasks/01-kb-setup/plan.md)
- 📝 [Summary](tasks/01-kb-setup/summary.md)

---

## Задача 02: dict-subagent 📋

### Цель

Реализовать `course_qa.py` — dict-спеку субагента с двумя тулами (`list_kb_docs`, `read_kb_doc`) и защитой от path-traversal; покрыть тулы unit-тестами.

> 💡 **Скиллы:** `.agents/skills/python-testing-patterns/SKILL.md`

### Состав работ

- [ ] `src/course_companion/subagents/course_qa.py`:

  ```python
  KB_DIR = Path(__file__).parent.parent.parent.parent / "data" / "kb"
  # Путь вычисляется от расположения модуля, не от cwd

  def list_kb_docs() -> str:
      """Возвращает список документов базы знаний с H1-заголовками.
      Формат: '- schedule.md: Расписание курса Deep Agents\n- ...'
      """
      ...

  def read_kb_doc(filename: str) -> str:
      """Читает документ из базы знаний по имени файла.
      Блокирует path-traversal: raises PermissionError если filename содержит '/' или '..'.
      """
      ...

  COURSE_QA_SPEC: dict = {
      "name": "course-qa",
      "description": "Справочник по курсу Deep Agents: расписание, программа, FAQ, домашние задания.",
      "system_prompt": (
          "Ты — справочник курса Deep Agents. "
          "Отвечай только по содержимому базы знаний. "
          "Используй list_kb_docs чтобы узнать какие документы доступны, "
          "затем read_kb_doc чтобы прочитать нужный."
      ),
      "tools": [list_kb_docs, read_kb_doc],
  }
  ```

- [ ] Правила защиты в `read_kb_doc`:
  - Если `filename` содержит `/`, `\\` или `..` — `raise PermissionError(f"Access denied: {filename}")`
  - Если файл не найден — `raise FileNotFoundError(f"Not found: {filename}")`
  - Чтение через `(KB_DIR / filename).read_text(encoding="utf-8")`

- [ ] `tests/subagents/test_course_qa.py` с четырьмя тестами:

  **test_list_kb_docs** — возвращает строку, содержащую `schedule.md`

  **test_read_kb_doc** — читает `schedule.md`, возвращает его содержимое

  **test_path_traversal_blocked** — `read_kb_doc("../secret.md")` → `PermissionError`

  **test_spec_structure** — `COURSE_QA_SPEC` содержит ключи `name`, `system_prompt`, `tools`; `tools` — непустой список

- [ ] Тесты для `list_kb_docs` и `read_kb_doc` используют реальный `data/kb/` (не мок файловой системы)
- [ ] Самопроверка по DoD

### Критерии готовности (DoD)

**Агент проверяет:**

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | Все 4 теста проходят | `uv run pytest tests/subagents/test_course_qa.py -v` |
| 2 | Path-traversal тест явно ловит `PermissionError` | строка `pytest.raises(PermissionError)` присутствует в тесте |
| 3 | ruff + mypy чисты | `uv run ruff check src/course_companion/subagents/course_qa.py` |

**Пользователь проверяет:**

- `read_kb_doc("../secret.md")` действительно не читает файл вне `kb/` — не просто возвращает ошибку, но и не допускает чтение
- Путь к `KB_DIR` не зависит от рабочей директории запуска

### Артефакты

- `course-companion/src/course_companion/subagents/course_qa.py`
- `course-companion/tests/subagents/test_course_qa.py`

### Документы

- 📋 [Plan](tasks/02-dict-subagent/plan.md)
- 📝 [Summary](tasks/02-dict-subagent/summary.md)

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

====================== 8 passed in 1.1s ======================
```

*(Оба субагента протестированы. DeclarativeSubAgent vs CompiledSubAgent — контраст очевиден.)*

---

## Итог

Sprint завершён 2026-08-02. Все 5 DoD-критериев выполнены. `.\make.ps1 lint` + `pytest` — 9 passed (4 новых + 5 из предыдущих спринтов).

**Реализовано:**
- `data/kb/` — 4 файла: schedule.md, syllabus.md, faq.md, homework.md с реалистичным контентом курса.
- `src/course_companion/subagents/course_qa.py` — DeclarativeSubAgent: `list_kb_docs`, `read_kb_doc`, `COURSE_QA_SPEC`.
- Path-traversal заблокирован: `../secret.md` → `PermissionError`.
- `tests/subagents/test_course_qa.py` — 4 теста, все зелёные.
