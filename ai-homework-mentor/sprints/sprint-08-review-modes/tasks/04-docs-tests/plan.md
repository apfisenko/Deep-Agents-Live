# Task 04: Docs + метрики субагентов + закрытие S8

> **Sprint:** [../../README.md](../../README.md)
> **Тип:** feat + docs
> **Ветка:** `feat/s8-04-docs-subagent-metrics`
> **Spec:** без spec

---

## Цель

В run-отчёте `subagents` видно затраты токенов **по каждому reviewer**; quickstart и comparison-variants описывают `-Mode` / compare; DoD спринта S8 закрыт.

---

## Состав работ

### A. Метрики окон субагентов (из фидбэка по run-отчётам)

- [x] Инструментировать каждое окно reviewer: estimate и/или `usage_metadata` (max tokens окна, опц. total за вызовы)
- [x] Пробросить метрики в `RunReport` / handoff events (`aspect`, `max_tokens`, `total_tokens_estimate`, `wall_ms`)
- [x] В `docs/run-report-*.md` (RU): секция **«Токены субагентов»** — таблица по аспектам
- [x] В итоговых метриках: `total_tokens_estimate` = max parent + сумма оценок окон reviewers (не длина summary)
- [x] Пояснение в отчёте: шаги CE = только parent; окна reviewers — отдельно
- [x] Тесты: mock handoff/metrics → секция и суммы в markdown
- [x] (опц.) строка в compare-отчёте: sum reviewer tokens single=0 vs subagents=N

### B. Документация и закрытие спринта

- [x] `docs/quickstart-windows.md` — `-Mode`, `compare-modes`, что смотреть в run-отчёте
- [x] `docs/comparison-variants.md` — воспроизведение флагом; актуализация V5/S8; пояснение parent steps vs reviewer windows
- [x] Добить lint / tests; обновить статусы задач в sprint README после «ок»
- [x] Самопроверка по DoD спринта

---

## Критерии готовности (DoD)

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | В run-отчёте `subagents` есть таблица токенов по каждому reviewer (aspect) | инспекция / тест |
| 2 | Пояснено: шаги = parent; окна субагентов отдельно | текст в отчёте / docs |
| 3 | Quickstart содержит `-Mode` и `compare-modes` | чтение docs |
| 4 | comparison-variants ссылается на S8 и актуальные S9/S10 | чтение docs |
| 5 | `.\make.ps1 ci` зелёный | CI локально |

---

## Артефакты

- `src/homework_mentor/reviewers/` (метрики окна / collector)
- `src/homework_mentor/reports/` (модели + writer секции)
- `docs/run-report-*.md` (генерируемые)
- `docs/quickstart-windows.md`, `docs/comparison-variants.md`
- `tests/test_run_report.py` (и связанные)
- sprint README / summary Task 04

---

## Scope

**Трогаем:** инструментирование reviewer windows, run/compare report writer, docs, тесты.

**НЕ трогаем:** checkpoint (S9), dynamic models (S10), смена rubric/аспектов.

---

## Риски и допущения

- DeepAgents может не отдавать полный stream субагента наружу — тогда max/estimate по доступным сообщениям handoff + отдельный observer при создании subagent; зафиксировать в summary, если только proxy.
- «Total tokens» по-прежнему оценка, пока нет полного invoice OpenRouter по всем окнам.
