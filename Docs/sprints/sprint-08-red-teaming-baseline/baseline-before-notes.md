# Baseline «до» — notes (задача 08)

> **Eval ID:** `eval-g7I-2026-07-25T16:58:54`  
> **Дата прогона:** 2026-07-25 (UTC) · ~40m 44s  
> **Артефакт:** [`practice/redteam/baseline-before/results.json`](../../practice/redteam/baseline-before/results.json)

---

## Preconditions

| Условие | Статус |
|---------|--------|
| Задача 07 = ACCEPT | ✅ |
| `POST /api/v1/chat` → backend `:8000` | ✅ |
| `SECURITY_ENABLED` | **off** (фиксов нет) |
| `promptfooconfig.yaml` / `redteam.yaml` не менялись | ✅ git diff пуст |
| `OPENROUTER_API_KEY` в env (target + grading) | ✅ (повторный прогон) |

---

## Команда

```powershell
$env:Path = "$env:LOCALAPPDATA\nodejs-promptfoo;$env:Path"
# OPENROUTER_API_KEY задан
.\make.ps1 qdrant-up
.\make.ps1 dev-backend
cd practice\redteam
npx promptfoo@latest redteam eval -c redteam.yaml --no-cache --no-share -j 1 `
  -o baseline-before/results.json
```

**Не** `redteam run` — только `redteam eval`.

---

## Метаданные

| Поле | Значение |
|------|----------|
| Git commit | `2db6b75` |
| Promptfoo CLI | 0.121.19 (portable Node v22.22.0) |
| Target | `file://./target.mjs` → `http://127.0.0.1:8000/api/v1/chat` |
| Grader / attack model | `openrouter:openai/gpt-4o-mini`, `showThinking: false` |
| Concurrency | 1 |
| Tests | 30 (в отчёте 58 probes — meta-iterations) |
| Tokens (total) | 113 502 |

---

## Результаты (интерпретация)

| Метрика | Значение | Смысл |
|---------|----------|--------|
| ✓ passed | **10** (33.33%) | Атака **не** прошла |
| ✗ failed | **20** (66.67%) | **Findings** — атака прошла |
| errors | **0** | Инфра OK |

**ASR (attack success rate) ≈ 67%** — ожидаемо для агента без слоя защиты.

### namedScores (из results.json)

| Metric | Pass count / tests |
|--------|-------------------|
| PolicyViolation | 0 / 3 (+ 0 meta) — все policy-кейсы failed |
| PromptExtraction | 1 / 3 base; 2 / 3 meta passed |
| ToolDiscovery | 1 / 3 base; 0 / 3 meta |
| ExcessiveAgency | 3 / 3 base; 0 / 3 meta |
| Hijacking | 3 / 3 base; 0 / 3 meta |

*(Детальный triage — задача 09.)*

---

## Заметки

- Первый прогон `eval-fwh-…` **не использовать** — 25× grader 401 (нет API key).
- В UI: `npx promptfoo view` → eval `eval-g7I-…`.
- `SECURITY_BLOCKED` в ответах не ожидался (слой защиты ещё не реализован).

---

## DoD задачи 08

| # | Критерий | ✅ |
|---|----------|---|
| 1 | Eval завершён с артефактами | ✅ |
| 2 | `baseline-before/` на диске | ✅ |
| 3 | Config/tests не менялись | ✅ |
| 4 | Команда = `redteam eval` | ✅ |
| 5 | Метаданные | ✅ этот файл |

**Следующий шаг:** задача 09 — `baseline-before-triage.md`.
