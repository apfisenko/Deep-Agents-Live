# Summary: Task 01 — Каркас проекта

> **План:** [plan.md](./plan.md)
> **Дата закрытия:** 2026-07-24

---

## Что реализовано

- `pyproject.toml` / `uv.lock` — пакет `homework-mentor`, deps: deepagents, rich, pyyaml, python-dotenv; groups lint/test
- `.python-version` — pin **Python 3.11**
- `make.ps1` — sync / run / lint / format / test
- `.env.example`, `.gitignore`
- `src/homework_mentor/__init__.py` — stub entrypoint
- `config/`, `logs/` — каталоги-заготовки
- `tests/test_import.py` — smoke импорта
- `README.md` — краткая точка входа

---

## Отклонения от плана

- Python: в плане был ≥3.12; по запросу и vision зафиксировано **≥3.11** (pin 3.11). Проверено: sync / lint / test на CPython 3.11.9.

---

## Принятые решения

| Решение | Причина | Ссылка на ADR |
|---------|---------|--------------|
| Имя пакета `homework_mentor` / project `homework-mentor` | PEP-совместимое имя без дефисов в import | — |
| `uv_build` + src-layout | modern-python skill | — |
| `make.ps1 run` → stub до Task 04 | YAGNI: CLI ещё нет | — |
| `requires-python = ">=3.11"` | vision + явный запрос; 3.12+ тоже ок | — |

---

## Проблемы и решения

| Проблема | Как решили |
|----------|-----------|
| ruff ALL: CPY001 | ignore `CPY` (copyright не требуется) |
| SystemExit(f-string) → TRY/EM | сообщение в переменную + stderr + exit 0 |

---

## Итог DoD

| # | Критерий | Результат |
|---|----------|-----------|
| 1 | Зависимости ставятся (`.\make.ps1 sync`) | ✅ |
| 2 | Lint проходит (`.\make.ps1 lint`) | ✅ |
| 3 | Smoke-тест зелёный (`.\make.ps1 test`) | ✅ |
| — | Python 3.11 поддерживается | ✅ `3.11.9`, lint+test зелёные |

---

## Что дальше

- Task 02: YAML-конфиг + логирование

---

## Ссылки

- [Sprint 00 README](../../README.md)
- Skills: `modern-python`, `uv-package-manager`
