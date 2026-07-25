# Plan: Task 12 — Baseline «после» + сравнение

> **Sprint:** [README](../../README.md) · задача 12  
> **Дата:** 2026-07-25

---

## Цель

`redteam eval` при `SECURITY_ENABLED=true` на том же `redteam.yaml`; сравнение с `baseline-before`.

---

## Preconditions

- Задача 11 ✅
- `SECURITY_ENABLED=true` в env backend
- `promptfooconfig.yaml` / `redteam.yaml` без diff vs «до»
- `/health` 200, `OPENROUTER_API_KEY` задан

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

## Арteфакты

- `practice/redteam/baseline-after/results.json`
- `baseline-after-notes.md`
- `baseline-comparison.md`
- `tasks/12-baseline-after/summary.md` (после «ок»)

---

## DoD

| # | Критерий |
|---|----------|
| 1 | baseline-after на диске |
| 2 | redteam eval |
| 3 | yaml unchanged |
| 4 | SECURITY_ENABLED=true в notes |
| 5 | baseline-comparison.md |
