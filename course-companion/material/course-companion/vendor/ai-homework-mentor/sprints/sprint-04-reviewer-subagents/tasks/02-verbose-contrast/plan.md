# Task 02: Verbose CLI — контраст до/после

> **Sprint:** [../../README.md](../../README.md)
> **Тип:** feat
> **Ветка:** `feat/mentor-04-verbose-contrast`
> **Spec:** без spec

---

## Цель

В `--verbose` показать панели reviewer-субагентов и parent context peak для контраста с S03 single-agent.

---

## Состав работ

- [x] `context_tracker.py` — `parent_peak_tokens`, `subagent_runs`
- [x] `cli/renderer.py` — панели subagent + baseline S03
- [x] `config/settings.yaml` — `s03_single_agent_peak_tokens`
- [ ] Самопроверка: `make check-backend-verbose`

---

## Критерии готовности (DoD)

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | Панель per subagent в verbose | `make check-backend-verbose` |
| 2 | Parent context peak отображается | `--verbose` output |
| 3 | Lint + тесты | `make ci` |

---

## Артефакты

- `mentor/agent/context_tracker.py`
- `cli/renderer.py`
- `config/settings.yaml`
- `mentor/config.py`

---

## Scope

**Трогаем:** только файлы из списка «Артефакты».

**НЕ трогаем:** orchestrator logic (кроме RunResult fields уже в Task 01).
