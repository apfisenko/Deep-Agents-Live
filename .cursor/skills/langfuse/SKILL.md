---
name: langfuse
description: >-
  Работа с Langfuse в проекте: self-hosted observability, Python SDK + LangChain callbacks, traces/spans,
  промпты, datasets и eval через MCP. Ведёт по диагностике traces, загрузке датасетов, настройке SDK и
  отладке интеграции. Используй когда: Langfuse, traces, observability, spans, generations, промпты,
  dataset в Langfuse, eval/experiment, CallbackHandler, LANGFUSE_*, отладка агента в UI, MCP langfuse.
---

# Langfuse

Скилл для **observability и eval** агентной системы через Langfuse (self-hosted в этом репо).

**Два канала доступа:**

| Канал | Когда | Где |
|-------|-------|-----|
| **Runtime SDK** | traces в production/dev backend | `backend/app/integrations/langfuse.py` |
| **MCP (IDE)** | чтение traces, промптов, datasets; docs | серверы `langfuse` + `langfuse-docs` |

Детали проекта: [`references/project.md`](references/project.md). MCP-воркфлоу: [`references/mcp.md`](references/mcp.md).

---

## Перед началом

1. Прочитать [`references/project.md`](references/project.md) — env, compose, паттерны SDK в репо.
2. Определить задачу:
   - **Интеграция / баг SDK** → код + `langfuse-docs` MCP
   - **Отладка trace** → UI или MCP `listObservations` / `getObservation`
   - **Промпты** → MCP `getPrompt`, `listPrompts`
   - **Датасет / eval** → JSONL репо + MCP `upsertDataset`, `upsertDatasetItem`
3. Перед вызовом MCP — прочитать дескриптор в `mcps/<server>/tools/` (если папка есть) или [MCP Reference](https://mcp.reference.langfuse.com/).

---

## Runtime: трейсинг агента

### Как устроено в репо

- `get_langfuse_callbacks()` — lazy init, кэш handler, **fail-open** (пустой список при ошибке).
- Агент передаёт callbacks + metadata в LangGraph:

```python
config = {
    "callbacks": get_langfuse_callbacks(settings),
    "metadata": {"channel": channel, "session_id": session_id},
    "tags": [channel],
}
```

- Health-check перед init: `{LANGFUSE_HOST}/api/public/health`.
- Flush асинхронный — trace может появиться в UI с задержкой `LANGFUSE_FLUSH_INTERVAL_SEC`.

### Чеклист «traces не видны»

```
- [ ] make up / .\make.ps1 up — Langfuse поднят
- [ ] curl http://localhost:3001/api/public/health → OK
- [ ] LANGFUSE_ENABLED=true, ключи совпадают с LANGFUSE_INIT_PROJECT_*
- [ ] Backend лог: "Langfuse traces enabled"
- [ ] Подождать flush или повторить запрос
- [ ] UI: http://localhost:3001 (admin@admin.local / admin)
```

Команды: `make check-langfuse`, `make compose ARGS="logs -f langfuse-web"`.

### Правила при правках SDK

- **Не блокировать** ответ пользователю — observability опциональна.
- Не логировать secret keys и тексты диалогов.
- Тесты: мокать `is_langfuse_reachable`, сбрасывать кэш через `reset_langfuse_callbacks()`.
- Новые metadata/tags — согласовать с фильтрами в UI (например `channel: web|telegram`).

---

## Datasets и eval

### Формат записей в репо

Канонический merge: `datasets/dataset-v1.jsonl`. Шарды: `dataset-extraction-v0.1.jsonl`, `dataset-synthetic-v0.1.jsonl`, B2B-шарды.

Схема записи:

```json
{
  "input": [{"role": "user", "content": "..."}],
  "expected_output": "...",
  "metadata": { "version": "v1", "segment": "b2c", "ability": "S1", ... }
}
```

### Загрузка в Langfuse (MCP)

1. `getHealth` — MCP доступен.
2. `upsertDataset` — имя, описание, при необходимости `inputSchema`.
3. Для каждой строки JSONL → `upsertDatasetItem`:
   - `input` → поле input (messages / object)
   - `expected_output` → expectedOutput
   - `metadata` → metadata item
4. Эксперимент: `createDatasetRunItem` / прогон через UI или SDK eval.

**Маппинг:** `input` (массив messages) хранить как ChatML; `expected_output` — строка golden reply.

---

## Промпты

- Версионирование в Langfuse UI / MCP: `listPrompts` → `getPrompt` (resolved) или `getPromptUnresolved`.
- Создание: `createChatPrompt` / `createTextPrompt`, лейблы: `updatePromptLabels`.
- Runtime: подтягивать промпт из Langfuse только если это явно в scope Task — иначе in-code prompt.

---

## MCP: порядок работы

### Документация (`langfuse-docs`)

1. `searchLangfuseDocs` — поиск по теме (SDK, datasets, self-hosting).
2. `getLangfuseDocsPage` — полный текст страницы.
3. `getLangfuseOverview` — обзор при незнакомой задаче.

### Инстанс (`langfuse`)

Требует в `.env`: `LANGFUSE_MCP_URL`, `LANGFUSE_BASIC_AUTH` (Base64 `PUBLIC_KEY:SECRET_KEY`).

| Задача | Инструменты |
|--------|-------------|
| Trace drill-down | `listObservations`, `getObservation` |
| Промпт | `getPrompt`, `listPrompts` |
| Датасет | `listDatasets`, `upsertDataset`, `upsertDatasetItem`, `listDatasetItems` |
| Eval run | `listDatasetRuns`, `getDatasetRun`, `createDatasetRunItem` |
| Метрики | `queryMetrics`, `listScores`, `createScore` |

Схему аргументов **всегда** читать из дескриптора перед `CallMcpTool`.

---

## Типовые сценарии

### E2E smoke (web + telegram)

1. `make up` → `make check-langfuse`
2. Один диалог web (SSE) + одно сообщение telegram
3. В UI: два trace, tag/metadata `channel` различимы, spans tool + LLM

### Отладка регрессии агента

1. Найти trace по session_id / времени (`listObservations` с фильтром).
2. Сравнить generations и tool calls с golden из `datasets/dataset-v1.jsonl`.
3. При расхождении — завести score/comment через MCP или UI.

### Импорт validation dataset v1

1. Прочитать `datasets/dataset-v1.jsonl`.
2. `upsertDataset` name=`b2c-agent-v1` (или по Task).
3. Batch `upsertDatasetItem` с сохранением `metadata.ability`, `metadata.segment`.

---

## Антипаттерны

- Вызывать MCP в runtime backend — только IDE/dev.
- Блокировать chat при недоступном Langfuse.
- Хардкодить ключи — только `.env`.
- Грузить датасет без версии в metadata.
- Читать docs из памяти — сначала `searchLangfuseDocs`.

---

## Ссылки в репо

- Интеграция: `Docs/concept/integrations.md` (§ Langfuse)
- Код: `backend/app/integrations/langfuse.py`, `backend/app/agent/react_agent.py`
- Тесты: `backend/tests/test_langfuse_integration.py`
- MCP config: `mcp.json`, `.cursor/mcp.json`
