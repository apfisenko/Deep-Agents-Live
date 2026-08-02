# Summary: 01-rubric-yaml

> **Sprint:** sprint-08-rubric-multi-agent  
> **Дата:** 2026-08-02  
> **Статус:** ✅ Done

## Что сделано

- Создана рубрика `src/skills/multi-agent/rubric.yaml` — 5 аспектов по 0.20, sum == 1.0
- Создан `src/skills/multi-agent/SKILL.md` — полные инструкции для reviewer-субагентов по каждому аспекту, формат вывода
- Реализован `src/course_companion/skills/resolver.py` — `resolve_rubric(topic)` с fuzzy-matching по `match_keywords`; путь вычисляется от `__file__`, не зависит от cwd
- Написаны 7 тестов в `tests/skills/test_resolve_rubric.py`

## Решения

- `SKILLS_DIR = Path(__file__).parent.parent.parent / "skills"` — три `.parent` от `src/course_companion/skills/` ведут в `src/`, затем `/ "skills"` → `src/skills/`
- Тест `test_not_found` проходит потому что рубрики `blockchain` нет → `FileNotFoundError` поднимается корректно

## Итог DoD

| # | Критерий | Результат |
|---|----------|-----------|
| 1 | Сумма весов == 1.0 | ✅ |
| 2 | Все 7 тестов зелёные | ✅ 7 passed |
| 3 | `resolve_rubric` не зависит от cwd | ✅ |
| 4 | `make ci`: lint + typecheck + 43 tests | ✅ |
