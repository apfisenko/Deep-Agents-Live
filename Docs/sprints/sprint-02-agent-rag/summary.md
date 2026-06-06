# Summary: Sprint 02 — agent-rag

> **Sprint:** [README.md](./README.md)
> **Дата закрытия:** 2026-06-07

---

## Что реализовано

- `backend/app/rag/` — manifest, indexer, store, search; инкрементальная индексация `data/b2b/`, `data/b2c/`
- `backend/app/tools/` — 5 business-tools + `registry.py`
- `backend/app/agent/react_agent.py` — ReAct (LangGraph), SSE-события
- `backend/app/memory/sessions.py` — in-memory сессии
- `backend/app/integrations/openrouter.py`, `langfuse.py` — LLM, embeddings, observability
- `backend/app/api/routers/chat.py`, `admin.py` — JSON + SSE chat, reindex
- `data/b2b/`, `data/b2c/` — sample-документы и каталог
- `backend/tests/` — 18 pytest-тестов (RAG, chat, tools, errors)
- `backend/scripts/check_api.py`, `request_chat.py` — make-цели `check-*`, `chat-*`

---

## Отклонения от плана

- Embeddings: дефолт `openai/text-embedding-3-small` + `EMBEDDING_FALLBACK_MODEL` (Gemini preview нестабилен на OpenRouter).
- Индексация: per-file error handling — битый файл не роняет старт.
- Дополнительно: make-цели проверки API (`check-health`, `check-api`, `chat-telegram`, `chat-stream`).

---

## Принятые решения

| Решение | Причина |
|---------|---------|
| LangGraph + `astream_events` для SSE | Единый runner для JSON и stream |
| In-memory vector store | ADR-0002, MVP без Postgres |
| Reindex только при `ENV=dev` | Безопасность admin-эндпоинта |

---

## Проблемы и решения

| Проблема | Как решили |
|----------|-----------|
| OpenRouter embedding 200 без data | Fallback-модель, конфиг `EMBEDDING_FALLBACK_MODEL` |
| PowerShell `curl` ломает JSON | Скрипты httpx + make-цели вместо raw curl |

---

## Итог DoD

| # | Критерий | Результат |
|---|----------|-----------|
| 1 | RAG индексирует b2b/b2c без дубликатов | ✅ |
| 2 | `POST /admin/reindex` инкрементально | ✅ |
| 3 | ReAct + 5 tools через OpenRouter | ✅ |
| 4 | SSE по контракту | ✅ |
| 5 | JSON chat (telegram) | ✅ |
| 6 | In-memory сессии | ✅ |
| 7 | Воронка мок-оплаты → leads.txt | ✅ |
| 8 | Langfuse traces (при enabled) | ✅ |
| 9 | Ошибки OpenRouter → 503/400 | ✅ |
| 10 | Backend-тесты | ✅ (18 tests) |
| 11 | Health с реальными счётчиками | ✅ |

---

## Что дальше

- **Sprint 03:** Next.js виджет, SSE-клиент, UI по design-reference
- Langfuse traces в UI — проверить после `make up` + `LANGFUSE_ENABLED=true`

---

## Ссылки

- [api-contracts.md](../../concept/api-contracts.md)
- [integrations.md](../../concept/integrations.md)
- ADR-0002 (in-memory), ADR-0003 (mock payment)
