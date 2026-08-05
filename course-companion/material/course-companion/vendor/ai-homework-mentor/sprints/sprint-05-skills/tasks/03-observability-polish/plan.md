# Task 03: Observability polish

> **Sprint:** [../../README.md](../../README.md)
> **Тип:** feat

## Цель

Сделать видимой связь YAML rubric/skills с реальным поведением: что загружено и откуда, подтверждённо ли применено; переработать context window; добавить live-прогресс во время `mentor check`.

## Состав работ

- [ ] `MaterializedSkill` + таблица «Skills loaded» (source → workspace)
- [ ] `SkillUsageTracker` + `SubagentRun.skills_confirmed` vs assigned
- [ ] Context window — только parent-turns, Δ и % от лимита
- [ ] `SubagentRun.tokens` из subagent LLM вызовов
- [ ] `cli/progress.py` — LiveProgress (TTY-aware)
- [ ] Комментарии в `config/rubrics/*.yaml` + раздел README
- [ ] Тесты + `make ci`

## DoD

| # | Критерий | Проверка |
|---|----------|----------|
| 1 | «Skills loaded» показывает source → workspace | `make check-backend-verbose` |
| 2 | Subagent: Assigned vs Confirmed read | verbose output |
| 3 | Context window — parent only, Δ, % | просмотр |
| 4 | Live-прогресс в TTY; pipe не ломается | терминал + `\| rg` |
| 5 | YAML + README | просмотр |
| 6 | `make ci` зелёный | `make ci` |

## Артефакты

- `mentor/agent/tools/skills_loader.py`
- `mentor/agent/context_tracker.py`
- `mentor/agent/reviewers.py`
- `mentor/agent/orchestrator.py`
- `cli/progress.py`, `cli/renderer.py`
- `config/rubrics/*.yaml`, `README.md`
- `tests/test_context_tracker.py`, `tests/test_rubric.py`, `tests/test_orchestrator.py`
