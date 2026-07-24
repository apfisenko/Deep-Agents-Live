# Task 03: Публичные skills с skills.sh

> **Sprint:** [../../README.md](../../README.md)
> **Тип:** feat
> **Spec:** без spec

---

## Цель

Установлены и верифицированы `modern-python` и `fastapi-templates` в `ai-homework-mentor/.agents/skills/`; перед использованием прочитан SKILL.md; зафиксирован inventory.

---

## Состав работ

- [ ] Скопировать/установить `modern-python` в `.agents/skills/` проекта
- [ ] Найти и установить `fastapi-templates` из доверенного источника (skills.sh / курс)
- [ ] Прочитать оба SKILL.md; сверить назначение с аспектами review
- [ ] `docs/skills-inventory-s5.md`
- [ ] Минимальная фикстура `tests/fixtures/fastapi_hw`
- [ ] Smoke: router резолвит skills на local_hw / fastapi_hw
- [ ] Самопроверка по DoD

---

## Критерии готовности (DoD)

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | SKILL.md существуют по путям inventory | file check |
| 2 | Router резолвит установленные skills | pytest |
| 3 | Lint + tests | `.\make.ps1 lint`; `.\make.ps1 test` |

---

## Артефакты

- `ai-homework-mentor/.agents/skills/modern-python/`
- `ai-homework-mentor/.agents/skills/fastapi-templates/`
- `docs/skills-inventory-s5.md`
- `tests/fixtures/fastapi_hw/`

---

## Scope

**Трогаем:** `.agents/skills/`, docs inventory, fastapi fixture, router smoke.

**НЕ трогаем:** Cursor rule routers и Rich panel (task 04); S6 synthesis.

---

## Решения

- Только 2 публичных skill — без «на будущее»
- В skill-контекст не передаём `.env`, ключи, полные PD
