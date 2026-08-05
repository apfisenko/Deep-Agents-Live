# `companion/drill/` — A2UI-модуль drill-режима

Модуль генерации **динамических форм кейса** для тренажёра (ступень 4 практики):
companion решает, ЧТО спросить (кейс), этот модуль — КАК отрисовать. Форма
описывается протоколом [A2UI v0.9](https://a2ui.org) и рождается в рантайме —
фронт заранее её не знает.

Статус: **модуль вмонтирован в живую систему** — сначала был готов
и проверен на своём стенде, затем подключён к companion: endpoint живёт на
сервере companion через `http.app` (`companion/webapp.py` + `langgraph.json`),
кейс приходит из канала `drill_case` стейта (тул `show_drill_case`; сам кейс
companion генерирует по скиллу `scaling-case-drill` из `data/skills/`), surface —
в общем фронте (`frontend/src/DrillPanel.tsx`). Чек-лист интеграции ниже
(«Как модуль подключён») сохранён как справка — все пункты выполнены.

## Как устроено

Три части, каждая — свой файл:

```
кейс (JSON) ──> generator.py ──> SSE: A2UI-сообщения ──> @a2ui/react surface
                (один LLM-вызов)                             │ заполнил, нажал
                                                             v
тред companion <── delivery.py <── routes.py <── POST userAction
   (разбор текстом в чат)         (langgraph_sdk, enqueue)
```

- **`case.py` — вход модуля.** `DrillCase`: текст сценария, оси выбора с
  вариантами (`axes[].id/question/options`), свободный вопрос. Компактная
  JSON-структура: companion кладёт такую в свой стейт, фронт постит её сюда.
- **`generator.py` — форма = один отдельный LLM-вызов.** System-промпт
  собирает `A2uiSchemaManager`: правила + полные JSON-схемы каталога + наш
  шаблонный пример `examples/0.9.1/drill_form.json` (~11K токенов — потому и
  изолировано от промпта companion). Токены LLM гонятся через
  `A2uiStreamParser`: сообщения валидируются и уезжают клиенту по мере
  генерации, форма «проявляется» инкрементально. Невалидная попытка
  (`A2uiParseError` / строгая валидация / неполная форма) — частичные
  поверхности убираются `deleteSurface`, попытка повторяется
  (до `max_attempts`, потом `FormGenerationError` -> SSE-ошибка).
- **`routes.py` — транспорт.** Один `POST /drill/a2ui`:
  тело `{"case": {...}}` -> SSE-стрим формы; тело
  `{"version": "v0.9", "action": {...}, "threadId": "..."}` -> доставка ответа
  + ack-поверхность. Формат SSE-событий — как у референсного shell'а Google:
  `data: [{"kind": "data", "data": <a2ui-msg>}]`. Наружу отдаются и
  `APIRouter` (вмонтировать в сервер companion), и `create_drill_app()`
  (отдельный порт :8123).
- **`delivery.py` — ответ студента в тред companion.** `userAction.context`
  (значения формы, разрешённые из data model по биндингам) упаковывается в
  служебное сообщение и уезжает фоновым раном через `langgraph_sdk`
  (`runs.create(..., multitask_strategy="enqueue")`) — companion отвечает
  разбором в обычный чат. Клиент параметризуем: тесты и стенд подставляют фейк.

### Контракт с формой (то, на что может рассчитывать потребитель)

- `surfaceId` формы = `drill-<case_id>` — по нему userAction соотносится с кейсом;
- выбор по оси `axes[i].id` лежит в `userAction.context[<id>]` (список значений),
  свободный ответ — в `context["rationale"]`;
- событие кнопки — `submit_drill_answer`.

Комплектность этого контракта генератор проверяет сам после каждой попытки
(валидатор SDK гарантирует только схемность отдельных сообщений).

## Мини-стенд (`devstand/`, dev-only)

Живой прогон модуля без companion: кейс-заглушка «выбор протокола на шов»
захардкожен в `devstand/server.py`, доставка пишется в лог-заглушку
(`GET /devstand/delivered`).

```bash
# 1. Сервер drill-endpoint'а (:8123); python-зависимости — в devstand/pyproject.toml
cd companion/drill/devstand
uv sync
uv run python server.py

# 2. Клиент (:5273)
cd client
npm install --legacy-peer-deps   # без флага упадёт, см. «Грабли» №1
npm run dev
# браузером на http://localhost:5273 (не 127.0.0.1 — vite слушает ::1)

# Тесты модуля (фейковые LLM/SDK-клиент, сети не надо)
cd companion/drill/devstand
uv run pytest ../tests

# Демо retry-пути: первая LLM-попытка искусственно ломается
DRILL_FAIL_FIRST=1 uv run python server.py
```

Нужен `.env` в корне course-companion (`OPENAI_API_KEY` / `OPENAI_BASE_URL` /
`OPENAI_MODEL`) — генерация формы живая.

Артефакты живых прогонов (скрины формы, доставленный userAction, лог retry) —
в `devstand/run-artifacts/`.

## Грабли версий

1. `npm install` без `--legacy-peer-deps` падает: `@a2ui/markdown-it@0.0.4`
   требует peer `@a2ui/web_core@^0.9.2` при актуальном 0.10.1.
2. `catalogId` — только литеральный v0_9-URL
   (`https://a2ui.org/specification/v0_9/catalogs/basic/catalog.json`):
   `BasicCatalog.get_catalog_id("0.9.1")` вернёт v0_9_1-URL, которого клиент
   не знает («Unknown catalog»).
3. Импорты клиента строго `@a2ui/react/v0_9` и `@a2ui/web_core/v0_9` —
   дефолтный экспорт пакетов до сих пор сломанный v0_8.
4. Версия в сообщениях — всегда `"v0.9"` (клиентские zod-схемы не знают `"v0.9.1"`).
5. Стрим-парсер лечит только фрагментацию; синтаксическую ошибку он кидает
   `A2uiParseError`, а невалидные куски молча дропает — отсюда retry +
   собственная проверка комплектности формы.

Пины: `a2ui-agent-sdk==0.4.0`, `@a2ui/react@0.10.1`, `@a2ui/web_core@0.10.1`.
Экосистема ломается между минорами — не обновлять без нужды.

## Как модуль подключён к companion

1. ✅ **Python-зависимости** модуля (`a2ui-agent-sdk`, `fastapi`, `langgraph-sdk`,
   `openai`) — в корневом `pyproject.toml` course-companion; тесты модуля
   гоняются вместе с корневыми (`uv run pytest`).
2. ✅ **Endpoint** — `build_drill_router(...)` вмонтирован в сервер companion:
   `companion/webapp.py` + `http.app` в `langgraph.json` (канал 2 живёт на
   :2024); `create_drill_app()` на :8123 остался запасным путём
   (у фронта — env `DRILL_PROXY_TARGET`).
3. ✅ **Кейс из стейта:** тул `show_drill_case` (companion/modes.py, только
   «лицо» drill) кладёт `DrillCase`-JSON в канал `drill_case`; фронт видит его
   через useStream и постит на `/drill/a2ui`.
4. ✅ **Surface в общем фронте:** ядро devstand-клиента перенесено в
   `frontend/src/DrillPanel.tsx` + `frontend/src/a2ui.ts`; `threadId` — из
   живого чата; панель закрывается по приходу разбора в чат.
5. ✅ **Delivery по-настоящему:** `CompanionDelivery()` без параметров идёт на
   `COMPANION_URL` (по умолчанию `http://127.0.0.1:2024`, assistant
   `companion`) — loopback в тот же сервер; заглушка осталась только стенду.

Живой сквозной прогон (форма → userAction → разбор в чате; фидбек фоновой
проверки посреди дрилла) — `examples/walkthrough/`.
