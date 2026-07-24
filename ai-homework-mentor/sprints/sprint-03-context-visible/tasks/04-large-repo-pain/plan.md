# Task 04: Большой репо + фиксация боли S3

> **Sprint:** [../../README.md](../../README.md)
> **Тип:** feat + docs
> **Spec:** без spec

---

## Цель

Живой прогон на большом объёме + `docs/pain-s3.md` с числами — вход для контраста S4.

---

## Решение по источнику кода (согласовано)

| Роль | Вариант | Реализация |
|------|---------|------------|
| CI / pytest CE | **B** | `tests/fixtures/large_hw/` — синтетический толстый fixture, генератор при необходимости |
| Demo + `pain-s3.md` | **A** | Публичный mid-size Python repo в `config/fixtures.yaml`, pin commit |

**C** не используется как канон — только опциональный `-Path` (уже есть в CLI).

---

## Состав работ

- [ ] Генератор / fixture `tests/fixtures/large_hw/`
- [ ] `config/fixtures.yaml` — `large_demo.github_url` + pinned ref
- [ ] Прогон single-agent с production-подобными порогами CE
- [ ] `docs/pain-s3.md` — метрики, цитата verbose, тезис «нужна изоляция»
- [ ] Заготовка `docs/contrast-s3-s4.md`
- [ ] Самопроверка DoD спринта

---

## Критерии готовности (DoD)

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | `docs/pain-s3.md` с числами/событиями | file check |
| 2 | `large_hw` используется в CI-тестах CE | pytest |
| 3 | Lint + test | `.\make.ps1 lint`; `.\make.ps1 test` |

---

## Scope

**Трогаем:** fixtures, config/fixtures.yaml, docs, tests task 04.

**НЕ трогаем:** субагенты (S4).
