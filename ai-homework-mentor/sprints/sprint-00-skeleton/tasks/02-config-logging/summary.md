# Summary: Task 02 — YAML-конфиг + логирование

> **План:** [plan.md](./plan.md)
> **Дата закрытия:** 2026-07-24

---

## Что реализовано

- `config/agent.yaml` — модель OpenRouter, temperature, лимиты контекста
- `config/prompts/orchestrator.yaml` — системный промпт болванки
- `config/output.yaml` — `compact` по умолчанию, флаги verbose-заготовки
- `src/homework_mentor/config.py` — Pydantic-схемы, `load_yaml_config`, `load_runtime_settings` (fail-fast)
- `src/homework_mentor/logging_setup.py` — stdout + `logs/app.log`, `service=`, `SecretRedactFilter`
- `tests/test_config.py`, `tests/test_logging.py`

---

## Отклонения от плана

- Skill `sharp-edges` отсутствует — fail-fast по conventions проекта.
- Имя `require_runtime_secrets()` в плане → фактически `load_runtime_settings()`.

---

## Принятые решения

| Решение | Причина | Ссылка на ADR |
|---------|---------|--------------|
| YAML без ключа; ключ только в `load_runtime_settings()` | DoD: ошибка «при старте агента», не при чтении промптов | — |
| `SecretStr` для API key | не светить секрет в repr/логах pydantic | — |
| Корень конфига от `Path(__file__)` | независим от CWD пользователя | — |

---

## Проблемы и решения

| Проблема | Как решили |
|----------|-----------|
| ruff TC003 на `Path` в logging | `TYPE_CHECKING` import |

---

## Итог DoD

| # | Критерий | Результат |
|---|----------|-----------|
| 1 | Конфиг парсится | ✅ |
| 2 | Нет ключа → понятная ошибка | ✅ `ConfigError` / `OPENROUTER_API_KEY` |
| 3 | API key не в логе | ✅ redaction filter |
| 4 | Lint + tests | ✅ 9 passed |

---

## Что дальше

- Task 03: агент-болванка DeepAgents + OpenRouter

---

## Ссылки

- [Sprint 00 README](../../README.md)
