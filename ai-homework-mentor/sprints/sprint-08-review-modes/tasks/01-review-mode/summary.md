# Summary: Task 01 — ReviewMode + wiring single/subagents

> **План:** [plan.md](./plan.md)
> **PR:** —
> **Дата закрытия:** 2026-07-24

---

## Что реализовано

- `src/homework_mentor/config.py` — `ReviewMode`, `resolve_review_mode` (CLI > env `REVIEW_MODE` > default `subagents`)
- `config/prompts/review.yaml` — `single_system_prompt`, `single_review_user_template`
- `src/homework_mentor/orchestrator/review.py` — ветвление agent/message по mode; `ReviewRunResult.review_mode`
- `src/homework_mentor/pipeline.py` — проброс `review_mode`; materialize notes для single/subagents
- `src/homework_mentor/reviewers/notes.py` — `materialize_single_agent_note_from_reply` → `review_single.md`
- `src/homework_mentor/cli/app.py` — `-Mode` / `--mode`; `review_mode` в session panel
- `src/homework_mentor/cli/session_log.py` — поле `review_mode` в summary log
- `.env.example` — комментарий `REVIEW_MODE`
- `tests/test_review_mode.py` — resolve, agent wiring, pipeline, CLI argparse, materialize

---

## Отклонения от плана

Нет отклонений. Fallback-нота для single (`review_single.md`) добавлена как согласованный в плане способ не ломать synthesis S6.

---

## Принятые решения

| Решение | Причина | Ссылка на ADR |
|---------|---------|--------------|
| Default = `subagents` | Обратная совместимость v1 / quickstart | — |
| Отдельные YAML-промпты для `single` | Не смешивать инструкции «делегируй» и «пиши notes сам» | — |
| Fallback `review_single.md` из reply | Synthesis читает `review_*.md`; live-агент может не вызвать write_file | — |
| Verbose panel subagents только при `subagents` | Не показывать пустой handoff в single | — |

---

## Проблемы и решения

| Проблема | Как решили |
|----------|-----------|
| Минимальные review.yaml в тестах без новых полей | Обновили фикстуры в `test_config` / `test_context_engineering` |
| Pipeline-тест с `final_feedback` без `fix_plan` шёл в synthesis | В тесте задали оба артефакта |

---

## Итог DoD

| # | Критерий | Результат |
|---|----------|-----------|
| 1 | `-Mode single` не делегирует reviewer-субагентам | ✅ mock: `subagents=[]` |
| 2 | `-Mode subagents` (и default) — делегирование как v1 | ✅ ≥2 reviewers |
| 3 | Невалидный mode → fail fast | ✅ `ConfigError` / argparse `SystemExit` |
| 4 | Lint + tests | ✅ `.\make.ps1 lint`; 136 passed |

---

## Что дальше

- Task 02: Run-отчёт (RU) — params, context trace, totals, timing → `docs/run-report-*.md`
- Task 03: `compare-modes`
- Task 04: docs polish

---

## Ссылки

- Sprint: [../../README.md](../../README.md)
- Ветка: `feat/s8-01-review-mode`
