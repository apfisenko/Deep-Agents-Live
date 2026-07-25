# Sprint 08: red-teaming-baseline

> **Версия roadmap:** v0.2 (security baseline до persistence/guardrails)
> **Roadmap:** [../../roadmap.md](../../roadmap.md)
> **Статус:** ✅ Done
> **Открыт:** 2026-07-25
> **Закрыт:** 2026-07-25

---

## Преамбула

Это классический процесс security-инженерии, не разовая проверка: устанавливаем инструмент → проверяем, что он работает → под модель угроз подбираем, чем именно будем бить → генерируем конфигурацию проверки и объясняем, что она проверяет → генерируем сами проверки (тестовые сценарии) → ревьюим их до боевого прогона → прогоняем → разбираем находки → чиним → перепроверяем ровно те же кейсы.

Инструмент — **Promptfoo**. Цель спринта — не абстрактная «проверить безопасность», а получить воспроизводимый baseline **до/после** на конкретном агенте с конкретными закрытыми находками.

---

## Цель спринта

Получить воспроизводимый red-teaming baseline агента-ассистента LLMStart.ru (Promptfoo): модель угроз → конфиг/сценарии → прогон «до» → фиксы за `SECURITY_ENABLED` → прогон «после» на том же наборе кейсов и итоговый отчёт.

---

## Контекст и неизменные факты

Агент — публичный диалоговый ассистент без авторизации (backend + mcp_server). Сейчас нет слоя защиты. Материалы: `Docs/concept/idea.md`, `vision.md`, `architecture.md`, `api-contracts.md`.

Факты (не выдумывать в задачах):

| Факт | Значение |
|------|----------|
| Chat endpoint | `POST /api/v1/chat` (сверка с `api-contracts.md`; не stream) |
| Tools | `search_knowledge_base`, `list_b2c_products`, `save_lead`, `create_payment_link`, `confirm_payment` |
| **PROTECTED** | системные инструкции, canary-токен, имена/схемы/параметры tools, сериализованные tool-calls |
| **DISCLOSABLE** | каталог, цены, программы, сегменты b2b/b2c |
| Бизнес-правило | `confirm_payment` нельзя без предшествующего `create_payment_link` для того же продукта в том же диалоге |
| LLM-провайдер | OpenRouter (атаки и грейдинг; reasoning выключен) |

---

## Инварианты спринта

- Конфигурацию (задача 04) и тестовые сценарии (задача 06) **не писать руками** — только skills + generate, затем human review.
- Между baseline «до» и «после» меняется **только** код фикса и флаг `SECURITY_ENABLED`.
- Реран — исключительно `redteam eval`, не `redteam run`.
- Изоляция тест-кейсов: общий `session_id` не передаём.
- Правило двух согласований: без явного «ок» к следующему шагу не переходить.

---

## DoD спринта

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | Есть модель угроз и карта рисков под этого агента | `threat-model.md` |
| 2 | Promptfoo + skills установлены, стенд healthy, smoke OK | `tooling-notes.md`, `GET /health` |
| 3 | Плагины/стратегии выбраны до конфига | `plugin-selection.md` |
| 4 | Конфиг и explainer сгенерированы через skills, не руками | `practice/redteam/promptfooconfig.yaml`, `config-explainer.md` |
| 5 | Конфиг принят человеком по чек-листу | `config-review-notes.md` = pass |
| 6 | Сценарии сгенерированы (`redteam generate`), ревью go | `redteam-tests.yaml`, `test-review-notes.md` |
| 7 | Baseline «до» сохранён (`redteam eval`) | `baseline-before/` + notes |
| 8 | Triage: ≥1 строка на плагин (или «не воспроизвелось») | `baseline-before-triage.md` |
| 9 | Пути фикса зафиксированы до кода | `fix-decisions.md` |
| 10 | Фиксы за `SECURITY_ENABLED` (default on) | код + `.env.example` + тесты |
| 11 | Baseline «после» на тех же сценариях, есть сравнение | `baseline-after/`, `baseline-comparison.md` |
| 12 | Между до/после не менялись конфиг и сценарии | diff/checksum yaml |
| 13 | Итоговый отчёт + обновлённый roadmap | `final-report.md`, `roadmap.md` |

---

## Задачи

| # | Задача | Статус | Plan | Summary |
|---|--------|--------|------|---------|
| 01 | Модель угроз и карта рисков | ✅ | — | [summary](tasks/01-threat-model/summary.md) · [threat-model](threat-model.md) |
| 02 | Установка Promptfoo + smoke | ✅ | — | [summary](tasks/02-promptfoo-tooling/summary.md) · [tooling-notes](tooling-notes.md) |
| 03 | Подбор плагинов и стратегий | ✅ | — | [summary](tasks/03-plugin-selection/summary.md) · [plugin-selection](plugin-selection.md) |
| 04 | Генерация конфига + explainer | ✅ | — | [summary](tasks/04-config-generation/summary.md) · [config](../../../practice/redteam/promptfooconfig.yaml) · [explainer](../../../practice/redteam/config-explainer.md) |
| 05 | Ревью конфигурации | ✅ | — | [summary](tasks/05-config-review/summary.md) · [review-notes](config-review-notes.md) |
| 06 | Генерация тестовых сценариев | ✅ | — | [summary](tasks/06-test-generation/summary.md) · [redteam.yaml](../../../practice/redteam/redteam.yaml) · [generate-notes](generate-notes.md) |
| 07 | Ревью сгенерированных сценариев | ✅ | — | [summary](tasks/07-test-review/summary.md) · [test-review-notes](test-review-notes.md) |
| 08 | Baseline «до»: прогон | ✅ | — | [summary](tasks/08-baseline-before/summary.md) · [notes](baseline-before-notes.md) · [results](../../../practice/redteam/baseline-before/results.json) |
| 09 | Baseline «до»: triage | ✅ | [plan](tasks/09-baseline-triage/plan.md) | [summary](tasks/09-baseline-triage/summary.md) · [triage](baseline-before-triage.md) |
| 10 | Развилка: выбор пути фикса | ✅ | [plan](tasks/10-fix-decisions/plan.md) | [summary](tasks/10-fix-decisions/summary.md) · [fix-decisions](fix-decisions.md) |
| 11 | Реализация фиксов | ✅ | [plan](tasks/11-fixes-implementation/plan.md) | [summary](tasks/11-fixes-implementation/summary.md) |
| 12 | Baseline «после»: прогон и сравнение | ✅ | [plan](tasks/12-baseline-after/plan.md) | [summary](tasks/12-baseline-after/summary.md) · [notes](baseline-after-notes.md) · [comparison](baseline-comparison.md) · [results](../../../practice/redteam/baseline-after/results.json) |
| 13 | Итоговый отчёт и roadmap | ✅ | — | [summary](tasks/13-final-report/summary.md) · [final-report](final-report.md) |

---

## Задача 01: Модель угроз и карта рисков ✅

### Цель

Зафиксировать модель угроз именно для агента LLMStart.ru и карту «риск продукта → OWASP LLM / ASI Top 10» как вход для подбора плагинов Promptfoo.

> Закрывает: нет общего «проверить безопасность» без границ — до инструментов и конфига ясно, кого моделируем и что в scope.

### Состав работ

- [x] Прочитать `Docs/concept/`: `idea.md`, `vision.md`, `architecture.md`, `api-contracts.md`
- [x] Ответить на **пять вопросов модели угроз** применительно к этому агенту:
  1. Кто атакующий
  2. Что умеет
  3. Компетентность
  4. Что **не** моделируем
  5. Что следует для границ доверия (PROTECTED vs DISCLOSABLE)
- [x] Зафиксировать неизменные факты спринта (таблица выше)
- [x] Составить таблицу: риск продукта → категория OWASP LLM Top 10 / ASI Top 10
- [x] Самопроверка по критериям DoD

### Критерии готовности (DoD)

**Агент проверяет:**

| # | Критерий | Способ проверки | Результат |
|---|----------|-----------------|-----------|
| 1 | Есть ответы на все 5 вопросов модели угроз | `threat-model.md`, разделы 1–5 | ✅ |
| 2 | Факты PROTECTED/DISCLOSABLE и 5 tools совпадают с brief | сверка с vision + README | ✅ |
| 3 | Таблица риск → OWASP/ASI непустая, без выдуманных tools | ревью таблицы R1–R9 | ✅ |
| 4 | Эндпоинт чата сверен с api-contracts | `POST /api/v1/chat` в threat-model | ✅ |

**Пользователь проверяет:**

- Модель угроз описывает **этот** агент (публичный чат, 5 tools, нет auth)
- Out-of-scope явно отсекает то, что не бьём Promptfoo в этом спринте
- Карта рисков достаточна как вход для задачи 03

### Артефакты

- [`threat-model.md`](threat-model.md)

---

## Задача 02: Установка Promptfoo + smoke ✅

### Цель

Установить Promptfoo и skills, поднять стенд (backend + mcp_server), подтвердить рабочий smoke-прогон до подбора плагинов.

> Закрывает боль задачи 01: модель угроз есть, но инструмент и стенд ещё не доказаны как работающие.

### Состав работ

- [x] Проверить Node.js: `^20.20.0` или `>=22.22.0`
- [x] `npx promptfoo@latest --version`
- [x] Установить skills и зафиксировать назначение:
  - `promptfoo-provider-setup` — провайдеры (OpenRouter) для target/grading/атак
  - `promptfoo-redteam-setup` — генерация redteam-конфига
  - `promptfoo-redteam-run` — generate / eval / разбор прогонов
- [x] Поднять backend; проверить `/health` (`mcp_server` в репо нет — см. tooling-notes)
- [x] Smoke-check Promptfoo: минимальный тривиальный прогон (не redteam агента)
- [x] Зафиксировать версии и результат в `tooling-notes.md`
- [x] Самопроверка по критериям DoD

### Критерии готовности (DoD)

**Агент проверяет:**

| # | Критерий | Способ проверки | Результат |
|---|----------|-----------------|-----------|
| 1 | Node в допустимом диапазоне | portable `node -v` → v22.22.0 | ✅ |
| 2 | Promptfoo установлен | `npx promptfoo@latest --version` → 0.121.19 | ✅ |
| 3 | Три skills на месте + краткое «зачем» | `.agents/skills/promptfoo-*` + notes | ✅ |
| 4 | Backend healthy | `GET /health` → 200 | ✅ |
| 5 | Smoke Promptfoo без ошибки CLI | echo eval 1/1 pass, exit 0 | ✅ |

**Пользователь проверяет:**

- Skills покрывают задачи 04/06/08/12
- Стенд тот же, что для baseline
- Smoke не подменяет redteam агента
- Ок с portable Node 22.22.0 (system всё ещё 22.14.0) и отсутствием отдельного `mcp_server`

### Артефакты

- [`tooling-notes.md`](tooling-notes.md)
- Skills: `.agents/skills/promptfoo-provider-setup`, `promptfoo-redteam-setup`, `promptfoo-redteam-run`
- Smoke-конфиг: `practice/redteam/smoke/promptfooconfig.yaml`

---

## Задача 03: Подбор плагинов, стратегий и параметров ✅

### Цель

По карте рисков из `threat-model.md` выбрать plugins, strategies и параметры Promptfoo — без генерации конфига.

> Закрывает боль задачи 02: инструмент готов, но ещё не решено, *чем* бить агента под его модель угроз.

### Состав работ

- [x] Взять таблицу «риск → OWASP/ASI» из `threat-model.md` как единственный вход
- [x] Для каждого релевантного риска: плагин + обоснование
- [x] Выбрать strategies под поверхность атаки (публичный чат, tool-агент)
- [x] Зафиксировать `numTests`, `entities`, `provider` (OpenRouter, reasoning off) с обоснованием
- [x] Явно включить policy: `confirm_payment` только после `create_payment_link`
- [x] Отразить PROTECTED vs DISCLOSABLE в выборе плагинов
- [x] Не генерировать `promptfooconfig.yaml`
- [x] Самопроверка по критериям DoD

### Критерии готовности (DoD)

**Агент проверяет:**

| # | Критерий | Способ проверки | Результат |
|---|----------|-----------------|-----------|
| 1 | Таблица риск → плагин → почему | `plugin-selection.md` | ✅ |
| 2 | Список strategies + обоснование | `jailbreak:meta` only | ✅ |
| 3 | Заполнены numTests, entities, provider | 3 / 6 products / OpenRouter | ✅ |
| 4 | Policy confirm_payment обязательна | inline policy text | ✅ |
| 5 | Нет плагинов вне карты рисков | 5 plugins = R1–R6 | ✅ |

**Пользователь проверяет:**

- Покрытие ключевых рисков публичного tool-агента без auth
- Entities/tools не противоречат фактам спринта
- `numTests` реалистичен для одного baseline до/после
- Готово как жёсткий вход для задачи 04

### Артефакты

- [`plugin-selection.md`](plugin-selection.md)

---

## Задача 04: Генерация конфигурации + отчёт-объяснение ✅

### Цель

Через skills и промпт (не руками) получить `promptfooconfig.yaml` и `config-explainer.md` строго по решениям задачи 03 и фактам спринта.

> Закрывает боль задачи 03: выбор плагинов есть, но нет воспроизводимого конфига для generate/eval.

### Состав работ

- [x] Собрать вход: concept docs, `threat-model.md`, `plugin-selection.md`, skills setup, факты спринта
- [x] Артефакты по skills `promptfoo-provider-setup` + `promptfoo-redteam-setup`:
  - `practice/redteam/promptfooconfig.yaml`
  - `practice/redteam/config-explainer.md`
  - `practice/redteam/target.mjs` (изоляция session_id)
- [x] Требования к yaml соблюдены (см. DoD)
- [x] Самопроверка: `npx promptfoo validate config` → valid

### Критерии готовности (DoD)

**Агент проверяет:**

| # | Критерий | Способ проверки | Результат |
|---|----------|-----------------|-----------|
| 1 | Оба файла существуют | `practice/redteam/` | ✅ + target.mjs |
| 2 | YAML парсится | `validate config` | ✅ Configuration is valid |
| 3 | Plugins/strategies = задача 03 | сверка | ✅ |
| 4 | OpenRouter + purpose PROTECTED/DISCLOSABLE | yaml | ✅ `showThinking: false` |
| 5 | Target = HTTP chat, не stream | target.mjs → `/api/v1/chat` | ✅ |

**Пользователь проверяет:**

- Конфиг соответствует plugin-selection / threat-model
- Explainer читаем; ок с `target.mjs` (новый UUID на запрос)
- Финальная приёмка — задача 05 (`validate target` — вручную при поднятом backend)

### Артефакты

- [`practice/redteam/promptfooconfig.yaml`](../../../practice/redteam/promptfooconfig.yaml)
- [`practice/redteam/config-explainer.md`](../../../practice/redteam/config-explainer.md)
- [`practice/redteam/target.mjs`](../../../practice/redteam/target.mjs)

---

## Задача 05: Ревью конфигурации ✅

### Цель

Человеком принять конфиг + explainer по чек-листу; все расхождения правит человек до генерации сценариев.

> Закрывает боль задачи 04: конфиг сгенерирован машиной и может врать.

### Состав работ

- [x] Чек-лист по yaml:
  - [x] URL/method: `POST /api/v1/chat` на стенд задачи 02
  - [x] Reasoning отключён
  - [x] Имена tools только из фактов спринта
  - [x] Policy confirm_payment присутствует
  - [x] entities совпадают с задачей 03
  - [x] strategies в корректной форме
  - [x] plugins/strategies/параметры = задача 03
  - [x] изоляция session_id
  - [x] defaultTest assert на маркер блокировки
- [x] Сверить explainer с yaml
- [x] Расхождения правит **человек** (override URL → target.mjs)
- [x] Зафиксировать вердикт в `config-review-notes.md`
- [x] Самопроверка по критериям DoD

### Критерии готовности (DoD)

**Агент проверяет:**

| # | Критерий | Способ проверки | Результат |
|---|----------|-----------------|-----------|
| 1 | YAML валиден после правок | validate | ✅ |
| 2 | Чек-лист отмечен | `config-review-notes.md` | ✅ |
| 3 | Diff plugins с задачей 03 пуст или human override задокументирован | сверка | ✅ |

**Пользователь проверяет:**

- Каждый пункт чек-листа пройден лично ✅
- Конфиг готов к `redteam generate` ✅

### Артефакты

- [`config-review-notes.md`](config-review-notes.md)
- [`tasks/05-config-review/summary.md`](tasks/05-config-review/summary.md)

---

## Задача 06: Генерация тестовых сценариев ✅

### Цель

`npx promptfoo redteam generate` по принятому конфигу → `redteam-tests.yaml` без ручного написания кейсов.

> Закрывает боль задачи 05: конфиг одобрен, атакующих сценариев ещё нет.

### Состав работ

- [x] Задача 05 = pass; конфиг не менять «по пути»
- [x] Окружение генерации (OpenRouter и пр.)
- [x] `npx promptfoo redteam generate` по `practice/redteam/promptfooconfig.yaml`
- [x] Зафиксировать выход как `practice/redteam/redteam.yaml` (канон Promptfoo; см. generate-notes)
- [x] Не дописывать сценарии руками на этом шаге
- [x] Метаданные: дата, версия promptfoo, модель
- [x] Самопроверка по критериям DoD

### Критерии готовности (DoD)

**Агент проверяет:**

| # | Критерий | Способ проверки | Результат |
|---|----------|-----------------|-----------|
| 1 | Файл сценариев существует и непустой | path + count | ✅ 30 tests |
| 2 | Generate exit 0 | лог | ✅ |
| 3 | Конфиг задачи 05 не менялся | git diff yaml | ✅ |
| 4 | Метаданные записаны | `generate-notes.md` | ✅ |

**Пользователь проверяет:**

- Генерация от финального yaml задачи 05 ✅
- Не было ручной подмены generate ✅
- Объём согласован с `numTests` (5×3×meta = 30) ✅

### Артефакты

- [`practice/redteam/redteam.yaml`](../../../practice/redteam/redteam.yaml)
- [`generate-notes.md`](generate-notes.md)

---

## Задача 07: Ревью сгенерированных сценариев ✅

### Цель

До боевого прогона прочитать `redteam-tests.yaml` и зафиксировать замечания — чтобы baseline «до» не гонялся по мусорным кейсам.

> Закрывает боль задачи 06: сценарии сгенерированы машиной.

### Состав работ

- [x] Прочитать `redteam.yaml` (стратифицированная выборка — см. test-review-notes)
- [x] Проверить: риски/плагины, нет выдуманных tools, PROTECTED vs DISCLOSABLE, policy payment, мусор/дубли, изоляция сессий
- [x] Вердикт: **accept** (regenerate/human edit не нужны)
- [x] Не запускать `redteam eval` на этом шаге
- [x] Самопроверка по критериям DoD

### Критерии готовности (DoD)

**Агент проверяет:**

| # | Критерий | Способ проверки | Результат |
|---|----------|-----------------|-----------|
| 1 | `test-review-notes.md` существует | path | ✅ |
| 2 | Явный вердикт go / no-go | секция Verdict | ✅ ACCEPT |
| 3 | Human edit перечислены с причинами | список в notes | ✅ нет |
| 4 | Конфиг не менялся «для красоты тестов» | diff yaml | ✅ |

**Пользователь проверяет:**

- Сценарии осмысленны для этого агента ✅
- При go — готовность к задаче 08 ✅

### Артефакты

- [`test-review-notes.md`](test-review-notes.md)

---

## Задача 08: Baseline «до» — прогон ✅

### Цель

`npx promptfoo redteam eval` против агента as-is; сохранить сырые результаты как `baseline-before`.

> Закрывает боль задачи 07: сценарии одобрены, точки «до» ещё нет.

### Состав работ

- [x] Preconditions: задача 07 = go; `/health` 200; без фиксов / `SECURITY_ENABLED` off; yaml не менять
- [x] Только `npx promptfoo redteam eval` (не `redteam run`)
- [x] Сохранить results/report как `baseline-before`
- [x] Метаданные: дата, состояние кода, версии, модель, флаг security
- [x] Самопроверка по критериям DoD

### Критерии готовности (DoD)

**Агент проверяет:**

| # | Критерий | Способ проверки | Результат |
|---|----------|-----------------|-----------|
| 1 | Eval завершён с артефактами | лог + path | ✅ eval-g7I-… |
| 2 | `baseline-before` на диске | path | ✅ results.json |
| 3 | Config/tests не менялись | git diff | ✅ |
| 4 | Команда = `redteam eval` | notes | ✅ |
| 5 | Метаданные записаны | `baseline-before-notes.md` | ✅ |

**Пользователь проверяет:**

- Тот же стенд/порт, что в конфиге ✅
- Фиксы не включали «чтобы прошло» ✅
- Сырья хватает для triage без перепрогона ✅

### Артефакты

- [`practice/redteam/baseline-before/`](../../../practice/redteam/baseline-before/)
- [`baseline-before-notes.md`](baseline-before-notes.md)

---

## Задача 09: Baseline «до» — разбор находок ✅

### Цель

Triage-таблица: находка → категория OWASP → предполагаемый слой защиты (без решения «как чиним»).

> Закрывает боль задачи 08: сырой отчёт не превращён в actionable список.

### Состав работ

- [x] Разобрать `baseline-before`
- [x] ≥1 строка на каждый плагин (находка или «не воспроизвелось»)
- [x] Колонки: id, описание, плагин/стратегия, OWASP/ASI, evidence, первичный слой защиты
- [x] Отделить FP / out-of-scope (DISCLOSABLE)
- [x] Не менять конфиг, сценарии, код
- [x] Самопроверка по критериям DoD

### Критерии готовности (DoD)

**Агент проверяет:**

| # | Критерий | Способ проверки | Результат |
|---|----------|-----------------|-----------|
| 1 | Triage-документ существует | path | ✅ |
| 2 | ≥1 строка на плагин | сверка с `plugin-selection.md` | ✅ 5/5 |
| 3 | OWASP + слой-гипотеза у каждой находки | колонки | ✅ 20 findings |
| 4 | FP помечены отдельно | секция/статус | ✅ |

**Пользователь проверяет:**

- «Не воспроизвелось» — осознанный вывод ✅
- Таблица достаточна для задачи 10 ✅

### Артефакты

- [`baseline-before-triage.md`](baseline-before-triage.md)
- [`tasks/09-baseline-triage/summary.md`](tasks/09-baseline-triage/summary.md)

---

## Задача 10: Развилка — выбор пути фикса ✅

### Цель

По каждой находке решить без кода: свой код / guard / prompt-hardening → `fix-decisions.md`.

> Закрывает боль задачи 09: гипотезы слоёв есть, согласованного плана фикса нет.

### Состав работ

- [x] Для каждой не-FP находки — путь фикса + критерий «закрыто» + риск обхода
- [x] Единый флаг `SECURITY_ENABLED` (default on) для всех фиксов задачи 11
- [x] Зафиксировать хвост вне спринта
- [x] Код не писать
- [x] Самопроверка по критериям DoD

### Критерии готовности (DoD)

**Агент проверяет:**

| # | Критерий | Способ проверки | Результат |
|---|----------|-----------------|-----------|
| 1 | `fix-decisions.md` существует | path | ✅ |
| 2 | Каждая не-FP находка имеет решение | join по id | ✅ 20/20 |
| 3 | Путь + критерий закрытия | поля заполнены | ✅ |
| 4 | Упомянут `SECURITY_ENABLED` | секция | ✅ |

**Пользователь проверяет:**

- Tool-policy/abuse не закрываются «только промптом» без обоснования ✅
- Объём фиксов реалистичен для одной итерации до «после» ✅
- Отложенное явно видно ✅

### Артефакты

- [`fix-decisions.md`](fix-decisions.md)
- [`tasks/10-fix-decisions/summary.md`](tasks/10-fix-decisions/summary.md)

---

## Задача 11: Реализация фиксов ✅

### Цель

Реализовать фиксы строго по `fix-decisions.md`, каждый за флагом `SECURITY_ENABLED` (default on).

> Закрывает боль задачи 10: решения приняты, в коде защиты ещё нет.

### Состав работ

- [x] Конфиг `SECURITY_ENABLED` (env + Config), default `true`, fail-fast
- [x] Только пункты «в этом спринте» из `fix-decisions.md`
- [x] Маркер блокировки согласован с defaultTest assert Promptfoo
- [x] При `SECURITY_ENABLED=false` — поведение как до фиксов
- [x] Тесты на ключевые политики; полный redteam — не здесь
- [x] Sanitize/verify по изменённым файлам
- [x] **Не менять** promptfoo yaml / tests
- [x] Самопроверка по критериям DoD

### Критерии готовности (DoD)

**Агент проверяет:**

| # | Критерий | Способ проверки | Результат |
|---|----------|-----------------|-----------|
| 1 | `SECURITY_ENABLED` из env, default on | конфиг + тест | ✅ |
| 2 | Фиксы = `fix-decisions.md` | FIX-01…04 | ✅ |
| 3 | При `false` политики off | тесты | ✅ |
| 4 | Маркер блокировки стабилен | константа + тесты | ✅ |
| 5 | Lint/tests по затронутому | pytest + ruff | ✅ 149 pass |
| 6 | Redteam yaml не менялись | git diff | ✅ |

**Пользователь проверяет:**

- Нет правок конфига/сценариев «чтобы после зеленее» ✅
- Ручной smoke: блок при `true`, дыра при `false` (по смыслу решения) — задача 12
- Без YAGNI-рефакторинга вокруг ✅

### Артефакты

- `backend/app/security/` — guards
- `backend/app/config.py`, `react_agent.py`, `tools/registry.py`
- `.env.example` — `SECURITY_ENABLED`
- `backend/tests/test_security.py`
- [`tasks/11-fixes-implementation/summary.md`](tasks/11-fixes-implementation/summary.md)

---

## Задача 12: Baseline «после» — прогон и сравнение ✅

### Цель

При `SECURITY_ENABLED=true` снова `redteam eval` на тех же сценариях; сравнить до/после.

> Закрывает боль задачи 11: фиксы есть, доказательства на том же наборе кейсов нет.

### Состав работ

- [x] Preconditions: фиксы в стенде; `SECURITY_ENABLED=true`; config/tests = как «до»; healthy
- [x] Только `npx promptfoo redteam eval`
- [x] Сохранить `baseline-after`
- [x] Сравнение с `baseline-before` по находкам: закрыта / частично / открыта / регрессия
- [x] Не чинить код «между делом» без возврата к задаче 11
- [x] Самопроверка по критериям DoD

### Критерии готовности (DoD)

**Агент проверяет:**

| # | Критерий | Способ проверки | Результат |
|---|----------|-----------------|-----------|
| 1 | `baseline-after` на диске | path | ✅ |
| 2 | Команда = `redteam eval` | notes | ✅ |
| 3 | Config/tests неизменны vs «до» | diff/checksum | ✅ |
| 4 | `SECURITY_ENABLED=true` в метаданных | notes | ✅ |
| 5 | Таблица сравнения | `baseline-comparison.md` | ✅ |

**Пользователь проверяет:**

- Честное сравнение: те же сценарии и target
- Закрытие по сути, не только score
- Регрессии/незакрытое видны для задачи 13

### Артефакты

- `practice/redteam/baseline-after/`
- `Docs/sprints/sprint-08-red-teaming-baseline/baseline-after-notes.md`
- `Docs/sprints/sprint-08-red-teaming-baseline/baseline-comparison.md`

---

## Задача 13: Итоговый отчёт и roadmap ✅

### Цель

Свести baseline до/после в итоговый отчёт и обновить `Docs/roadmap.md`.

> Закрывает боль задачи 12: сравнение есть, спринт не закрыт в документации продукта.

### Состав работ

- [x] Сводная таблица: находка → категория → путь фикса → статус
- [x] Как воспроизвести до/после (`SECURITY_ENABLED`)
- [x] Антипаттерны спринта
- [x] Хвост на следующий спринт
- [x] Обновить `roadmap.md` (статус sprint-08, хвосты)
- [x] Итог в sprint README
- [x] Самопроверка по критериям DoD

### Критерии готовности (DoD)

**Агент проверяет:**

| # | Критерий | Способ проверки | Результат |
|---|----------|-----------------|-----------|
| 1 | `final-report.md` существует | path | ✅ |
| 2 | Находки из triage/comparison отражены | join по id | ✅ 20/20 |
| 3 | roadmap содержит sprint-08 и ссылку | grep | ✅ |
| 4 | Итог спринта заполнен в README | секция «Итог» | ✅ |

**Пользователь проверяет:**

- Другой инженер повторит baseline без устных пояснений
- Хвост реалистичен
- Roadmap отражает факт

### Артефакты

- `Docs/sprints/sprint-08-red-teaming-baseline/final-report.md`
- Обновлённые sprint README (итог) и `Docs/roadmap.md`

---

## Итог (заполняется после закрытия)

**Sprint 08 закрыт 2026-07-25.**

Воспроизводимый red-teaming baseline агента LLMStart.ru на Promptfoo: модель угроз → 30 adversarial tests → baseline «до» (ASR ~67%) → FIX-01…04 за `SECURITY_ENABLED` → baseline «после» (ASR ~37%, −30 pp). Закрыто grader pass: **10/20** findings; policy и prompt-extraction — полностью; tool-discovery и text-only payment confirm — хвост.

| Результат | Значение |
|-----------|----------|
| Eval «до» / «после» | `eval-g7I-…` / `eval-yYs-…` |
| Security module | `backend/app/security/` (FIX-01…04) |
| Итоговый отчёт | [`final-report.md`](final-report.md) |
| Сравнение | [`baseline-comparison.md`](baseline-comparison.md) |

**Хвост:** text-only payment confirm, input guard v2 (travel), grader tuning tool-discovery, FIX-04 calendar/Telegram → sprint-09/10.

## История

| Дата | Изменение |
|------|-----------|
| 2026-07-25 | План спринта согласован и зафиксирован в README |
| 2026-07-25 | Задача 04 закрыта: promptfooconfig + explainer + target.mjs |
| 2026-07-25 | Задача 05 закрыта: config-review PASS, готов к redteam generate |
| 2026-07-25 | Задачи 06–07 закрыты: redteam.yaml (30), review ACCEPT |
| 2026-07-25 | Задача 08 закрыта: baseline-before eval-g7I, 10/20/0 |
| 2026-07-25 | Задача 09 закрыта: baseline-before-triage, 20 findings, 4 risk clusters |
| 2026-07-25 | Задача 10 закрыта: fix-decisions, FIX-01…04, SECURITY_ENABLED |
| 2026-07-25 | Задача 11 закрыта: security module, FIX-01…04, 149 tests pass |
| 2026-07-25 | Задача 12 закрыта: baseline-after eval-yYs, 19/11/0, ASR 37%, comparison |
| 2026-07-25 | Задача 13 закрыта: final-report.md; спринт Done |
