# Summary: Task 04 — Генерация конфига + explainer

> **План:** [sprint README § задача 04](../../README.md)
> **Дата закрытия:** 2026-07-25

---

## Что реализовано

| Артефакт | Назначение |
|----------|------------|
| [`practice/redteam/promptfooconfig.yaml`](../../../../../practice/redteam/promptfooconfig.yaml) | Redteam setup: plugins/strategies/params из задачи 03, OpenRouter, purpose PROTECTED/DISCLOSABLE |
| [`practice/redteam/config-explainer.md`](../../../../../practice/redteam/config-explainer.md) | Человекочитаемое объяснение каждого блока yaml |
| [`practice/redteam/target.mjs`](../../../../../practice/redteam/target.mjs) | HTTP target → `POST /api/v1/chat`, новый `session_id` (UUID) на каждый вызов |

Генерация по логике skills `promptfoo-provider-setup` + `promptfoo-redteam-setup` на входе `threat-model.md`, `plugin-selection.md`, фактов спринта.

---

## Принятые решения

| Решение | Причина |
|---------|---------|
| Target = `file://./target.mjs`, не raw HTTP provider | API требует `session_id`; инвариант — изоляция кейсов |
| `defaultTest`: javascript assert на `SECURITY_BLOCKED`, always pass | Хук для задачи 11; ASR остаётся у plugin graders |
| `channel: telegram` | Синхронный контракт `/api/v1/chat` (не stream) |
| Portable Node v22.22.0 для CLI | System Node 22.14.0 не проходит engine Promptfoo |

---

## Итог DoD

| # | Критерий | Результат |
|---|----------|-----------|
| 1 | Оба файла + target существуют | ✅ |
| 2 | YAML валиден | ✅ `npx promptfoo validate config` → Configuration is valid (Node 22.22.0) |
| 3 | Plugins/strategies = задача 03 | ✅ 5 plugins + `jailbreak:meta`, numTests=3 |
| 4 | OpenRouter, reasoning off, purpose | ✅ `showThinking: false`, PROTECTED/DISCLOSABLE в purpose |
| 5 | Target HTTP chat, не stream | ✅ `target.mjs` → `/api/v1/chat` |

`validate target` — в scope задачи 05 (backend должен быть поднят).

---

## Что дальше

- Задача 05: human review → `config-review-notes.md` (чек-лист + `validate target`)
- Задача 06: `redteam generate` только после pass задачи 05
