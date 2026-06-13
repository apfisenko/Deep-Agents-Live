# Langfuse MCP — воркфлоу

Два сервера в `mcp.json`:

| Сервер | URL | Назначение |
|--------|-----|------------|
| `langfuse-docs` | `https://langfuse.com/api/mcp` | документация |
| `langfuse` | `${LANGFUSE_MCP_URL}` | данные инстанса |

Полный список tools: [mcp.reference.langfuse.com](https://mcp.reference.langfuse.com/).

## Обязательный порядок

1. **Прочитать схему** инструмента в `mcps/<server>/tools/<tool>.json` (если доступна).
2. **Вызвать** через `CallMcpTool` с аргументами по схеме.
3. При auth error — проверить `.env`, не вызывать `mcp_auth` без необходимости.

## Docs MCP (`langfuse-docs`)

```
searchLangfuseDocs(query) → getLangfuseDocsPage(path)
```

Использовать для: SDK API, self-hosting, datasets API, evaluators, LangChain integration.

`getLangfuseOverview` — стартовая карта, если тема неясна.

## Instance MCP (`langfuse`)

Требует running Langfuse + валидный `LANGFUSE_BASIC_AUTH`.

### Observability

- `listObservations` — поиск spans/generations (фильтры по схеме)
- `getObservation` — детали одного observation
- `getObservationFilterSchema` / `getObservationFilterValues` — построение фильтра

### Prompts

- `listPrompts` → `getPrompt(name, label?)`
- `createChatPrompt` / `createTextPrompt` — создание
- `updatePromptLabels` — production/staging labels

### Datasets

- `listDatasets` / `getDataset` — найти dataset
- `upsertDataset` — создать/обновить
- `upsertDatasetItem` — добавить пример (input + expectedOutput + metadata)
- `listDatasetItems` / `getDatasetItem` / `deleteDatasetItem`
- `listDatasetRuns` / `getDatasetRun` — результаты прогонов
- `createDatasetRunItem` — привязать trace к run item

### Scores & metrics

- `createScore` / `listScores` — оценки trace/observation
- `queryMetrics` — агрегаты
- `listEvaluators` / `upsertEvaluator` — LLM-as-judge evaluators

### Health

- `getHealth` — первый вызов при проблемах с MCP

## Маппинг JSONL → DatasetItem

Из `datasets/dataset-v1.jsonl`:

```json
{
  "input": [{"role": "user", "content": "..."}],
  "expected_output": "golden reply",
  "metadata": { "ability": "S1", "segment": "b2c", "version": "v1" }
}
```

→ `upsertDatasetItem`:

- `input`: массив messages (или обёртка по схеме API)
- `expectedOutput`: строка
- `metadata`: копия metadata записи + `source_file: dataset-v1.jsonl`

## Когда какой сервер

| Вопрос | Сервер |
|--------|--------|
| Как настроить CallbackHandler? | `langfuse-docs` |
| Почему trace не в UI? | instance + код |
| Загрузить dataset-v1 | `langfuse` |
| Как работает evaluator? | `langfuse-docs` → примеры в instance |
