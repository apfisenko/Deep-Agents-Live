# Summary: Задача 07 — Text2Cypher с guardrails

> **План:** [plan.md](./plan.md)  
> **Sprint:** [../../README.md](../../README.md#задача-07-инструмент-text2cypher-с-guardrails--done)  
> **Дата закрытия:** 2026-07-03

---

## Что реализовано

### Guardrails и executor

- [`backend/app/rag/text2cypher/guardrails.py`](../../../../../backend/app/rag/text2cypher/guardrails.py) — **#2** regex write-block (`CREATE|MERGE|DELETE|SET|REMOVE|DROP` → `ValueError`), **#3** auto `LIMIT 50`, timeout 5s на execute
- [`backend/app/rag/text2cypher/executor.py`](../../../../../backend/app/rag/text2cypher/executor.py) — `GuardedText2CypherExecutor`: NL → LLM (neo4j-graphrag `Text2CypherTemplate`) → guardrails → EXPLAIN read-only → execute
- [`backend/app/graph/client.py`](../../../../../backend/app/graph/client.py) — **#1** `get_text2cypher_driver()` на `NEO4J_READONLY_*`

### Prompt assets

- [`backend/app/rag/text2cypher/schema_enhanced.json`](../../../../../backend/app/rag/text2cypher/schema_enhanced.json) — trimmed LPG schema (labels, rels, canonical slugs) из [schema.md](../../schema.md)
- [`backend/app/rag/text2cypher/examples.py`](../../../../../backend/app/rag/text2cypher/examples.py) — 7 few-shot NL→Cypher (G2, G3, G4 + COUNT/SUM)
- [`backend/app/rag/text2cypher/schema_loader.py`](../../../../../backend/app/rag/text2cypher/schema_loader.py) — загрузка schema в промпт

### Retriever и tool

- [`backend/app/rag/retriever/text2cypher_backend.py`](../../../../../backend/app/rag/retriever/text2cypher_backend.py) — замена stub; `RETRIEVER_BACKEND=text2cypher`; Langfuse span `text2cypher-retrieval`
- [`backend/app/tools/text2cypher_tool.py`](../../../../../backend/app/tools/text2cypher_tool.py) — **#4** `query_catalog_aggregate` (узкий docstring; **не** в agent registry — задача 08)

### Конфиг и infra

- [`backend/app/config.py`](../../../../../backend/app/config.py) — `TEXT2CYPHER_MODEL`, `TEXT2CYPHER_QUERY_TIMEOUT_MS`, `TEXT2CYPHER_DEFAULT_LIMIT`
- [`.env.example`](../../../../../.env.example) — `TEXT2CYPHER_*`
- [`Makefile`](../../../../../Makefile), [`make.ps1`](../../../../../make.ps1) — `text2cypher-smoke`; `test-backend` с пробросом args

### Тесты и smoke

- [`backend/tests/test_text2cypher_guardrails.py`](../../../../../backend/tests/test_text2cypher_guardrails.py) — `test_text2cypher_write_blocked`, `test_text2cypher_limit_injected` (+ parametrized write keywords)
- [`backend/scripts/text2cypher_smoke.py`](../../../../../backend/scripts/text2cypher_smoke.py) — 2 NL-вопроса (count курсов + pricing комбо)

### Команды проверки

```powershell
.\make.ps1 test-backend tests/test_text2cypher_guardrails.py -v --log-cli-level=INFO
.\make.ps1 text2cypher-smoke
```

```bash
make test-backend ARGS="tests/test_text2cypher_guardrails.py -v"
make text2cypher-smoke
```

**Smoke (2026-07-03):** 2/2 PASS — count=4, combo pricing + discount из Neo4j.

---

## Отклонения от плана

| Отклонение | Причина |
|------------|---------|
| `GuardedText2CypherExecutor` вместо прямого `Text2CypherRetriever.search()` | Нужен контроль guardrails **до** execute; SDK retriever не даёт hook между generation и run |
| Tool не зарегистрирован в `get_agent_tools()` | По scope: agent routing — задача 08 |
| Eval subset `graphrag-gl-04` не прогонялся отдельным YAML | Smoke + unit достаточны для DoD задачи 07; segment eval — задача 08 |
| Reranker default → `jinaai/jina-reranker-v2-base-multilingual` (вне scope 07) | Исправление упавших тестов + согласование с `graphrag-v001.yaml` |

---

## Принятые решения

| Решение | Причина | ADR |
|---------|---------|-----|
| Отдельный readonly driver, не admin | Guardrail #1: изоляция credentials | [ADR-0008](../../../../decisions/0008-neo4j-docker-infra.md) |
| App-level regex + SDK EXPLAIN guard | Defense in depth; Community без RBAC | [ADR-0007](../../../../decisions/0007-neo4j-graphrag.md) |
| Enhanced schema JSON, не auto-fetch DB | Меньше токенов, только allowed labels из schema.md | [schema.md](../../schema.md) |
| Ошибка guard → empty chunks, не vector fallback | Не маскировать блокировку write | plan §Text2CypherBackend |

---

## Проблемы и решения

| Проблема | Как решили |
|----------|-----------|
| `text2cypher_smoke.py`: `ModuleNotFoundError: app` | Bootstrap `sys.path` + `load_repo_env()` как в `check_neo4j.py` |
| `make.ps1 test-backend ARGS=...` игнорировал args | Проброс `$DockerArgs` в `uv run pytest @DockerArgs` |
| Qdrant URL tests падали из-за кэша между тестами | `reset_qdrant_url_cache()` + autouse fixture |
| `test_retriever_run_config` ожидал BAAI reranker | Синхронизация с jina model в config/YAML |

---

## Итог DoD

| # | Критерий | Результат |
|---|----------|-----------|
| 1 | Write Cypher блокируется до execute | ✅ `test_text2cypher_write_blocked` |
| 2 | Read-only credentials | ✅ `get_text2cypher_driver()` + `NEO4J_READONLY_*` |
| 3 | COUNT/pricing возвращает rows | ✅ smoke 2/2 |
| 4 | Tool description — узкий scope | ✅ `query_catalog_aggregate` docstring |
| 5 | `make test-backend` green | ✅ 94 passed |
| 6 | Enhanced schema + ≥5 few-shot | ✅ JSON + 7 examples |

**Sprint DoD #5** (text2cypher за guardrails): ✅ закрыт задачей 07.

**Пользовательская проверка (частично отложена):** agent routing «text2cypher vs vector» — задача 08.

---

## Что дальше

- **Задача 08:** registry `query_catalog_aggregate`, routing rules в system prompt, eval `graphrag-final`, decision log
- **Global backend:** pricing keywords всё ещё vector-fallback — routing в 08 направит на `text2cypher`
- **`summary.md` sprint-06:** закрытие спринта после задачи 08

---

## Ссылки

- [schema.md](../../schema.md) §3.4 — этalon Cypher для gl-04
- [ADR-0007 Neo4j GraphRAG](../../../../decisions/0007-neo4j-graphrag.md)
- [ADR-0008 Neo4j Docker infra](../../../../decisions/0008-neo4j-docker-infra.md)
- [devops/README.md](../../../../../devops/README.md) — readonly user `text2cypher`
- [graphrag-v001 itog](../../../../../../evals/reports/graphrag-v001-20260703-itog.md) — gl-04 отложен до text2cypher
