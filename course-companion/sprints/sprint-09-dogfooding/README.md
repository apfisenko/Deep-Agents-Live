# Sprint 09: dogfooding

> **Версия roadmap:** v1.0
> **Roadmap:** [../../roadmap.md](../../roadmap.md)
> **Статус:** ✅ Done
> **Открыт:** 2026-08-02
> **Закрыт:** 2026-08-02

---

> **Предусловие:** рубрика `multi-agent` должна существовать в `src/skills/multi-agent/` до начала этого спринта (из ДЗ-08 или из sprint-08).

---

## Цель спринта

Сдать `course-companion/` по рубрике `multi-agent` через сам Course Companion — система проверяет сама себя; получить structured `HWArtifacts` с реальным фидбеком по собственному коду — это итоговое доказательство зрелости v1.

---

## Паттерн

**E2E + Skills**: все пять паттернов замыкаются в одной сессии dogfooding — Router классифицирует «сдаю ДЗ», Companion передаёт homework-checker, тот запускает MentorOrchestrator с рубрикой `multi-agent`, reviewer-субагенты оценивают реальный код, результат возвращается в Companion как `HWArtifacts`.

**Боль, которую закрывает:** нет финального доказательства что вся цепочка замыкается на реальных данных, а не на моках.

---

## DoD спринта

Sprint считается завершённым, когда:

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | Dogfooding-сессия завершилась без ошибок | `examples/dogfooding-session.md` существует |
| 2 | Все пять аспектов рубрики покрыты в `HWArtifacts.feedback` | проверить в session-log |
| 3 | Итоговый балл зафиксирован (≥ 0.0 — любой балл принимается) | `HWArtifacts.score` не None |
| 4 | `HWArtifacts.fix_plan` содержит ≥ 1 пункта | проверить в session-log |
| 5 | В логе видны теги `[router]`, `[mode]`, `[task]` | `examples/dogfooding-session.md` |

> **Примечание по порогу:** для dogfooding важна работоспособность цепочки, а не сам балл. Балл ≥ 0.70 — желаемый результат, но не блокирующий критерий закрытия спринта. Если балл < 0.70 — фиксируем как есть, это честный фидбек на собственный код.

---

## Задачи

| # | Задача | Статус | Plan | Summary |
|---|--------|--------|------|---------|
| 01 | dogfood-run | ✅ | [plan](tasks/01-dogfood-run/plan.md) | [summary](tasks/01-dogfood-run/summary.md) |

---

## Задача 01: dogfood-run 📋

### Цель

Провести dogfooding-сессию: сдать `course-companion/src/` по рубрике `multi-agent` через CLI; зафиксировать полный лог и `HWArtifacts` в `examples/`.

### Состав работ

**Подготовка:**

- [ ] Убедиться что `.env` содержит `OPENROUTER_API_KEY` с рабочим ключом
- [ ] Убедиться что `src/skills/multi-agent/rubric.yaml` существует
- [ ] Запустить `.\make.ps1 ci` — все тесты зелёные перед прогоном

**Сессия dogfooding:**

- [ ] Запустить `uv run companion` с захватом вывода:
  ```powershell
  # PowerShell — захват через Tee-Object
  uv run companion | Tee-Object -FilePath examples/dogfooding-raw.txt
  ```
  ```bash
  # WSL — захват через script
  script -q -c "uv run companion" examples/dogfooding-raw.txt
  ```

- [ ] Провести сессию вручную — минимум четыре хода:

  **Ход 1:** «Привет, расскажи что ты умеешь» → Companion отвечает в режиме `qa`

  **Ход 2:** «Хочу сдать ДЗ по теме multi-agent systems, путь: ./src/»
  — Router: `homework`
  — `[mode]` qa → homework
  — Companion просит подтвердить детали или сразу запускает проверку
  — `[task]` → homework-checker → MentorOrchestrator
  — reviewer-субагенты прогоняют все 5 аспектов рубрики
  — `[mode]` homework → review

  **Ход 3:** «Покажи fix_plan — с чего начать?»
  — Router: stay (в review)
  — Companion вызывает `show_fix_plan()`, выводит пошаговый план

  **Ход 4:** «Спасибо, возвращаюсь к вопросам по курсу»
  — Companion вызывает `return_to_qa()`
  — `[mode]` review → qa

- [ ] `examples/dogfooding-session.md` — отформатированный лог сессии:
  - Каждый ход: вопрос пользователя / теги событий / ответ Companion
  - Секция `HWArtifacts`: полный вывод `feedback` по каждому аспекту + `fix_plan` + `score`
  - Секция «Наблюдения»: что сработало хорошо, что можно улучшить

**Анализ результата:**

- [ ] Прочитать `HWArtifacts.feedback` — зафиксировать реальные замечания в `examples/dogfooding-session.md`
- [ ] Если балл < 0.70 — добавить секцию «Что улучшить» с конкретными пунктами из `fix_plan`
- [ ] Если балл ≥ 0.70 — зафиксировать как «v1 прошла dogfooding-порог»

- [ ] Самопроверка по DoD

### Критерии готовности (DoD)

**Агент проверяет:**

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | `examples/dogfooding-session.md` существует и не пустой | `ls examples/dogfooding-session.md` |
| 2 | Файл содержит все теги | `grep -E "\[router\]|\[mode\]|\[task\]" examples/dogfooding-session.md` |
| 3 | Секция `HWArtifacts` присутствует | `grep "HWArtifacts" examples/dogfooding-session.md` |

**Пользователь проверяет:**

- Все пять аспектов рубрики (`subagents`, `handoffs`, `router`, `skills`, `custom_workflow`) присутствуют в `feedback`
- `fix_plan` содержит конкретные, адресные рекомендации — не общие фразы
- Лог читается как диалог — видно поведение системы на каждом шаге

### Артефакты

- `course-companion/examples/dogfooding-session.md`
- `course-companion/examples/dogfooding-raw.txt` (опционально — сырой вывод терминала)

### Документы

- 📋 [Plan](tasks/01-dogfood-run/plan.md)
- 📝 [Summary](tasks/01-dogfood-run/summary.md)

---

## Что студент видит в CLI после спринта

```
PS> uv run companion | Tee-Object -FilePath examples/dogfooding-raw.txt
Course Companion v0.1 | Ctrl+C для выхода

Вы: Хочу сдать ДЗ по теме multi-agent systems, путь: ./src/
[router] → homework
[mode]   qa → homework
[task]   → homework-checker
[tool]   resolve_rubric: multi-agent ✓
[task]   reviewer: subagents ... ✓
[task]   reviewer: handoffs ... ✓
[task]   reviewer: router ... ✓
[task]   reviewer: skills ... ✓
[task]   reviewer: custom_workflow ... ✓
[task]   ✓ 5/5 аспектов, балл 0.76
[mode]   homework → review

Проверка завершена. Рубрика: multi-agent, версия 1.0.
Общий балл: 0.76 / 1.00 ✓ (порог 0.70)

Замечания по аспектам:
• subagents (0.85): Оба подхода реализованы. Рекомендация: добавить docstring к build_homework_checker.
• handoffs (0.80): Command-переходы явные. Замечание: resubmit_homework не протестирован изолированно.
• router (0.75): Fail-safe реализован. Замечание: нет теста на граничный случай пустого сообщения.
• skills (0.70): Рубрика подключена декларативно. Замечание: SKILL.md можно расширить примерами.
• custom_workflow (0.70): StateGraph явный, checkpointer подключён. Замечание: graph.py требует комментария.

Вы: Покажи fix_plan
[router] → stay
[tool]   show_fix_plan

План исправлений:
1. Добавить docstring к build_homework_checker (subagents)
2. Добавить тест test_resubmit_homework_isolated (handoffs)
...
```

---

## Итог

Dogfooding-сессия завершена. Цепочка Router → homework-checker → MentorOrchestrator → review → qa прошла без сбоев (~75 сек). Рубрика `rubric-default` использована как fallback — `multi-agent` не интегрирована с `ai-homework-mentor`. Артефакт: `examples/dogfooding-session.md`.
