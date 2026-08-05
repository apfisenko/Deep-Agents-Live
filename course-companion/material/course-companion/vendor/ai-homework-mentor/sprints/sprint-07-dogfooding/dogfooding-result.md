# Dogfooding — AI Homework Mentor (S07)

> Прогон: `make check-self-verbose` · 2026-07-01  
> Архив: [reports/dogfooding-20260701-113240](../../reports/dogfooding-20260701-113240/)

## Параметры

| Параметр | Значение |
|----------|----------|
| Модель | `deepseek/deepseek-v4-flash` |
| Rubric | `deep-agents` |
| Длительность | 357.3s |
| Subagents | 5/5 делегировано |
| Reflection | 5/5 аспектов, 0 противоречий |
| Parent context peak | 50,478 tok (39.4% от 128k) |

## Что выявили навыки (ключевое)

| Приоритет | Навык | Замечание |
|-----------|-------|-----------|
| 🔴 | `deep-agents-memory` | `.env` не в `SKIP_DIRS` — копируется в workspace |
| 🔴 | `deep-agents-memory` | `ensure_layout()` не создаёт `skills/` заранее |
| 🔴 | `modern-python` | Нет `pytest-cov`, ruff не `select = ["ALL"]` |
| 🔴 | `modern-python` | Нет тестов на `clone_github_repo`, `acquire_code` |
| 🟡 | `deep-agents-core` | `harness_profile` не передан явно в `create_deep_agent()` |
| 🟡 | `deep-agents-memory` | Dogfooding на `.` — особенности копирования local path |

## Сильные стороны

- Оркестрация (`deep-agents-orchestration`): subagent на аспект, только `task`.
- Context (`langchain-middleware`): parent/subagent токены разделены, observability.
- Синтез S06: отчёт на русском с колонкой «Навык».

## Артефакты

- [report.md](../../reports/dogfooding-20260701-113240/report.md)
- [console-verbose.txt](../../reports/dogfooding-20260701-113240/console-verbose.txt)
