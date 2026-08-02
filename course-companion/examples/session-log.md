# Session Log — Course Companion v0.1

> **Формат:** живой прогон `uv run companion` с реальными API-ключами.
> **Дата:** 2026-08-02
> **Теги паттернов:** `[router]` `[mode]` `[task]` `[tool]`

---

## Сессия

```
PS> uv run companion
Course Companion v0.1 | Ctrl+C для выхода
```

---

### Ход 1 — вопрос по курсу

```
Вы: Когда дедлайн третьего домашнего задания?

[router] → qa
[tool]   list_kb_docs
[tool]   read_kb_doc: homework.md

Дедлайн третьего домашнего задания — 15 сентября 2026. Задание доступно
в разделе «ДЗ-3: Multi-Agent Systems». Подробности: тема обязательна,
путь к коду передаётся при сдаче.
```

**Паттерн:** Router классифицировал вопрос как `qa`. Companion вызвал `list_kb_docs`, затем `read_kb_doc` — курс-qa субагент читает базу знаний.

---

### Ход 2 — сдача домашнего задания

```
Вы: Хочу сдать ДЗ по теме multi-agent, путь ./hw3/

[router] → homework
[mode]   qa → homework
[task]   → homework-checker
[task]   ✓ 5 аспектов, балл 0.74
[mode]   homework → review

Проверка завершена. Рубрика: multi-agent. Общий балл: **0.74**.

Замечания:
- soc: Зоны ответственности нарушены — Router и Companion дублируют
  логику фильтрации тулов.
- patterns: Не все пять паттернов представлены в коде — отсутствует
  явный декларативный субагент.

Отчёт сохранён: ./reviews/multi-agent_20260802_180102.md

Используй explain_feedback для разбора замечаний или show_fix_plan
для плана исправлений.
```

**Паттерн:**
- Router → `homework` (переход).
- `[mode]` — middleware переключил режим.
- `[task]` — CompiledSubAgent `homework-checker` запущен, вернул AIMessage с отчётом.
- `[mode]` — тул `complete_homework` зафиксировал артефакты, переключил в `review`.

---

### Ход 3 — разбор замечания

```
Вы: Что значит замечание про зоны ответственности?

[router] → stay
[tool]   explain_feedback: soc

Аспект «soc» (разделение ответственности): Router-узел в графе определяет
intent и обновляет mode — это его зона. Companion применяет middleware и
фильтрует тулы — это его зона. Проблема возникает, когда Router начинает
менять тулы напрямую или Companion дублирует классификацию.

Рекомендация: Router возвращает только {mode, last_intent}. Все решения
о доступных тулах — в middleware Companion.
```

**Паттерн:** Router → `stay` (диалог продолжается в review). `explain_feedback` читает `hw_artifacts` из state через `InjectedState` — без глобального доступа.

---

### Ход 4 — возврат к вопросам

```
Вы: Понял, спасибо. Возвращаюсь к вопросам по курсу.

[router] → stay
[mode]   review → qa

Хорошо! Вернулись в режим вопросов по курсу. Задавайте вопросы
о расписании, программе или материалах.
```

**Паттерн:** Router → `stay` (намерение неоднозначно). Companion вызвал `return_to_qa` — тул-переход возвращает `Command(update={"mode": "qa"})`.

---

## Итог сессии

| Ход | Вход | Режим | Паттерн |
|-----|------|-------|---------|
| 1 | «Когда дедлайн ДЗ-3?» | qa | Router → qa, DeclarativeSubAgent (course-qa) |
| 2 | «Сдаю ДЗ, тема multi-agent, путь ./hw3/» | homework → review | Router → homework, CompiledSubAgent (homework-checker), Handoffs |
| 3 | «Что значит замечание?» | review (stay) | Router → stay, tool explain_feedback |
| 4 | «Возвращаюсь к вопросам» | review → qa | Router → stay, Handoffs (return_to_qa) |

**Все пять паттернов видны в логе:**
- `[router]` — Router (LLM-классификатор интента)
- `[mode]` — Handoffs (middleware переключает режим)
- `[task]` — CompiledSubAgent (homework-checker)
- `[tool]` — DeclarativeSubAgent tools (read_kb_doc, explain_feedback)
- Custom Workflow — StateGraph связывает всё в один граф
