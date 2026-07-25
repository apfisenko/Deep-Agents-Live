# Summary: Task 02 — Установка Promptfoo + smoke

> **План:** [sprint README § задача 02](../../README.md)
> **Дата закрытия:** 2026-07-25

---

## Что реализовано

- [`tooling-notes.md`](../../tooling-notes.md) — версии Node/Promptfoo, skills, стенд, smoke, конвенция Windows (`make.ps1` + Docker via WSL)
- Skills: `.agents/skills/promptfoo-provider-setup`, `promptfoo-redteam-setup`, `promptfoo-redteam-run`
- Portable Node **v22.22.0** → `%LOCALAPPDATA%\nodejs-promptfoo` (system PATH был v22.14.0 — EBADENGINE)
- Smoke: `practice/redteam/smoke/promptfooconfig.yaml` — echo eval 1/1 PASS
- Backend: `.\make.ps1 dev-backend`, `/health` → 200

---

## Отклонения от плана

| Отклонение | Почему |
|------------|--------|
| Нет отдельного `mcp_server` | В Deep-Agents-Live tools в Agent Core; зафиксировано в tooling-notes |
| Node не из системного PATH | Promptfoo требует `>=22.22.0`; поставлен portable 22.22.0 |

---

## Принятые решения

| Решение | Причина |
|---------|---------|
| Portable Node рядом с user LocalAppData | Без nvm/winget; не ломает системный Node |
| Smoke на `echo`, не на `/chat` | Задача 02 — проверка CLI, не redteam агента |
| Docker/compose только через `.\make.ps1` (WSL) | Конвенция репо / ADR-0004 |

---

## Итог DoD

| # | Критерий | Результат |
|---|----------|-----------|
| 1 | Node в допустимом диапазоне | ✅ v22.22.0 (portable) |
| 2 | Promptfoo установлен | ✅ 0.121.19 |
| 3 | Три skills + «зачем» | ✅ |
| 4 | Backend healthy | ✅ 200 |
| 5 | Smoke Promptfoo | ✅ exit 0 |

---

## Что дальше

- Задача 03: подбор плагинов и стратегий (`plugin-selection.md`)
