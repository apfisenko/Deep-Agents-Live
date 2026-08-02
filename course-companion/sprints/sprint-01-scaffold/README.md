# Sprint 01: scaffold

> **Версия roadmap:** v0.1
> **Roadmap:** [../../roadmap.md](../../roadmap.md)
> **Статус:** ✅ Done
> **Открыт:** 2026-08-02
> **Закрыт:** 2026-08-02

---

## Цель спринта

Создать скелет проекта `course-companion/` с uv-окружением, вендорить `ai-homework-mentor` как editable path-зависимость и убедиться, что `MentorOrchestrator` импортируется без ошибок — всё остальное строится поверх этого фундамента.

---

## Паттерн

Нет мультиагентного паттерна — чистый scaffold.
**Боль, которую закрывает:** нечего строить поверх, пока ментор не вендорен и проект не настроен.

---

## DoD спринта

Sprint считается завершённым, когда:

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | `uv sync` завершается без ошибок | `.\make.ps1 dev` / `make dev` |
| 2 | `from mentor.agent.orchestrator import MentorOrchestrator` без `ImportError` | `.\make.ps1 test` / `make test` |
| 3 | `.\make.ps1 lint` зелёный (ruff без ошибок) | `.\make.ps1 lint` |
| 4 | `.\make.ps1 ci` проходит полностью | `.\make.ps1 ci` |
| 5 | `.env.example` содержит `OPENROUTER_API_KEY` с плейсхолдером | просмотр файла |

---

## Задачи

| # | Задача | Статус | Plan | Summary |
|---|--------|--------|------|---------|
| 01 | project-init | ✅ | [plan](tasks/01-project-init/plan.md) | [summary](tasks/01-project-init/summary.md) |
| 02 | vendor-mentor | ✅ | [plan](tasks/02-vendor-mentor/plan.md) | [summary](tasks/02-vendor-mentor/summary.md) |
| 03 | make-targets | ✅ | [plan](tasks/03-make-targets/plan.md) | [summary](tasks/03-make-targets/summary.md) |

---

## Задача 01: project-init 📋

### Цель

Инициализировать Python-проект: `pyproject.toml`, `src/course_companion/`, `.env.example`, базовая структура директорий.

> 💡 **Скиллы:** перед началом прочитать `.agents/skills/modern-python/SKILL.md` и `.agents/skills/uv-package-manager/SKILL.md`.

### Состав работ

- [ ] `pyproject.toml` — `name = "course-companion"`, `requires-python = ">=3.12"`;
  зависимости: `langchain`, `langgraph`, `openai`, `python-dotenv`, `pydantic>=2`;
  dev-зависимости: `pytest`, `pytest-asyncio`, `ruff`, `mypy`
- [ ] `src/course_companion/__init__.py` с `__version__ = "0.1.0"`
- [ ] `src/course_companion/config.py` — `Config`-класс с `fail fast` при отсутствии `OPENROUTER_API_KEY`
- [ ] `.env.example` с `OPENROUTER_API_KEY=sk-or-...` и поясняющими комментариями
- [ ] `.gitignore` (`.env`, `__pycache__`, `.venv`, `dist/`, `*.egg-info`)
- [ ] `uv sync` проходит без ошибок
- [ ] Самопроверка по DoD

### Критерии готовности (DoD)

**Агент проверяет:**

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | `pyproject.toml` валиден | `uv sync` без ошибок |
| 2 | Пакет импортируется | `uv run python -c "import course_companion"` |
| 3 | ruff не выдаёт ошибок | `uv run ruff check src/` |
| 4 | `Config` падает без ключа | `uv run python -c "from course_companion.config import Config; Config()"` при пустом `.env` → `ValueError` |

**Пользователь проверяет:**

- `uv run python -c "from course_companion import __version__; print(__version__)"` выводит `0.1.0`
- `.env.example` содержит читаемые комментарии к каждой переменной

### Артефакты

- `course-companion/pyproject.toml`
- `course-companion/.env.example`
- `course-companion/.gitignore`
- `course-companion/src/course_companion/__init__.py`
- `course-companion/src/course_companion/config.py`

### Документы

- 📋 [Plan](tasks/01-project-init/plan.md)
- 📝 [Summary](tasks/01-project-init/summary.md)

---

## Задача 02: vendor-mentor 📋

### Цель

Вендорить `ai-homework-mentor` как editable path-зависимость через uv; smoke-тест подтверждает, что `MentorOrchestrator` импортируется из нового проекта.

> 💡 **Скиллы:** `.agents/skills/uv-package-manager/SKILL.md`

### Состав работ

- [ ] В `pyproject.toml` добавить зависимость `ai-homework-mentor` и секцию:
  ```toml
  [tool.uv.sources]
  ai-homework-mentor = { path = "../ai-homework-mentor", editable = true }
  ```
- [ ] `uv sync` — убедиться, что пакет установлен
- [ ] `tests/__init__.py`
- [ ] `tests/test_smoke.py` — smoke-тест:
  ```python
  from mentor.agent.orchestrator import MentorOrchestrator
  def test_mentor_import(): assert MentorOrchestrator is not None
  ```
- [ ] `pytest.ini` или секция `[tool.pytest.ini_options]` в `pyproject.toml`
- [ ] Самопроверка по DoD

### Критерии готовности (DoD)

**Агент проверяет:**

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | Editable path-dep виден | `uv pip list` содержит `ai-homework-mentor` |
| 2 | Smoke-тест проходит | `uv run pytest tests/test_smoke.py -v` → `PASSED` |

**Пользователь проверяет:**

- `uv run python -c "from mentor.agent.orchestrator import MentorOrchestrator; print('OK')"` выводит `OK`

### Артефакты

- `course-companion/pyproject.toml` (обновлён: `uv.sources` + зависимость)
- `course-companion/tests/__init__.py`
- `course-companion/tests/test_smoke.py`

### Документы

- 📋 [Plan](tasks/02-vendor-mentor/plan.md)
- 📝 [Summary](tasks/02-vendor-mentor/summary.md)

---

## Задача 03: make-targets 📋

### Цель

Создать `Makefile` (для WSL/Linux/macOS) и `make.ps1` (для Windows PowerShell) с единой точкой входа для всех команд разработки.

### Состав работ

- [ ] `Makefile` с целями: `dev`, `test`, `lint`, `format`, `typecheck`, `ci`
  — все цели делегируют через `uv run`
  — `ci` = `lint` + `typecheck` + `test`
- [ ] `make.ps1` — PowerShell-эквивалент с параметром `[string]$Target`:
  ```powershell
  param([string]$Target = "help")
  switch ($Target) {
      "dev"       { uv sync }
      "test"      { uv run pytest ... }
      "lint"      { uv run ruff check src/ tests/ }
      "format"    { uv run ruff format src/ tests/ }
      "typecheck" { uv run mypy src/ }
      "ci"        { .\make.ps1 lint; .\make.ps1 typecheck; .\make.ps1 test }
      default     { Write-Host "Targets: dev test lint format typecheck ci" }
  }
  ```
- [ ] Самопроверка: `.\make.ps1 ci` зелёный в PowerShell; `make ci` зелёный в WSL

### Критерии готовности (DoD)

**Агент проверяет:**

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | `make test` проходит (WSL) | `make test` |
| 2 | `.\make.ps1 test` проходит (PowerShell) | `.\make.ps1 test` |
| 3 | `make lint` зелёный | `make lint` |
| 4 | `make ci` завершается без ошибок | `make ci` |

**Пользователь проверяет:**

- В PowerShell: `.\make.ps1 ci` — все шаги зелёные
- В WSL: `make ci` — все шаги зелёные

### Артефакты

- `course-companion/Makefile`
- `course-companion/make.ps1`

### Документы

- 📋 [Plan](tasks/03-make-targets/plan.md)
- 📝 [Summary](tasks/03-make-targets/summary.md)

---

## Что студент видит в CLI после спринта

```
PS> .\make.ps1 test

tests/test_smoke.py::test_mentor_import PASSED

====================== 1 passed in 0.4s ======================

PS> .\make.ps1 ci
[lint]     ruff check src/ tests/ ... OK
[typecheck] mypy src/ ... OK
[test]     pytest ... 1 passed
```

---

## Итог

Sprint завершён 2026-08-02. Все 5 DoD-критериев выполнены. `.\make.ps1 ci` — зелёный (lint + mypy + 2 tests passed).

**Ключевое решение (Task 02):** создан пакет `src/mentor/` с `MentorOrchestrator` stub — тонкая обёртка над `homework_mentor.orchestrator`. Это точка роста для Sprint 02 (CompiledSubAgent-адаптер).
