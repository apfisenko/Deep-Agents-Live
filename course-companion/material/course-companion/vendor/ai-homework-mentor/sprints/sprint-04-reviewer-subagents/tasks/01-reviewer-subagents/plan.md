# Task 01: Reviewer Subagents

> **Sprint:** [../../README.md](../../README.md)
> **Тип:** feat
> **Ветка:** `feat/mentor-04-reviewer-subagents`
> **Spec:** без spec

---

## Цель

Делегировать проверку каждого аспекта rubric изолированным reviewer-субагентам через `task` tool; parent синтезирует feedback из `notes/`.

---

## Состав работ

- [x] `mentor/agent/reviewers.py` — `build_reviewer_subagents`, `parse_task_messages`
- [x] Разблокировать `task` в harness profile
- [x] `config/prompts/reviewer.yaml` + обновить `orchestrator.yaml`
- [x] `orchestrator.py` — subagents, RunResult.subagent_runs
- [x] `tests/test_orchestrator.py`
- [ ] Самопроверка по критериям DoD

---

## Критерии готовности (DoD)

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | ≥3 аспекта делегируются | `uv run pytest tests/test_orchestrator.py` |
| 2 | `notes/<aspect>.md` на каждый аспект | `make check-backend-verbose` |
| 3 | `output/feedback.md` из нот | `cat .mentor-workspace/.../output/feedback.md` |
| 4 | Lint + тесты | `make ci` |

---

## Артефакты

- `mentor/agent/reviewers.py` — сборка subagents и парсинг task messages
- `mentor/agent/orchestrator.py` — интеграция S04
- `config/prompts/reviewer.yaml` — промпт reviewer
- `config/prompts/orchestrator.yaml` — делегирование через task
- `tests/test_orchestrator.py` — unit-тесты без LLM

---

## Scope

**Трогаем:** файлы из списка «Артефакты».

**НЕ трогаем:** `cli/renderer.py`, S05+, `bot/`, `backend/`.

---

## Риски и допущения

- Оркестратор может пропустить аспект — жёсткий user_message + warning в CLI при неполном делегировании.
