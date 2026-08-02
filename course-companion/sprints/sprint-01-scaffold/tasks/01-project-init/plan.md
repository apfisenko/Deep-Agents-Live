# Plan — Task 01: project-init

**Sprint:** sprint-01-scaffold  
**Статус:** 🚧 In Progress  
**Дата:** 2026-08-02

---

## Цель

Инициализировать Python-проект `course-companion/` с uv-окружением, src-layout, Config с fail-fast и `.env.example`.

---

## Состав работ

- [ ] `pyproject.toml` — `uv_build` backend, Python ≥3.12, зависимости + dev-группа
- [ ] `src/course_companion/__init__.py` — `__version__ = "0.1.0"`
- [ ] `src/course_companion/config.py` — `Config`, fail-fast на `OPENROUTER_API_KEY`
- [ ] `.env.example` — переменные с комментариями
- [ ] `.gitignore`
- [ ] `uv sync` без ошибок

---

## DoD

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | `pyproject.toml` валиден | `uv sync` без ошибок |
| 2 | Пакет импортируется | `uv run python -c "import course_companion"` |
| 3 | ruff без ошибок | `uv run ruff check src/` |
| 4 | `Config` падает без ключа | `uv run python -c "from course_companion.config import Config; Config()"` при пустом `.env` → `ValueError` |

---

## Артефакты

- `course-companion/pyproject.toml`
- `course-companion/.env.example`
- `course-companion/.gitignore`
- `course-companion/src/course_companion/__init__.py`
- `course-companion/src/course_companion/config.py`
