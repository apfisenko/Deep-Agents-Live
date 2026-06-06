# Task 03: Formatters и message handlers

> **Sprint:** [../../README.md](../../README.md)
> **Тип:** feat
> **Ветка:** `feat/bot-3-formatters-handlers`
> **Spec:** [architecture.md](../../../../concept/architecture.md), [api-contracts.md](../../../../concept/api-contracts.md)

---

## Цель

Полный message flow: текст пользователя → Core → Markdown→Telegram HTML; стабильный `session_id` per Telegram `chat_id`.

---

## Состав работ

- [ ] `session_store.py`: dict `chat_id -> session_id`; `get_session_id(chat_id)` создаёт UUID при первом обращении
- [ ] `formatters.py`: `markdown_to_telegram_html(text: str) -> str`
  - Bold `**`, links `[text](url)`, inline code, escape HTML specials
  - Ограничение: subset Markdown (достаточно для ответов агента)
- [ ] Handler `on_text_message`: 
  - `send_chat_action(typing)`
  - `core_client.send_message(session_id, text)`
  - `answer(html, parse_mode=HTML)`
- [ ] Error handlers: CoreUnavailable → «Сервис ИИ временно недоступен»; ModelError → короткое сообщение
- [ ] `/start` обновить: краткая инструкция + mention llmstart.ru
- [ ] `tests/test_formatters.py` — bold, link, escape
- [ ] `tests/test_session_store.py` — same chat_id → same session
- [ ] E2E с running backend + bot token
- [ ] Самопроверка по критериям DoD
- [ ] (после «ок» пользователя) Создать `summary.md`, обновить sprint README.md

---

## Критерии готовности (DoD)

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | Текстовое сообщение → ответ от агента в Telegram | Live test |
| 2 | Два сообщения в одном чате → контекст сохранён | «Какой курс?» → «А расписание?» |
| 3 | Payment link в ответе кликабелен | HTML link in Telegram |
| 4 | 503 от Core → user message, не crash | Stop backend |
| 5 | Formatter tests pass | pytest |
| 6 | Lint проходит | ruff |

> Те же команды пользователь выполняет для самостоятельной верификации.

---

## Артефакты

- `frontend/bot/formatters.py`
- `frontend/bot/session_store.py`
- `frontend/bot/handlers/chat.py` (или inline в main.py)
- `frontend/bot/tests/test_formatters.py`
- `frontend/bot/tests/test_session_store.py`
- `frontend/bot/main.py` — register handlers

---

## Scope

**Трогаем:** артефакты выше.

**НЕ трогаем:**
- Backend agent logic
- Web widget
- docker-compose

---

## Риски и допущения

- Допущение: aiogram `parse_mode=HTML` — экранировать `<`, `>`, `&` в user-generated parts (reply from LLM usually safe).
- Риск: сложный Markdown от LLM — fallback: strip unsupported, send plain text on parse error.
- Альтернатива: `parse_mode=MarkdownV2` — сложнее escape; HTML предпочтительнее per architecture.

---

## Открытые вопросы

- [ ] Нет блокирующих
