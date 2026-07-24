# Dogfooding v1 — AI Homework Mentor на себе

> **Дата:** 2026-07-24  
> **Сессия:** `workspace/20260724T190756Z`  
> **Summary log:** `logs/summary_log_20260724T190756Z.md`  
> **Команда:**

```powershell
cd ai-homework-mentor
.\make.ps1 run -- -Path . -Message "Тема: ai-homework-mentor v1. Проверь архитектуру CLI, orchestrator, skills routing." -Verbose
```

---

## Что сработало

| Шаг | Результат |
|-----|-----------|
| Parse + local path `.` | ✅ source=`ai-homework-mentor`, 247 files (после ignore) |
| Staging inside source | ✅ после фикса ignore `workspace`/`logs`/`.env` |
| Rubric / skills | default + `rubric-default`, `modern-python`, `fastapi-templates` |
| Reviewer subagents | 2 handoffs (architecture, code_quality), ~22s review |
| Notes | materialized из handoff (агенты не вызвали `write_file`) |
| Synthesis | ✅ `output/final_feedback.*`, `output/fix_plan.*` |
| Secrets | ✅ `.env` не в staging; ключей в notes/output нет |

---

## Findings (о себе)

Из `final_feedback` / `fix_plan` сессии `20260724T190756Z`:

### Strengths (как увидел агент)

- Модульная структура, SoC
- CLI entry в `pyproject.toml`
- Современный packaging (`pyproject.toml`)
- README достаточен для старта
- Код в целом читаемый

### Issues / fix_plan

| Severity | Что | criterion_id |
|----------|-----|--------------|
| optional | Добавить inline-комментарии к сложной логике (агент сослался на `generate`) | `quality` |

**Required fixes:** нет (пусто в `fix_plan.required`).

### Claims check

- claim «implemented CLI and tests» → `not_found` (шум: в Message не было такого claim; synthesis взял шаблонно)

---

## Топ follow-up (backlog, не чинить в S7)

1. **Topic parsing:** весь Message стал `topic` → unknown → default rubric. Нужен более жёсткий extract «Тема: …» / mapping для dogfood-темы.
2. **`api_detected=True`:** сработал `fastapi-templates` из‑за наличия FastAPI-артефактов в дереве (fixtures/skills) — ложный API signal на dogfood.
3. **Notes reliability:** субагенты часто не пишут `/notes/*.md`; закрыто materialize из handoff — оставить как safety net, отдельно улучшить prompt/FS.
4. **Качество синтеза на большом дереве:** замечание про `generate` похоже на шум из `tests/fixtures/large_hw` в staged code — рассмотреть ignore `tests/fixtures` или узкий Path для dogfood.
5. **Criterion ids вне rubric default:** strengths ссылаются на `cli-entry`/`packaging`/`docs` при default rubric с другим набором — усилить валидацию id при synthesis.

---

## Surprises

1. Первый прогон: handoffs есть, notes на диске нет → synthesis skipped → «final feedback not ready».
2. Второй прогон: materialize notes OK, но `_summaries_from_handoffs` падал (`str.model_dump`) — баг S6, всплыл только на live handoffs.
3. Staging `-Path .` изначально блокировался проверкой «staging inside source».
4. Feedback мягче ожидаемого для dogfood зрелости (почти нет required) — полезно как сигнал «агент хвалит себя», не как полный audit.

---

## Фиксы, сделанные в Task 02 (блокеры v1)

| Фикс | Зачем |
|------|-------|
| `code_fetch/local.py` + ignore `workspace`,`logs`,`.env`,… | dogfood `-Path .` |
| `reviewers/notes.py` materialize from handoffs | notes для synthesis |
| `_summaries_from_handoffs` parse string summaries | live synthesis |

---

## Артефакты (локально, gitignore)

- `workspace/20260724T190756Z/output/final_feedback.json`
- `workspace/20260724T190756Z/output/fix_plan.json`
- `workspace/20260724T190756Z/notes/review_architecture.md`
- `workspace/20260724T190756Z/notes/review_code_quality.md`
- `logs/summary_log_20260724T190756Z.md`
