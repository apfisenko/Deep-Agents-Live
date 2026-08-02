# ADR 002: CompiledSubAgent vs DeclarativeSubAgent для субагентов

**Статус:** Принято  
**Дата:** 2026-08-02  
**Автор:** Course Companion Team

---

## Контекст

Course Companion включает два субагента с принципиально разными характеристиками:
- `homework-checker` — проверяет конкретное ДЗ, требует путь и тему в runtime
- `course-qa` — отвечает на вопросы по статичной базе знаний

Необходимо выбрать паттерн реализации для каждого.

## Решение

- `homework-checker` реализован как **CompiledSubAgent** (`build_homework_checker(path, topic)` возвращает `CompiledStateGraph`).
- `course-qa` реализован как **DeclarativeSubAgent** (`COURSE_QA_SPEC` — словарь `{tools, system_prompt}`).

## Обоснование

**homework-checker — CompiledSubAgent:**

Рубрика и путь к workspace известны только в момент вызова (`run_homework_check`). Граф собирается с этими параметрами в `build_homework_checker()` и возвращает готовый `Runnable`. Ошибки пайплайна `MentorOrchestrator` перехватываются и оборачиваются в `AIMessage` — граф никогда не бросает исключение наружу.

**course-qa — DeclarativeSubAgent:**

База знаний статична (набор `.md`-файлов в `data/kb/`). Субагент описывается промптом и двумя тулами (`list_kb_docs`, `read_kb_doc`). Нет runtime-параметров — нет необходимости компилировать граф заново при каждом вызове. Companion инстанциирует агент на месте через `create_react_agent`.

## Альтернативы

| Вариант | Почему отклонён |
|---------|----------------|
| Оба как Compiled | Избыточно для course-qa: нет runtime-параметров |
| Оба как Declarative | homework-checker не может быть статичным — рубрика и путь приходят в runtime |
| REST API для ментора | Оверкилл для CLI-инструмента |

## Последствия

- Разные паттерны подчёркивают разницу в природе субагентов — ценно как учебный пример.
- `build_homework_checker` вызывается каждый раз при сдаче ДЗ — незначительный оверхед компиляции.
- `COURSE_QA_SPEC` легко расширить новыми тулами без изменения companion.
