# Sprint 13: drill-a2ui (S4 · Т12)

> **Версия roadmap:** v1.0-scaling
> **Roadmap:** [../../roadmap.md](../../roadmap.md)
> **Статус:** ✅ Done
> **Предшественник:** [Sprint 12](../sprint-12-service-split-a2a/README.md)
> **Следующий:** [Sprint 14](../sprint-14-docker-compose/README.md) (опц.)

**Окружение:** Python **3.11** · Windows: `make.ps1` · Docker — Sprint 14 через WSL

---

## Цель спринта

Четвёртый режим **drill**: «хочу потренироваться» → A2UI-форма с кейсом масштабирования → разбор по аргументации; фидбек проверки может прийти **посреди drill**.

---

## Боль, которую закрывает

| Боль T11 | После спринта |
|----------|---------------|
| Плоский текст в терминале | Динамическая A2UI v0.9 форма |
| Нечем тренировать протоколы | Скилл `scaling-case-drill` |

---

## Тезис темы масштабирования

**A2UI — протокол на шве «агент ↔ динамический UI».** UI как проекция стейта: `show_drill_case` → `drill_case` в values → фронт монтирует форму.

### Три HTTP-канала

| # | Канал | Куда | Когда |
|---|-------|------|-------|
| 1 | Чат | companion `:2024` | всегда |
| 2 | A2UI | `POST /drill/a2ui` на `:2024` | drill |
| 3 | Поллер | checker `:2025` | фоновая проверка |

---

## DoD спринта

| # | Критерий | Агент | Человек |
|---|----------|-------|---------|
| 1 | Router → drill | test intent | «Хочу потренироваться» |
| 2 | `show_drill_case` → `drill_case` | unit test | values в UI |
| 3 | POST /drill/a2ui SSE | test_routes | Форма ~30–40 с |
| 4 | userAction → разбор | delivery test | Зачёт / разбор по осям |
| 5 | Фидбек mid-drill | walkthrough | кадр 04-feedback-mid-drill |
| 6 | check/list в drill | matrix test | Поллер в drill |
| 7 | CLI без drill | companion CLI | Drill только web |
| 8 | CI зелёный | make ci | — |

---

## Задачи

| # | Задача | Статус | Plan | Summary |
|---|--------|--------|------|---------|
| 01 | scaling-case-drill-skill | ✅ | — | [summary](./summary.md) |
| 02 | drill-mode-handoffs | ✅ | — | [summary](./summary.md) |
| 03 | drill-a2ui-module | ✅ | — | [summary](./summary.md) |
| 04 | webapp-drill-endpoint | ✅ | — | [summary](./summary.md) |
| 05 | frontend-drill-panel | ✅ | — | [summary](./summary.md) |
| 06 | integration-walkthrough | ✅ | — | [summary](./summary.md) |

---

## Задача 01: scaling-case-drill-skill

- [x] `data/skills/scaling-case-drill/SKILL.md`
- [x] `references/seams-toolbox.md`, `decision-framework.md`, `evaluation.md`
- [x] Progressive disclosure через `read_file`

---

## Задача 02: drill-mode-handoffs

- [x] `RouteDecision` + `"drill"`
- [x] `SERVICE_PREFIXES = ("[авто]", "[drill]")` — router stay
- [x] `drill_case` в `CourseCompanionState`
- [x] `MODE_PROMPTS["drill"]`, blacklist тулов
- [x] `show_drill_case` tool
- [x] check/list во всех режимах включая drill

---

## Задача 03: drill-a2ui-module

Структура `src/course_companion/drill/`:

| Файл | Роль |
|------|------|
| `case.py` | DrillCase schema |
| `generator.py` | LLM + A2uiStreamParser, retry |
| `routes.py` | POST /drill/a2ui |
| `delivery.py` | CompanionDelivery via langgraph_sdk |

- [x] Pins: `a2ui-agent-sdk==0.4.0`, fastapi, langgraph-sdk
- [x] Devstand `:8123` — **опционально** (изолированный прогон модуля)
- [x] `tests/drill/`

---

## Задача 04: webapp-drill-endpoint

- [x] `webapp.py` — mount `build_drill_router(...)`
- [x] `langgraph.companion.json` → `"http": {"app": "..."}`
- [x] Не shadow `/threads`, `/runs`

---

## Задача 05: frontend-drill-panel

- [x] `npm install --legacy-peer-deps`
- [x] `@a2ui/react/v0_9`, `@a2ui/web_core/v0_9`
- [x] `DrillPanel.tsx`, `a2ui.ts`
- [x] `App.tsx`: watch `drill_case`, `drillReviewArrived()`
- [x] vite: `/api/drill` → companion `:2024`

---

## Задача 06: integration-walkthrough

Сценарий split + async + drill + mid-drill feedback:

1. Сдать ДЗ → карточка
2. «Хочу потренироваться» → форма
3. Поллер → фидбек mid-drill
4. Submit → разбор

- [x] `examples/walkthrough/session-log.txt`
- [x] ADR `009-a2ui-drill-channel.md`
- [x] `src/course_companion/drill/README.md`

---

## Что студент видит

A2UI-панель с осями выбора протоколов; разбор по аргументации; фидбек проверки может прийти посреди заполнения формы.

---

## Грабли A2UI (§6.1 PRACTICE)

| # | Грабля | Mitigation |
|---|--------|------------|
| 1 | npm без `--legacy-peer-deps` | README |
| 2 | default import = v0_8 | только `/v0_9` |
| 3 | catalogId helper | литерал v0.9 URL |
| 4 | version "v0.9.1" | всегда "v0.9" |
| 5 | `[авто]`/`[drill]` меняют mode | SERVICE_PREFIXES |

---

## Итог (заполняется после закрытия)

Четвёртый режим **drill** + A2UI-канал на `:2024`. Три HTTP-канала (чат / drill / поллер) работают в одной сессии; mid-drill feedback проверен live. **86 tests** · **ADR 009**.

**Summary:** [summary.md](./summary.md)
