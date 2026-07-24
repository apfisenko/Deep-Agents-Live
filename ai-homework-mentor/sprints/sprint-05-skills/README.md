# Sprint 05: Skills — свои rubric + публичные навыки

> **Версия roadmap:** v0.2 (спринты S0–S10)
> **Roadmap:** [../../roadmap.md](../../roadmap.md)
> **Статус:** ✅ Done
> **Открыт:** 2026-07-24
> **Закрыт:** 2026-07-24
> **Зависит от:** [Sprint 04](../sprint-04-subagents/README.md) (reviewer-субагенты + handoff)

---

## Цель спринта

Критерии и процедуры проверки оформлены как навыки: свои rubric-skills по темам + уместные публичные skills из [skills.sh](https://www.skills.sh/); reviewer-субагенты подгружают SKILL.md по маршрутизации; verbose показывает активированные skills; правила использования скиллов актуализированы в роутерах проекта.

---

## Контекст слоя

| | |
|--|--|
| **Боль, которую закрываем** | Критерии и «как проверять» размазаны по промптам — плохо переиспользуются и не видны в verbose |
| **Механизм deep-agent** | **Skills** — свои rubric-skills + публичные процедуры (`modern-python`, `fastapi-templates`, …) |
| **Боль, которую оставляем** | Нет reflection-синтеза и полноценных `final_feedback` / `fix_plan` (S6) |
| **Политика безопасности** | Только доверенный источник; **прочитать SKILL.md** до применения; skills в **субагенте** без секретов; **код студента не исполняется** |

### Границы

| В S5 | Не в S5 |
|------|---------|
| Rubric → project skills в `skills/` | Полный синтез и fix_plan (S6) |
| Маршрутизация skills по теме + аспекту reviewer | Dynamic model routing (S10) |
| Установка 1–2 публичных skills с skills.sh | Установка «всех подряд» с маркетплейса |
| Актуализация двух `40-skills-router.mdc` | Dogfooding (S7) |

---

## DoD спринта

Sprint считается завершённым, когда:

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | Rubric оформлены как навыки проекта (`skills/rubric-*`) | Файлы SKILL.md + mapping topic → skill |
| 2 | Публичные skills установлены из доверенного источника и **прочитаны** (описание совпадает с назначением) | `.agents/skills/` + запись в plan/summary |
| 3 | Reviewer-субагент получает skill в brief; процедура из SKILL.md, не дублируется в промпте целиком | Verbose: skill id + path; код review |
| 4 | `modern-python` — на аспекте качества кода; `fastapi-templates` — только если в работе есть API (эвристика по topic/файлам) | Два сценария прогона (с API / без) |
| 5 | Verbose: блок «Rubric & Skills» — активные rubric-skill + ecosystem skills | `-Verbose` прогон |
| 6 | Актуализированы роутеры: `ai-homework-mentor/.cursor/rules/40-skills-router.mdc` и `.cursor/rules/methodology/40-skills-router.mdc` | diff + таблица «тип проверки → skill» |
| 7 | Lint + tests | `.\make.ps1 lint`; `.\make.ps1 test` |

---

## Навыки (skills) для исполнителя

| Skill | Зачем в S5 |
|-------|------------|
| `deep-agents-core` / `deep-agents-orchestration` | Подключение skills к субагентам |
| `ecosystem-primer` | Обзор экосистемы skills |
| `find-skills` (если есть) | Поиск/установка с skills.sh |
| `create-skill` (`.cursor/skills-cursor/create-skill`) | Формат собственных rubric-skills |
| `modern-python`, `fastapi-templates` | **Прочитать SKILL.md** перед интеграцией в review |

Роутеры (обновить в этом спринте): [`.cursor/rules/methodology/40-skills-router.mdc`](../../../.cursor/rules/methodology/40-skills-router.mdc) + проектный `ai-homework-mentor/.cursor/rules/40-skills-router.mdc` (создать).

---

## Маршрутизация (целевая модель)

```text
Assignment Topic
    → rubric-skill (skills/rubric-<topic>/SKILL.md)
    → aspect (architecture | code_quality | api | …)
        → ecosystem skill (optional)
            ├── modern-python        → reviewer_code_quality
            ├── fastapi-templates    → reviewer_api OR if **/routes/**, **/api/** detected
            └── (future) deep-agents-* → agent-themed homework
```

**Правило:** skill подключается только если SKILL.md прочитан исполнителем/агентом и назначение совпадает с аспектом. Не тащить skill «на всякий случай».

---

## Задачи

| # | Задача | Статус | Plan | Summary |
|---|--------|--------|------|---------|
| 01 | Свои rubric-skills | ✅ | [plan](tasks/01-rubric-skills/plan.md) | [summary](tasks/01-rubric-skills/summary.md) |
| 02 | Роутинг skills по теме и аспекту | ✅ | [plan](tasks/02-skills-routing/plan.md) | [summary](tasks/02-skills-routing/summary.md) |
| 03 | Публичные skills с skills.sh | ✅ | [plan](tasks/03-public-skills/plan.md) | [summary](tasks/03-public-skills/summary.md) |
| 04 | Роутеры + verbose «Rubric & Skills» | ✅ | [plan](tasks/04-routers-verbose/plan.md) | [summary](tasks/04-routers-verbose/summary.md) |

---

## Задача 01: Свои rubric-skills ✅

### Цель

Критерии из `config/rubric/` (S2) переоформлены в переиспользуемые навыки проекта в `skills/rubric-*`.

> 💡 **Скиллы:** `create-skill`, `schema-guided-reasoning`.

### Состав работ

- [ ] Минимум 2 rubric-skill: `skills/rubric-default/`, `skills/rubric-python-cli/` (или темы курса)
- [ ] Каждый SKILL.md: frontmatter, «что проверяем», чеклист по criterion id, ссылки на обязательное/опциональное
- [ ] Mapping topic → rubric-skill id в `config/skills_routing.yaml` (или секция в agent.yaml)
- [ ] При старте сессии: копия/ссылка активного rubric-skill в workspace (как в S2, но источник — skill)
- [ ] Тесты mapping topic → skill path
- [ ] Самопроверка по DoD задачи

### Критерии готовности (DoD)

**Агент проверяет:**

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | SKILL.md валидны по структуре | lint/review checklist |
| 2 | Известная тема → ожидаемый rubric-skill | pytest |

**Пользователь проверяет:**

- Текст skill читается как инструкция ментору, не как промпт «ответь студенту»

### Артефакты

- `skills/rubric-*/SKILL.md`
- `config/skills_routing.yaml`

### Документы

- 📋 [План задачи](tasks/01-rubric-skills/plan.md)
- 📝 [Summary](tasks/01-rubric-skills/summary.md)

---

## Задача 02: Роутинг skills в runtime ✅

### Цель

Оркестратор и reviewer-субагенты получают список skills для сессии; skill читается с диска и передаётся в изолированное окно (сжато или по секциям), не дублируя весь YAML rubric в system prompt.

> 💡 **Скиллы:** `deep-agents-orchestration`, `deep-agents-core`.

### Состав работ

- [ ] Модуль `skills/router.py`: resolve(topic, aspect, code_manifest) → `[SkillRef(id, path, reason)]`
- [ ] Tool или loader: read skill file (только allowlist путей: `skills/`, `.agents/skills/`)
- [ ] Brief субагента расширяется полем `skills[]` (id + excerpt или path)
- [ ] Лог: какой skill активирован и почему (без содержимого PD)
- [ ] Тесты: API-тема → fastapi-templates; generic python → modern-python; без API → fastapi не подключается
- [ ] Самопроверка по DoD задачи

### Критерии готовности (DoD)

**Агент проверяет:**

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | Router возвращает детерминированный набор на фикстурах | pytest |
| 2 | Path traversal вне allowlist → ошибка | pytest |

**Пользователь проверяет:**

- На двух разных topic/fixture набора skills различается осмысленно

### Артефакты

- `src/.../skills/router.py`, loader
- обновлённый `ReviewBrief` (skills[])

### Документы

- 📋 [План задачи](tasks/02-skills-routing/plan.md)
- 📝 [Summary](tasks/02-skills-routing/summary.md)

---

## Задача 03: Публичные skills с skills.sh ✅

### Цель

Установлены и верифицированы публичные skills для проверки кода; перед использованием прочитан SKILL.md; интеграция только через роутер S5.

> 💡 **Скиллы:** `find-skills`; затем **прочитать** `modern-python`, `fastapi-templates`.

### Состав работ

- [ ] Проанализировать [skills.sh](https://www.skills.sh/) — выбрать `modern-python`, `fastapi-templates` (или эквиваленты с совпадающим назначением)
- [ ] Установить в `.agents/skills/` **только** из доверенного источника (официальный registry / курс)
- [ ] Чеклист верификации: имя skill = описание в SKILL.md = аспект review
- [ ] Зафиксировать в `docs/skills-inventory-s5.md`: id, path, назначение, какой reviewer
- [ ] Запрет: не передавать в skill-контекст `.env`, ключи, полные тексты PD
- [ ] Smoke: reviewer с `modern-python` на fixture local_hw
- [ ] Самопроверка по DoD задачи

### Критерии готовности (DoD)

**Агент проверяет:**

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | SKILL.md существуют по путям из inventory | file check |
| 2 | Router из задачи 02 резолвит установленные skills | pytest |

**Пользователь проверяет:**

- Описание в inventory совпадает с прочитанным SKILL.md
- Нет лишних skills «на будущее»

### Артефакты

- `.agents/skills/modern-python/`, `.agents/skills/fastapi-templates/` (или согласованные имена)
- `docs/skills-inventory-s5.md`

### Документы

- 📋 [План задачи](tasks/03-public-skills/plan.md)
- 📝 [Summary](tasks/03-public-skills/summary.md)

---

## Задача 04: Роутеры + verbose «Rubric & Skills» ✅

### Цель

Правила использования skills зафиксированы для людей и агентов; verbose показывает активированные rubric + ecosystem skills.

> 💡 **Скиллы:** `create-rule` (формат `.mdc`).

### Состав работ

- [ ] Создать `ai-homework-mentor/.cursor/rules/40-skills-router.mdc` — таблица **проверка ДЗ → skill** (rubric + ecosystem + deep-agents-* при необходимости)
- [ ] Дополнить `.cursor/rules/methodology/40-skills-router.mdc` секцией **AI Homework Mentor** (или ссылкой на проектный роутер)
- [ ] Шаг в workflow: «перед review — прочитать SKILL.md из таблицы»
- [ ] Rich verbose: панель Rubric & Skills (id, path, reason, aspect)
- [ ] Compact: одна строка «skills: …»
- [ ] Самопроверка по DoD спринта

### Критерии готовности (DoD)

**Агент проверяет:**

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | Оба роутера существуют и согласованы | file check |
| 2 | Verbose рендер skills | unit на фикстуре SkillRef[] |
| 3 | Lint + test | `.\make.ps1 lint`; `.\make.ps1 test` |

**Пользователь проверяет:**

- По роутеру понятно, какой skill на каком аспекте
- Verbose на прогоне показывает ожидаемый набор

### Артефакты

- `ai-homework-mentor/.cursor/rules/40-skills-router.mdc`
- обновлённый `.cursor/rules/methodology/40-skills-router.mdc`
- Rich panel Rubric & Skills

### Документы

- 📋 [План задачи](tasks/04-routers-verbose/plan.md)
- 📝 [Summary](tasks/04-routers-verbose/summary.md)

---

## Демонстрация через Rich CLI

```powershell
cd ai-homework-mentor
# Python CLI без API
.\make.ps1 run -- -Path .\tests\fixtures\local_hw -Message "Тема: python-cli" -Verbose

# Fixture/репо с FastAPI (если есть)
.\make.ps1 run -- -Path <fastapi-fixture> -Message "Тема: fastapi-api" -Verbose
```

**Что пользователь увидит:**

| Режим | Ожидаемый вывод |
|-------|-----------------|
| **compact** | Итог review + строка активных skills |
| **verbose** | Subagents (S4) **+** Rubric & Skills: rubric-skill, `modern-python`, опц. `fastapi-templates` с reason |

---

## Вне scope (не делать в S5)

- Reflection и финальные артефакты S6
- Установка skills без чтения SKILL.md
- Исполнение кода студента «чтобы проверить по skill»
- Передача секретов в контекст skill/subagent
- Полная замена rubric YAML — skill **дополняет/носит** критерии, не ломает S2 без миграции

---

## Итог (заполняется после закрытия)

S5 закрыт 2026-07-24: rubric-skills + runtime router + `modern-python`/`fastapi-templates` в `.agents/skills/` + verbose «Rubric & Skills» + оба Cursor-роутера. Lint/tests зелёные (103). Следующий слой — S6 (синтез `final_feedback` / `fix_plan`).

---

## Следующий спринт

После «ок» по S5 → разворот **S6** (`sprint-06-synthesis`): reflection + `final_feedback` + `fix_plan` из review-нот.
