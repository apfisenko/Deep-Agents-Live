# Summary: Task 11 — Реализация фиксов

> **План:** [plan.md](./plan.md) · [fix-decisions](../../fix-decisions.md) · [sprint README § задача 11](../../README.md)  
> **Дата закрытия:** 2026-07-25

---

## Что сделано

### Конфиг

- `Settings.security_enabled` ← env `SECURITY_ENABLED` (default `true`) в `backend/app/config.py`
- `.env.example` — `SECURITY_ENABLED=true`

### FIX-01…04 (`backend/app/security/`)

| FIX | Модуль | Интеграция |
|-----|--------|------------|
| FIX-01 | `payment_state.py` | `tools/registry.py` — session-scoped `create_payment_link` → `confirm_payment` |
| FIX-02 | `output_sanitizer.py` | `react_agent.py` — post-LLM scan (CoT, tools, schemas) |
| FIX-03 | `input_guard.py` | `react_agent.py` — pre-LLM hijack/audit block |
| FIX-04 | rules in `output_sanitizer.py` | fake Telegram JSON / side effects |

Дополнительно: `constants.py` (`SECURITY_BLOCKED`), `context.py` (session ContextVar), `prompt_appendix.py`.

### Поведение

- `SECURITY_ENABLED=true`: guards active; block → reply с `SECURITY_BLOCKED`
- `SECURITY_ENABLED=false`: legacy payment + без guards (baseline «до»)

### Тесты

- `backend/tests/test_security.py` (14 кейсов)
- `backend/tests/conftest.py` — `SECURITY_ENABLED=true` по умолчанию
- **149 passed**, ruff OK

`practice/redteam/*.yaml` не менялись.

---

## Итог DoD

| # | Критерий | Результат |
|---|----------|-----------|
| 1 | `SECURITY_ENABLED` env, default on | ✅ |
| 2 | FIX-01…04 = fix-decisions | ✅ |
| 3 | `false` → bypass | ✅ тест |
| 4 | `SECURITY_BLOCKED` стабилен | ✅ |
| 5 | lint/tests | ✅ pytest + ruff |
| 6 | redteam yaml unchanged | ✅ |

---

## Что дальше

- Задача 12: `redteam eval` при `SECURITY_ENABLED=true` → `baseline-after/` + `baseline-comparison.md`
