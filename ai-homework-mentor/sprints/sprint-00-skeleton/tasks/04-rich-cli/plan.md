# Task 04: Rich CLI + склейка E2E

> **Sprint:** [../../README.md](../../README.md)
> **Тип:** feat
> **Spec:** без spec

---

## Цель

Rich CLI принимает `-Message` / `-Path` / `-Verbose`, вызывает `run_agent`, показывает ответ; зафиксированы gaps S0.

---

## Состав работ

- [x] CLI argparse: `-Message`, `-Path`, `-Verbose`
- [x] Path: только UI/лог (+ как текст в агент, если нет Message); чтение кода — S1
- [x] Compact / Verbose (config panel без CE/субагентов)
- [x] `main` → CLI → `run_agent`
- [x] `docs/gaps-s0.md`
- [x] Тесты CLI с моком агента
- [x] Самопроверка DoD
- [x] (после «ок») summary + sprint README / roadmap S0

---

## Критерии готовности (DoD)

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | `run -Message` exit 0 (с ключом) или CLI unit-тест | `.\make.ps1 test` + ручной run при наличии `.env` |
| 2 | `-Path` принимает существующий путь | unit + `.\make.ps1 run -- -Path .` при ключе |
| 3 | Lint + tests | `.\make.ps1 lint`; `.\make.ps1 test` |
| 4 | `docs/gaps-s0.md` существует | файл на месте |

---

## Артефакты

- `src/homework_mentor/cli/`
- `docs/gaps-s0.md`
- обновление `homework_mentor.main`

---

## Scope

**Трогаем:** CLI, main, gaps doc, тесты CLI.

**НЕ трогаем:** парсинг темы, clone, workspace, субагенты.

---

## Риски

- Реальный OpenRouter для ручного DoD нужен `.env`; CI покрыт моком.
