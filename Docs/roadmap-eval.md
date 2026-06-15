# Roadmap — Eval-трек: Deep-Agents-Live (llmstart agent)

> **Методология:** [.methodology/eval/eval-methodology.md](../.methodology/eval/eval-methodology.md)
> **Продуктовый roadmap:** [roadmap.md](roadmap.md)
> **Последнее обновление:** 2026-06-15

---

## Цель трека

Измеримое качество агента: для любого изменения системы (промпт, модель, реализация, retrieval) — ответ «стало лучше или хуже и где» по главной метрике (E-18) на версионированных датасетах.

---

## Предусловия трека (Слой 0 методологии)

| Пункт | Статус | Комментарий |
|---|---|---|
| Агент работает e2e, доступен по API | ✅ | MVP v0.1 закрыт (sprint-04): `POST /api/v1/chat`, `/api/v1/chat/stream`, web + Telegram |
| Трейсинг + спаны инструментов в Langfuse | ✅ | `CallbackHandler` в `react_agent.py`; SDK `langfuse>=4.7.1` в `backend/uv.lock`; self-hosted `:3001` |
| Реестр конфигураций (`config_id`, E-6) | ✅ | Task 01 sprint-eval-01: `config_id` в API + `evals/configs/` |
| ≥ 10 кейсов с известным ответом | ✅ | `dataset/v0.1.jsonl` — 27 items; 5 чатов в `dataset/analysis/chats/`; KB — `data/b2c/`, `data/b2b/` |
| Главная метрика определена (E-18) | ✅ | `avg_answer_correctness` на `e2e/e2e-qa` — [metrics-map.md](eval/metrics-map.md) |
| ≥ 2 конфигурации для сравнения | 🚧 | Candidate-конфиги есть; compare + env-infra — sprint-eval-03 |

**Исходные данные для eval (зафиксировано при онбординге):**

| Источник | Путь (факт) | Назначение |
|----------|-------------|------------|
| Реальные диалоги | `dataset/source/CHAT_*.json`, разборы `dataset/analysis/chats/CHAT_*.md` | Эталоны, сценарии, стратификация |
| Отчёт анализа | `dataset/analysis-report.md` | Таксономия G1–G5, частоты, анти-паттерны |
| База знаний | `data/` (`.rag-manifest.json`, `b2c/programs/`, `b2b/`) | Ground truth для RAG-ответов |
| Черновой датасет v0.1 | `dataset/v0.1.jsonl` (27 items, типы A/B/C) | Референс формата; миграция в `evals/datasets/` — задача 04 |

**Не готово к eval (ожидаемо):** каталог `evals/` отсутствует; `docs/eval/dataset-map.md` и `metrics-map.md` — в задачах 02–03.

---

## Легенда

📋 Planned · 🚧 In Progress · ✅ Done · ⏸ Paused · 🗄 Archived

> **⚠️ KR — это обещания спринтов, а не todo создания roadmap.** При генерации этого документа никакие рабочие артефакты (dataset-map, metrics-map, конфиги, манифесты) НЕ создаются — они появляются только внутри задач спринтов после апрува плана (правило агента №8 методологии).

---

## v0.1 — Eval MVP: вертикальный срез ✅

**Цель:** полный путь «манифест → review → sync → baseline-прогон → отчёт» работает на одном датасете.

**Ключевые результаты:**
- [x] Реестр конфигов: `config_id` реально меняет поведение агента (E-6) — task 01
- [x] Каркас `evals/` + команды операций работают (E-2) — task 01
- [x] `dataset-map.md` и `metrics-map.md` утверждены — tasks 02–03
- [x] Датасет `e2e-qa`: ≥ 20 items, 100% `reviewed_by`, `gt_quality` проставлен (E-13/E-14) — task 04
- [x] Baseline-ран с полным `run_metadata` (E-9); evidence в summary — task 05 (`...191628Z`)
- [x] Отчёт анализа в `evals/reports/` — task 06

**Спринты:**
| # | Sprint | Цель | Статус | Документ |
|---|--------|------|--------|---------|
| eval-01 | vertical-slice | baseline-оценка на e2e-qa одной командой | ✅ | [sprint-eval-01](sprints/eval/sprint-eval-01-vertical-slice/README.md) |
| eval-02 | datasets-coverage | остальные датасеты по dataset-map с их метриками | ✅ | [sprint-eval-02](sprints/eval/sprint-eval-02-datasets-coverage/README.md) |

---

## v0.2 — Сравнимость и цикл улучшения ✅

**Цель:** сравнение конфигураций и работающий eval-fix loop.

**Спринт:** [sprint-eval-03-comparability-cycle](sprints/eval/sprint-eval-03-comparability-cycle/README.md)

**Ключевые результаты:**
- [x] Env-driven модели/judge/embedding/dataset prefix (не хардкод)
- [x] Makefile: build → sync → experiment → analyze → compare
- [x] `check-traces`: web + telegram в Langfuse
- [ ] `compare` с защитой версии датасета (E-16) — infra ✅, нужен прогон
- [ ] ≥ 1 candidate-конфиг прогнан и сравнён с baseline (отличие — один параметр, E-7)
- [ ] ≥ 2 итерации eval-fix loop с зафиксированной дельтой (E-22)
- [x] `funnel-to-lead` через user simulation (E-23) — sprint-eval-03 task 03
- [x] Первый error analysis с таксономией провалов; категории превращены в items датасетов (К-3/К-4) — sprint-eval-03 task 04

---

## v1.0 — Институционализация 📋

**Цель:** eval как постоянная практика, а не разовая акция.

**Ключевые результаты:**
- [ ] Skill проекта (правила агента + шаблоны методологии)
- [ ] CI regression-gate по главной метрике
- [ ] Annotation queues для разметки (corrected outputs → эталоны; human baseline для судьи)
- [ ] Разметка approximate → verified расширена (E-14)
- [ ] (опц.) Онлайн-evaluators на прод-трафике

---

## История изменений

| Дата | Изменение |
|------|-----------|
| 2026-06-15 | Sprint eval-02 закрыт: 6 датасетов v001 + multi-dataset runner + RAG evaluators |
| 2026-06-15 | Sprint eval-02 открыт: datasets-coverage (6 датасетов + multi-dataset runner) |
| 2026-06-15 | Task 05 закрыта: runner + evaluators + baseline run `191628Z` |
| 2026-06-15 | Sprint eval-01 закрыт: vertical slice validate→analyze на e2e-qa/v001 |
| 2026-06-15 | Task 06 закрыта: analyze_run + отчёт analysis-191628Z |
| 2026-06-16 | Sprint eval-03 открыт: env-driven eval, Makefile cycle, check-traces |
