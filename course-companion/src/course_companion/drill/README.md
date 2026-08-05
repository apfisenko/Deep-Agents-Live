# `course_companion/drill/` — A2UI-модуль drill-режима

Генерация динамических форм кейса тренажёра (A2UI v0.9).

## Структура

| Файл | Роль |
|------|------|
| `case.py` | `DrillCase` — контракт входа |
| `generator.py` | LLM + `A2uiStreamParser`, retry |
| `routes.py` | `POST /drill/a2ui` (SSE) |
| `delivery.py` | `CompanionDelivery` via langgraph_sdk |

## Монтирование

`webapp.py` → `langgraph.companion.json` `"http": {"app": "..."}`.

Фронт: `/api/drill/a2ui` → companion `:2024` (vite proxy).

## Грабли A2UI

1. `npm install --legacy-peer-deps` (`.npmrc` в frontend).
2. Импорты только `@a2ui/react/v0_9`, `@a2ui/web_core/v0_9`.
3. `catalogId` — литерал v0.9 URL, не helper.
4. В сообщениях `version: "v0.9"`, не `v0.9.1`.
5. Windows: `EXAMPLES_DIR.as_uri()` для schema manager.
