# Sprint 08: rubric-multi-agent ⚠️ опциональный

> **Версия roadmap:** v0.8
> **Roadmap:** [../../roadmap.md](../../roadmap.md)
> **Статус:** ✅ Done
> **Открыт:** 2026-08-02
> **Закрыт:** 2026-08-02

---

> **Условие выполнения:** этот спринт выполняется только если рубрика `multi-agent` **не была создана** в рамках ДЗ-08 курса Deep Agents.
> Если рубрика уже существует в `ai-homework-mentor` — этот спринт пропускается, переходим сразу к sprint-09.
>
> **Зависимость:** должен быть выполнен **до** sprint-09-dogfooding.

---

## Цель спринта

Создать рубрику `multi-agent` как подключаемую Skills-экспертизу для `ai-homework-mentor`: `rubric.yaml` с пятью аспектами и `SKILL.md` с системным промптом для reviewer-субагентов — без изменения кода ментора.

---

## Паттерн

**Skills** — рубрика = YAML + SKILL.md; подключается к `ai-homework-mentor` декларативно, без правки кода агента. Это и есть демонстрация паттерна Skills в продукте.

**Боль, которую закрывает:** без рубрики `multi-agent` dogfooding невозможен — ментор не знает по каким критериям проверять мультиагентный код.

---

## DoD спринта

Sprint считается завершённым, когда:

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | `rubric.yaml` валиден: 5 аспектов, веса по 0.20, сумма = 1.0 | `python -c "import yaml; r=yaml.safe_load(open('src/skills/multi-agent/rubric.yaml')); assert sum(a['weight'] for a in r['aspects']) == 1.0"` |
| 2 | `resolve_rubric("multi-agent")` возвращает рубрику | `pytest tests/skills/test_resolve_rubric.py -v` |
| 3 | `resolve_rubric("multi agent systems")` — тоже находит рубрику (fuzzy) | `pytest tests/skills/test_resolve_rubric.py::test_fuzzy_match -v` |
| 4 | `SKILL.md` содержит инструкции для каждого из пяти аспектов | просмотр файла |

---

## Задачи

| # | Задача | Статус | Plan | Summary |
|---|--------|--------|------|---------|
| 01 | rubric-yaml | ✅ | [plan](tasks/01-rubric-yaml/plan.md) | [summary](tasks/01-rubric-yaml/summary.md) |

---

## Задача 01: rubric-yaml 📋

### Цель

Создать `src/skills/multi-agent/rubric.yaml` и `SKILL.md`; реализовать `resolve_rubric()` с fuzzy-matching по имени темы; покрыть unit-тестом.

> 💡 **Скиллы:** `.agents/skills/python-testing-patterns/SKILL.md`

### Состав работ

**rubric.yaml:**

- [ ] `src/skills/multi-agent/rubric.yaml`:

  ```yaml
  name: multi-agent
  version: "1.0"
  description: Рубрика проверки мультиагентных систем на курсе Deep Agents
  match_keywords:
    - multi-agent
    - multi agent
    - мультиагент
    - subagents
    - handoffs
    - langgraph
    - deepagents

  aspects:
    - id: subagents
      name: Субагенты
      weight: 0.20
      criteria:
        - Агенты изолированы — каждый решает одну задачу
        - Использованы минимум два подхода (declarative + compiled)
        - Субагенты не взаимодействуют с пользователем напрямую

    - id: handoffs
      name: Handoffs (передача управления)
      weight: 0.20
      criteria:
        - Реализован механизм переключения режимов без создания нового агента
        - История диалога сохраняется при переключении
        - Переход задаётся явным Command, не неявной логикой

    - id: router
      name: Router (классификатор интента)
      weight: 0.20
      criteria:
        - Router отделён от основной логики агента
        - Structured output используется для классификации
        - Реализована sticky-логика (stay) и fail-safe

    - id: skills
      name: Skills (подключаемая экспертиза)
      weight: 0.20
      criteria:
        - Рубрика описана декларативно (YAML + SKILL.md)
        - Рубрика подключается без изменения кода агента
        - Присутствует рубрика для dogfooding-проверки

    - id: custom_workflow
      name: Custom Workflow
      weight: 0.20
      criteria:
        - Используется явный StateGraph, не магия фреймворка
        - State типизирован (TypedDict или Pydantic)
        - Checkpointer подключён для многоходового диалога

  scoring:
    pass_threshold: 0.70
    output_format: structured
  ```

**SKILL.md:**

- [ ] `src/skills/multi-agent/SKILL.md` — системный промпт для reviewer-субагентов ментора:
  - Описание роли: «Ты — ревьюер мультиагентных систем на курсе Deep Agents»
  - Инструкции по каждому аспекту: что проверять, на что обращать внимание
  - Формат вывода: оценка по аспекту (0.0–1.0) + конкретные замечания + рекомендация по исправлению
  - Не менее 3 конкретных критериев по каждому из 5 аспектов

**resolve_rubric:**

- [ ] `src/course_companion/skills/resolver.py`:

  ```python
  SKILLS_DIR = Path(__file__).parent.parent.parent / "skills"

  def resolve_rubric(topic: str) -> dict:
      """Находит рубрику по теме. Матчинг по match_keywords (case-insensitive, substring).
      Raises FileNotFoundError если рубрика не найдена.
      """
      topic_lower = topic.lower()
      for rubric_dir in SKILLS_DIR.iterdir():
          rubric_file = rubric_dir / "rubric.yaml"
          if not rubric_file.exists():
              continue
          rubric = yaml.safe_load(rubric_file.read_text(encoding="utf-8"))
          keywords = [kw.lower() for kw in rubric.get("match_keywords", [])]
          if any(kw in topic_lower for kw in keywords):
              return rubric
      raise FileNotFoundError(f"No rubric found for topic: {topic!r}")
  ```

- [ ] `src/course_companion/skills/__init__.py`

**Тесты:**

- [ ] `tests/skills/__init__.py`
- [ ] `tests/skills/test_resolve_rubric.py`:

  **test_exact_match** — `resolve_rubric("multi-agent")["name"] == "multi-agent"`

  **test_fuzzy_match** — `resolve_rubric("multi agent systems")["name"] == "multi-agent"`

  **test_keyword_match** — `resolve_rubric("задание по deepagents и handoffs")["name"] == "multi-agent"`

  **test_not_found** — `resolve_rubric("blockchain")` → `FileNotFoundError`

- [ ] `.\make.ps1 test` — все тесты проходят
- [ ] Самопроверка по DoD

### Критерии готовности (DoD)

**Агент проверяет:**

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | Сумма весов аспектов == 1.0 | `assert sum(...) == 1.0` |
| 2 | Все 4 теста resolver'а проходят | `uv run pytest tests/skills/ -v` |
| 3 | `resolve_rubric` не зависит от cwd | путь вычисляется от `__file__` |

**Пользователь проверяет:**

- `SKILL.md` содержит конкретные инструкции — не абстрактные принципы; reviewer понимает что именно искать в коде
- `match_keywords` покрывает типичные варианты названия темы ДЗ студентами

### Артефакты

- `course-companion/src/skills/multi-agent/rubric.yaml`
- `course-companion/src/skills/multi-agent/SKILL.md`
- `course-companion/src/course_companion/skills/__init__.py`
- `course-companion/src/course_companion/skills/resolver.py`
- `course-companion/tests/skills/__init__.py`
- `course-companion/tests/skills/test_resolve_rubric.py`

### Документы

- 📋 [Plan](tasks/01-rubric-yaml/plan.md)
- 📝 [Summary](tasks/01-rubric-yaml/summary.md)

---

## Что студент видит в CLI после спринта

```
PS> .\make.ps1 test
...
tests/skills/test_resolve_rubric.py::test_exact_match PASSED
tests/skills/test_resolve_rubric.py::test_fuzzy_match PASSED
tests/skills/test_resolve_rubric.py::test_keyword_match PASSED
tests/skills/test_resolve_rubric.py::test_not_found PASSED

========================= 29 passed =========================
```

*(Рубрика готова. Dogfooding — следующий спринт.)*

---

## Итог

Рубрика `multi-agent` создана. `resolve_rubric()` находит рубрику по fuzzy-matching на `match_keywords`. `make ci` — lint ✅ / typecheck ✅ / 43 tests ✅.
