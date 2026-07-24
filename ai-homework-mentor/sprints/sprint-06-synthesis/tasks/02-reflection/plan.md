# Task 02: Reflection — покрытие и противоречия

> **Sprint:** [../../README.md](../../README.md)
> **Тип:** feat
> **Spec:** без spec

---

## Цель

Перед финальной сборкой: проверить покрытие аспектов и явно зафиксировать противоречия между review-нотами (`ReflectionResult`).

---

## Состав работ

- [x] Промпт `config/prompts/synthesis_reflection.yaml`
- [x] `ReflectionResult` + `run_reflection` (только артефакты: notes/summaries/rubric/todo)
- [x] Coverage — детерминированно (expected vs covered → gaps)
- [x] Contradictions — LLM structured output; injectable detector для тестов; не усреднять молча
- [x] Фикстура конфликтующих notes + pytest (gap + contradiction)
- [x] Самопроверка по DoD

---

## Критерии готовности (DoD)

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | Gap в coverage на фикстуре | pytest |
| 2 | Contradiction в ReflectionResult | pytest (fixture + injected detector) |
| 3 | Reflection не читает `/code/` | code review + unit assert на входах |
| 4 | Lint + tests | `.\make.ps1 lint`; `.\make.ps1 test` |

---

## Артефакты

- `config/prompts/synthesis_reflection.yaml`
- `src/homework_mentor/synthesis/__init__.py`
- `src/homework_mentor/synthesis/reflection.py`
- `tests/fixtures/synthesis_conflict/notes/*`
- `tests/test_reflection.py`
- конфиг: загрузка reflection prompts

---

## Scope

**Трогаем:** synthesis package, reflection prompt, config load, fixtures, tests.

**НЕ трогаем:** final synthesis pipeline (T03), CLI panels (T04), удаление SimpleFeedback.

---

## Решения

- Coverage считается в Python; LLM только для contradictions (SGR)
- Политика противоречий: явная секция + resolution hint, без silent merge
