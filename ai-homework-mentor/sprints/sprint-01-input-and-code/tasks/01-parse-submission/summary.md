# Summary: Task 01 — Модель Submission + парсинг входа

> **План:** [plan.md](./plan.md)
> **Дата закрытия:** 2026-07-24

---

## Что реализовано

- `src/homework_mentor/submission/models.py` — `SourceType`, `Submission`, `TopicExtraction` (SGR)
- `src/homework_mentor/submission/parser.py` — эвристики URL/path/topic + LLM topic extract
- `config/prompts/parse_submission.yaml` + загрузка в `YamlConfig`
- `tests/test_parse_submission.py`

---

## Отклонения от плана

- нет

---

## Принятые решения

| Решение | Причина | Ссылка на ADR |
|---------|---------|--------------|
| Эвристики до LLM | дёшево и тестируемо; LLM только для темы без «Тема:» | — |
| `topic_extractor` injectable | CI без сети | — |
| Не выдумывать тему | политика sprint README | — |

---

## Проблемы и решения

| Проблема | Как решили |
|----------|-----------|
| ruff RUF001 на кириллице в clarification | per-file ignore |

---

## Итог DoD

| # | Критерий | Результат |
|---|----------|-----------|
| 1 | GitHub URL | ✅ |
| 2 | Без темы → clarification | ✅ |
| 3 | Промпт в YAML | ✅ |
| 4 | Lint + tests | ✅ |

---

## Что дальше

- Task 02: локальная директория → `workspace/code/`

---

## Ссылки

- [Sprint 01 README](../../README.md)
- Skill: `schema-guided-reasoning`
