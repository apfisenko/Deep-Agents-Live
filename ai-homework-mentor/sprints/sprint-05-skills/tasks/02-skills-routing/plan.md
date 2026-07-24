# Task 02: Роутинг skills в runtime

> **Sprint:** [../../README.md](../../README.md)
> **Тип:** feat
> **Spec:** без spec

---

## Цель

Оркестратор и reviewer-субагенты получают детерминированный список skills для сессии; skill читается с диска (allowlist) и попадает в brief, без дублирования всего YAML в system prompt.

---

## Состав работ

- [ ] `SkillRef` + `resolve(topic, aspect, code_manifest) → list[SkillRef]`
- [ ] Loader: читать SKILL.md только из allowlist (`skills/`, `.agents/skills/`)
- [ ] `ReviewBrief.skills[]` (id, path, reason)
- [ ] Лог активации skill (id + reason, без PD)
- [ ] Тесты: API → fastapi; python → modern-python; без API → fastapi нет; traversal → error
- [ ] Самопроверка по DoD

---

## Критерии готовности (DoD)

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | Router детерминирован на фикстурах | pytest |
| 2 | Path вне allowlist → ошибка | pytest |
| 3 | Lint + tests | `.\make.ps1 lint`; `.\make.ps1 test` |

---

## Артефакты

- `src/homework_mentor/skills/router.py`, `loader.py`, `models.py`
- обновлённый `ReviewBrief`
- `tests/test_skills_router.py`

---

## Scope

**Трогаем:** skills package, handoff schema, brief building, tests.

**НЕ трогаем:** установку публичных skills (task 03), Rich panel (task 04).

---

## Решения

- Эвристика API: topic содержит fastapi/api **или** в code_manifest есть `**/routes/**`, `**/api/**`, `*fastapi*`
- `modern-python` → aspect `code_quality`
- `fastapi-templates` → aspect `architecture` (или api), только при API-эвристике
