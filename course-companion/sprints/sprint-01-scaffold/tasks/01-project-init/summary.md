# Summary — Task 01: project-init

**Статус:** ✅ Done  
**Дата:** 2026-08-02

---

## Что сделано

- `pyproject.toml` с `uv_build` backend, Python ≥3.12, зависимостями и dev-группой
- `src/course_companion/__init__.py` — `__version__ = "0.1.0"`
- `src/course_companion/config.py` — `Config` с fail-fast на `OPENROUTER_API_KEY`
- `.env.example` с комментариями к каждой переменной
- `.gitignore`
- `README.md` (требовался `uv_build` для сборки пакета)

## Решения

- **ruff ignores:** добавлены `CPY001` (copyright), `RUF002` (кириллица в docstrings), `S101` для tests/
- **mypy:** `ignore_missing_imports = true` — `homework_mentor` не имеет py.typed

## DoD

| # | Критерий | Результат |
|---|----------|-----------|
| 1 | `pyproject.toml` валиден | ✅ `uv sync` без ошибок |
| 2 | Пакет импортируется | ✅ `import course_companion` |
| 3 | ruff без ошибок | ✅ |
| 4 | `Config` падает без ключа | ✅ `ValueError` через pipe-тест |
