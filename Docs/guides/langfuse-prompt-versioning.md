# Prompt Management в Langfuse — версионность и link to traces

> **E-10** ([eval-methodology](../../.methodology/eval/eval-methodology.md)): промпты в Langfuse Prompt Management; конфиг ссылается по `name` + `label`; при запуске резолвится версия и пишется в metadata trace / run.

---

## Модель

| Слой | Роль |
|------|------|
| **`backend/app/agent/prompts/*.txt`** | Source of truth в git (review, diff, PR) |
| **Langfuse Prompt Management** | Runtime-зеркало: версии, labels, metrics, link to traces |
| **`.env`** | `PROMPT_SOURCE`, `PROMPT_NAME`, `PROMPT_LABEL`, **`PROMPT_FALLBACK_PATH`** |
| **Langfuse labels** | **`PROMPT_NAME` + `PROMPT_LABEL`** — backend fetch по паре name + label; другие промпты могут иметь ту же метку |

Правка промпта = коммит `.txt` → загрузка в Langfuse → label **`PROMPT_LABEL`** на версии **`PROMPT_NAME`**. Скрипт upload снимает эту метку только с **других промптов реестра** (`prompt_registry.py`), не трогая composable-промпты вроде `_agent-*`.

---

## Промпты в репозитории

| `prompt.name` | Файл |
|---------------|------|
| `SYSTEM_PROMPT` | `SYSTEM_PROMPT.txt` |
| `SYSTEM_PROMPT_SEARCH_FIRST` | `SYSTEM_PROMPT_SEARCH_FIRST.txt` |
| `SYSTEM_PROMPT_SEARCH_FALLBACK` | `SYSTEM_PROMPT_SEARCH_FALLBACK.txt` (prod default) |
| `SYSTEM_PROMPT_GRAPHRAG_ROUTING` | `SYSTEM_PROMPT_GRAPHRAG_ROUTING.txt` |

Реестр: `backend/app/agent/prompt_registry.py`.

---

## Первичная загрузка

```powershell
.\make.ps1 up
.\make.ps1 check-langfuse
.\make.ps1 langfuse-upload-prompts
```

Скрипт: `backend/scripts/upload_langfuse_prompts.py`.

- По умолчанию загружает **только `PROMPT_NAME`** и вешает на него label из **`PROMPT_LABEL`**.
- Перед загрузкой **снимает этот label** с остальных промптов **реестра** (не затрагивает `_agent-*` и прочие промпты вне реестра).
- `--all` — загрузить все `.txt` из реестра; label получает только `--name`.

```powershell
cd backend
uv run python scripts/upload_langfuse_prompts.py --label production --commit-message "sync after routing tweak"
# все промпты в Langfuse, label только на PROMPT_NAME:
uv run python scripts/upload_langfuse_prompts.py --all --name SYSTEM_PROMPT_SEARCH_FALLBACK
```

---

## Версионность: типовой цикл

### 1. Изменить промпт в git

```text
backend/app/agent/prompts/SYSTEM_PROMPT_SEARCH_FALLBACK.txt
```

Коммит в PR — как любой код.

### 2. Загрузить новую версию в Langfuse

```powershell
.\make.ps1 langfuse-upload-prompts
```

Каждый запуск **не перезаписывает** старые версии — создаёт **v2, v3, …** и вешает label на новую версию (если `--label production`, label переезжает на последнюю загруженную).

### 3. Продвижение label (без нового текста)

В UI Langfuse → **Prompts** → выбрать промпт → **Versions** → на нужной версии назначить label `production` / `staging`.

Через MCP (Cursor): `getPrompt`, `updatePromptLabels` — см. [MCP Reference](https://mcp.reference.langfuse.com/).

### 4. Runtime подхватывает label

При `PROMPT_SOURCE=langfuse` **активный промпт определяется парой `PROMPT_NAME` + `PROMPT_LABEL`**: backend вызывает `get_prompt(PROMPT_NAME, label=PROMPT_LABEL)` и проверяет, что у этой версии есть метка. Другие промпты в Langfuse могут иметь тот же label (например `_agent-role@production`) — это не конфликт.

Переключение — через **`.env`**:

```env
PROMPT_SOURCE=langfuse
PROMPT_NAME=SYSTEM_PROMPT_SEARCH_FALLBACK
PROMPT_LABEL=production
SYSTEM_PROMPT_PATH=backend/app/agent/prompts/SYSTEM_PROMPT_SEARCH_FALLBACK.txt
PROMPT_FALLBACK_PATH=backend/app/agent/prompts/SYSTEM_PROMPT_SEARCH_FALLBACK.txt
```

В eval-конfig (`baseline-react-inmemory.yaml`):

```yaml
prompt:
  source: ${PROMPT_SOURCE}
  path: ${SYSTEM_PROMPT_PATH}
  name: ${PROMPT_NAME}
  label: ${PROMPT_LABEL}
```

Код: `prompt_resolver.py` → `resolve_prompt_name_for_label` (проверка label на `PROMPT_NAME`) → `client.get_prompt(name, label=...)`.

При отсутствии версии `PROMPT_NAME@PROMPT_LABEL` — **`ConfigNotFoundError`**, без silent fallback.

---

## Подключение к агенту

Переключение **file ↔ langfuse** — только через `.env`:

| Переменная | `file` (default) | `langfuse` |
|------------|------------------|------------|
| `PROMPT_SOURCE` | `file` | `langfuse` |
| `PROMPT_NAME` | `SYSTEM_PROMPT_SEARCH_FALLBACK` | Имя промпта в Langfuse; fetch по паре с `PROMPT_LABEL` |
| `PROMPT_LABEL` | `production` | Label версии **`PROMPT_NAME`**; определяет активную версию |
| `PROMPT_FALLBACK_PATH` | **дефолтный `.txt`**, если Langfuse недоступен при `PROMPT_SOURCE=langfuse` |

```env
PROMPT_SOURCE=langfuse
PROMPT_NAME=SYSTEM_PROMPT_SEARCH_FALLBACK
PROMPT_LABEL=production
PROMPT_FALLBACK_PATH=backend/app/agent/prompts/SYSTEM_PROMPT_SEARCH_FALLBACK.txt

LANGFUSE_PUBLIC_KEY=pk-lf-dev
LANGFUSE_SECRET_KEY=sk-lf-dev
LANGFUSE_HOST=http://localhost:3001
LANGFUSE_ENABLED=true
```

Отдельный `config_id` не нужен — достаточно `PROMPT_SOURCE=langfuse` при default `baseline-react-inmemory`.

Traces и fetch промпта используют одни ключи; `LANGFUSE_ENABLED` управляет только **отправкой traces**, не загрузкой промпта.

---

## Автообновление версии (prompt cache)

При `PROMPT_SOURCE=langfuse` backend кэширует промпт с TTL **`PROMPT_CACHE_TTL_SEC`** (default `60`). На каждый запрос к агенту проверяется кэш; при истечении TTL — refresh из Langfuse.

Пример логов:

```text
INFO prompts.store: CACHE REFRESH SYSTEM_PROMPT_SEARCH_FALLBACK@production — v4 → v5 (changed), source=langfuse, cache_age=62s, ttl=60s, refreshed_at=2026-08-01T17:54:00+00:00, cached_since=2026-08-01T17:53:00+00:00, langfuse_updated_at=2026-08-01T14:54:00+00:00
INFO app.agent.react_agent: Prompt version changed (v4 → v5) — invalidating agent and config cache
```

Если версия не изменилась — runner **не** пересоздаётся (только обновляется cache entry).  
При смене версии — пересборка `ReactAgentRunner` без рестарта backend.

Код: `backend/app/agent/prompt_store.py`, `get_agent_runner()` в `react_agent.py`.

---

## Link to traces

При `source: langfuse` и успешном fetch (не fallback) backend передаёт `langfuse_prompt` в metadata LangChain config — `CallbackHandler` связывает generation с версией промпта. В UI:

1. **Traces** → generation span → видна **связанная версия промпта**
2. **Prompts** → промпт → вкладка **Metrics** (latency, tokens, cost по версиям)

Проверка:

```powershell
.\make.ps1 dev-backend
.\make.ps1 check-chat-stream
# подождать flush (~5 сек)
```

UI: http://localhost:3001 → последний trace → generation должен ссылаться на `SYSTEM_PROMPT_SEARCH_FALLBACK` с номером версии.

Metadata trace также содержит: `prompt_name`, `prompt_label`, `prompt_version`.

---

## Fallback (fail-open)

| Ситуация | Поведение |
|----------|-----------|
| Langfuse недоступен | Текст из **`PROMPT_FALLBACK_PATH`**, диалог работает, **link to traces нет** |
| Промпт не найден, есть `.txt` | SDK fallback на файл |
| Нет ни Langfuse, ни файла | `ConfigNotFoundError` |

---

## Eval и сравнение конфигов

- **Baseline** `baseline-react-inmemory` — `prompt.source: file` (неприкосновенен, E-7)
- **Candidate** `baseline-react-inmemory-langfuse` — тот же стек, только `source: langfuse`

В `run_metadata` эксперимента пишутся `prompt_source`, `prompt_name`, `prompt_label`, `prompt_version`.

Сравнивать прогоны можно только при осознанном выборе: file vs langfuse — это **разные** `config_id`.

---

## Labels: staging / A-B

Рекомендуемые labels:

| Label | Назначение |
|-------|------------|
| `production` | Текущий prod |
| `staging` | Кандидат перед promote |
| `experiment-<id>` | Разовый A/B (отдельный eval-конfig с этим label) |

Workflow A/B:

1. Загрузить промпт с `--label staging`
2. Eval-конfig с `prompt.label: staging`
3. После прохождения метрик — перенести label `production` на winning version в UI

---

## MCP (Cursor IDE)

Сервер `langfuse` в `.cursor/mcp.json`. Инструменты: `listPrompts`, `getPrompt`, `createTextPrompt`, `updatePromptLabels`.

Skill: `.cursor/skills/langfuse/SKILL.md`.

---

## Troubleshooting

| Симптом | Действие |
|---------|----------|
| Промпт не обновился | Перезапустить backend; проверить label в UI |
| Нет link to traces | `source` должен быть `langfuse`; не fallback; `LANGFUSE_ENABLED=true` |
| Metrics пустые | Нужны traces с linked prompt; подождать агрегацию |
| Upload падает на health | `.\make.ps1 up`, `.\make.ps1 check-langfuse` |
| `no version with label` при старте | У `PROMPT_NAME` нет версии с `PROMPT_LABEL`; загрузить или назначить label в UI |

---

## Ссылки

- [integrations.md § Langfuse](../concept/integrations.md)
- [Langfuse: Link to Traces](https://langfuse.com/docs/prompt-management/features/link-to-traces)
- [Langfuse: Prompt Management](https://langfuse.com/docs/prompt-management/get-started)
