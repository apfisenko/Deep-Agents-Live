# Review: context-middleware — Context engineering

**Источник ревью:** `/code/mentor/agent/orchestrator.py`, `/code/mentor/agent/context_tracker.py`,
`/code/config/settings.yaml`, `/code/mentor/config.py`

**Скилл:** `rubric-deep-agents` → context-middleware aspect; `langchain-middleware` (не применим — HITL не используется)

---

## ✅ 1. SummarizationMiddleware настроена корректно

- Файл: `orchestrator.py`, строки 198–203
- Параметры:
  - `model=model` — передан LLM
  - `backend=backend` — передан `FilesystemBackend`
  - `trigger=("fraction", 0.55)` — триггер срабатывает при 55% заполнения контекста (значение из `settings.yaml` → `summarization_trigger_fraction: 0.55`)
  - `keep=("fraction", 0.15)` — после суммаризации остаётся 15% контекста
- Middleware зарегистрирована в `create_deep_agent(middleware=[summ])` (строка 209)
- **Вывод:** конфигурация рабочая, trigger fraction = 0.55, backend передан ✅

## ✅ 2. Разделение контекста parent vs subagent

- Файл: `context_tracker.py`
- `ContextTracker` хранит:
  - `parent_peak_tokens: int` (строка 36) — пик токенов родительского агента
  - `subagent_peak_tokens: dict[str, int]` (строка 38) — пик токенов каждого сабагента по имени
  - `subagent_skill_reads: dict[str, set[str]]` (строка 39) — какие скиллы читал каждый сабагент
- `record_llm_usage()` (строка 46) — записывает parent-токены, если `_current_step == "agent-review"`
- `record_subagent_llm()` (строка 61) — записывает subagent-токены по имени
- `TokenUsageCallback.on_llm_end()` (строка 205) — маршрутизация:
  - Если `_active_task_depth > 0` → сабагент (через `record_subagent_llm`)
  - Если `_is_subagent_call()` вернул True → сабагент (через `record_subagent_llm` с именем из метаданных)
  - Иначе → parent (через `record_llm_usage`)
- `_is_subagent_call()` (строка 153) проверяет `metadata.ls_agent_type == "subagent"` или наличие тега `subagent`
- `_subagent_name_from_metadata()` (строка 162) читает `lc_agent_name` из metadata
- **Вывод:** parent и subagent токены полностью разделены ✅

## ✅ 3. Отслеживание чтения скиллов (skill reads)

- `_SKILL_TOOLS = frozenset({"read_file", "ls", "glob"})` (строка 18)
- `on_tool_start()` (строка 174) — при вызове инструмента из этого набора отслеживает путь через `_skill_name_from_tool_input()`
- `_skill_name_from_tool_input()` (строка 123) — извлекает имя скилла из пути `/skills/<skill_name>/...` с помощью `_SKILL_PATH_RE`
- Результат записывается в `tracker.record_skill_read(subagent_name, skill_name)` (строка 194)
- **Вывод:** skill reads трекаются во время выполнения task ✅

## ✅ 4. Progress observability (LiveProgress)

- Файл: `orchestrator.py`
- Параметр `progress` передаётся в `run()` (строка 105) и пробрасывается далее
- `progress.phase(...)` вызывается на этапах:
  - `"parse"` (строка 110)
  - `"chat"` (строки 124, 144)
  - `"acquire-code"` (строка 165)
  - `"select-rubric"` (строка 173)
  - `"materialize-skills"` (строка 176)
  - `"agent-review"` (строка 220)
  - `"synthesize"` (строка 235)

- Файл: `context_tracker.py`
- `TokenUsageCallback._notify_tool()` (строка 170) — вызывает `progress.tool(tool_name, detail)` при запуске инструментов сабагентами
- `progress` передаётся в `TokenUsageCallback(tracker, progress=progress)` (оркестратор, строка 222)
- **Вывод:** прогресс отслеживается: фазы + вызовы инструментов ✅

## ✅ 5. Token observability (метрики контекста)

- `ContextTracker` собирает:
  - `steps: list[ContextStep]` — все шаги с prompt/completion/total токенами
  - `summarizations: int` — количество суммаризаций
  - `offloads: int` — количество оффлоадов
  - `parent_peak_tokens` и `subagent_peak_tokens` — пиковые значения
  - `record_offload()` — фиксирует оффлоад (используется для code-index, строка 170 оркестратора)
  - `record_summarization()` — фиксирует суммаризацию (используется при наличии conversation_history, строка 277)
- `RunResult` (оркестратор, строка 66) включает `tracker: ContextTracker` для внешнего анализа
- **Вывод:** все метрики контекста собираются и доступны ✅

---

## Итог

| Критерий | Статус |
|---|---|
| SummarizationMiddleware настроена (0.55, backend) | ✅ |
| Parent vs subagent контекст разделён | ✅ |
| Skill reads трекаются | ✅ |
| Progress observability (фазы + инструменты) | ✅ |
| Token observability (метрики контекста) | ✅ |
