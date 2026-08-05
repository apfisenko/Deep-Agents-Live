# ADR 009: A2UI drill channel

**Статус:** accepted  
**Спринт:** 13 (drill-a2ui)

## Контекст

Тренажёр (drill) требует динамическую форму кейса — плоский текст в чате не подходит.
A2UI v0.9 описывает UI декларативно; companion решает *что* спросить, отдельный
LLM-вызов в drill-модуле — *как* отрисовать форму.

## Решение

Три HTTP-канала на ступени 4:

| Канал | Путь | Назначение |
|-------|------|------------|
| 1 | Agent Server `/threads` | чат (useStream) |
| 2 | `POST /drill/a2ui` (http.app) | генерация формы + доставка userAction (SSE) |
| 3 | checker `:2025` | поллер фоновой проверки |

- `show_drill_case` пишет кейс в `drill_case` (values) → фронт монтирует `DrillPanel`.
- Ответ студента: drill-endpoint → `CompanionDelivery` → служебное `[drill]` сообщение
  в тред (enqueue) → разбор текстом в канале 1.
- `[авто]` / `[drill]` — `SERVICE_PREFIXES`: router stay, режим не меняется
  (фидбек проверки может прийти mid-drill).

## Последствия

- Drill только в web-пути (deepagents + server_modes); CLI без drill.
- Зависимости: `a2ui-agent-sdk==0.4.0`, `@a2ui/react/v0_9` на фронте.
- Windows: `examples_path` для A2UI — `Path.as_uri()` (file://).
