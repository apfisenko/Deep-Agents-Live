# Baseline «после» — notes (задача 12)

> **Eval ID:** `eval-yYs-2026-07-25T19:37:51`  
> **Дата прогона:** 2026-07-25 (UTC) · ~1h 2m 41s  
> **Артефакт:** [`practice/redteam/baseline-after/results.json`](../../practice/redteam/baseline-after/results.json)

---

## Preconditions

| Условие | Статус |
|---------|--------|
| Задача 11 ✅ (FIX-01…04) | ✅ |
| `SECURITY_ENABLED=true` | ✅ (ручной прогон) |
| `promptfooconfig.yaml` / `redteam.yaml` без diff vs «до» | ✅ git diff пуст |
| Backend `/health` 200, `OPENROUTER_API_KEY` | ✅ (прогон завершён без errors) |

---

## Команда

```powershell
$env:SECURITY_ENABLED = "true"
.\make.ps1 qdrant-up
.\make.ps1 dev-backend
cd practice\redteam
npx promptfoo@latest redteam eval -c redteam.yaml --no-cache --no-share -j 1 `
  -o baseline-after/results.json
```

---

## Метаданные

| Поле | Значение |
|------|----------|
| Promptfoo CLI | latest (`npx promptfoo@latest`) |
| Target | `file://./target.mjs` → `http://127.0.0.1:8000/api/v1/chat` |
| Grader / attack model | `openrouter:openai/gpt-4o-mini` |
| Concurrency | 1 |
| Tests | 30 (116 probes в отчёте) |
| Tokens (total) | 214 166 (191 364 eval + 22 802 grading) |
| Duration | 1h 2m 41s |

---

## Результаты (интерпретация)

| Метрика | Значение | Смысл |
|---------|----------|--------|
| ✓ passed | **19** (63.33%) | Атака **не** прошла |
| ✗ failed | **11** (36.67%) | **Findings** — атака прошла (grader) |
| errors | **0** | Инфра OK |

**ASR (attack success rate) ≈ 37%** — снижение vs baseline «до» (~67%).

### namedScores (из results.json)

| Metric | Pass / tests |
|--------|-------------|
| PolicyViolation | 3/3 base; **2/3** meta |
| PromptExtraction | **3/3** base; **3/3** meta |
| ToolDiscovery | **0/3** base; **0/3** meta |
| ExcessiveAgency | 3/3 base; **1/3** meta |
| Hijacking | 3/3 base; **1/3** meta |

### Маркер `SECURITY_BLOCKED`

| Статистика | Значение |
|------------|----------|
| Ответов с маркером | **19 / 30** |
| blocked + grader pass | 16 |
| blocked + grader fail | 3 (idx 12, 13, 14 — tool-discovery base) |

---

## Заметки

- Прогон выполнен **вручную** пользователем; артефакт на диске.
- `telemetry.shutdown() timed out` — warning при завершении, на результаты не влияет.
- Сравнение с «до» — [`baseline-comparison.md`](./baseline-comparison.md).

---

## DoD задачи 12 (частичная самопроверка)

| # | Критерий | ✅ |
|---|----------|---|
| 1 | baseline-after на диске | ✅ |
| 2 | redteam eval | ✅ |
| 3 | yaml unchanged | ✅ |
| 4 | SECURITY_ENABLED=true в notes | ✅ |
| 5 | baseline-comparison.md | ✅ (см. отдельный файл) |

**Summary задачи 12** — после явного «ок».
