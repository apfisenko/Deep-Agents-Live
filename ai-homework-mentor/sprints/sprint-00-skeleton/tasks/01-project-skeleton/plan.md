# Task 01: Каркас проекта

> **Sprint:** [../../README.md](../../README.md)
> **Тип:** chore
> **Ветка:** локально (без отдельной ветки, пока не запрошено)
> **Spec:** без spec

---

## Цель

Инициализирован каталог `ai-homework-mentor/` как запускаемый Python-проект с единой точкой входа `make.ps1`.

---

## Состав работ

- [x] `pyproject.toml` (Python ≥3.11, src-layout пакет `homework_mentor`, deps-заготовки + ruff/pytest)
- [x] `make.ps1`: `sync`, `run`, `lint`, `format`, `test`
- [x] Каркас каталогов: `src/homework_mentor/`, `config/`, `logs/` (gitignore), `.env.example`
- [x] Минимальный smoke-тест импорта пакета
- [x] Самопроверка по критериям DoD
- [x] (после «ок» пользователя) Создать `summary.md`, обновить sprint README.md

---

## Критерии готовности (DoD)

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | Зависимости ставятся | `.\make.ps1 sync` |
| 2 | Lint на каркасе проходит | `.\make.ps1 lint` |
| 3 | Smoke-тест зелёный | `.\make.ps1 test` |

> Те же команды пользователь выполняет для самостоятельной верификации.

---

## Артефакты

- `ai-homework-mentor/pyproject.toml` — проект uv + ruff/pytest
- `ai-homework-mentor/uv.lock` — lockfile
- `ai-homework-mentor/.python-version` — pin Python 3.11
- `ai-homework-mentor/make.ps1` — sync / run / lint / format / test
- `ai-homework-mentor/.env.example` — `OPENROUTER_API_KEY=`, `LOG_LEVEL=INFO`
- `ai-homework-mentor/.gitignore` — `.env`, `.venv`, `logs/`, `workspace/`, `__pycache__`
- `ai-homework-mentor/src/homework_mentor/__init__.py` — пакет-заготовка
- `ai-homework-mentor/config/.gitkeep` — место для YAML (задача 02)
- `ai-homework-mentor/logs/.gitkeep` — каталог логов (содержимое gitignore)
- `ai-homework-mentor/tests/test_import.py` — smoke импорта

---

## Scope

**Трогаем:** только файлы из списка «Артефакты» + `sprints/sprint-00-skeleton/tasks/01-project-skeleton/plan.md`.

**НЕ трогаем:**
- `concept/`, `roadmap.md`, README других спринтов
- агент DeepAgents, Rich CLI, YAML-загрузчик, логирование (задачи 02–04)
- корневой `make.ps1` репозитория

---

## Риски и допущения

- Skills `modern-python` / `uv-package-manager` применены; `deepagents` добавляем как runtime-dep уже в Task 01 (заготовка), wiring — в Task 03.
- Имя пакета: `homework_mentor` (без дефисов).
- `make.ps1 run` в Task 01 — заглушка (exit с сообщением или вызов будущего CLI-модуля); полноценный CLI — Task 04.
- Python 3.12+ (sprint README); vision упоминает 3.11 — **фиксируем ≥3.11** (pin `.python-version`).

---

## Открытые вопросы

- [x] Имя пакета `homework_mentor` — согласовано в плане (ок пользователя на Task 01)
