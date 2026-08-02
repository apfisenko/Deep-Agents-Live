# Plan: 01-rubric-yaml

> **Sprint:** sprint-08-rubric-multi-agent  
> **Статус:** ✅ Done  
> **Дата:** 2026-08-02

## Цель

Создать рубрику `multi-agent` как подключаемую Skills-экспертизу: `rubric.yaml` + `SKILL.md` + `resolve_rubric()` + unit-тесты.

## Состав работ

- `src/skills/multi-agent/rubric.yaml` — 5 аспектов × 0.20, match_keywords
- `src/skills/multi-agent/SKILL.md` — системный промпт reviewer-субагентов
- `src/course_companion/skills/__init__.py` — экспорт
- `src/course_companion/skills/resolver.py` — `resolve_rubric(topic)` с fuzzy-matching
- `tests/skills/__init__.py`
- `tests/skills/test_resolve_rubric.py` — 7 тестов

## DoD

| # | Критерий | Статус |
|---|----------|--------|
| 1 | Сумма весов == 1.0 | ✅ |
| 2 | Все 7 тестов зелёные | ✅ |
| 3 | `resolve_rubric` не зависит от cwd | ✅ |
| 4 | `make ci` зелёный | ✅ |

## Артефакты

- `course-companion/src/skills/multi-agent/rubric.yaml`
- `course-companion/src/skills/multi-agent/SKILL.md`
- `course-companion/src/course_companion/skills/__init__.py`
- `course-companion/src/course_companion/skills/resolver.py`
- `course-companion/tests/skills/__init__.py`
- `course-companion/tests/skills/test_resolve_rubric.py`
