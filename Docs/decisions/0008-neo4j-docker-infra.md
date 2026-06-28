# ADR-0008 — Neo4j Docker: порты, compose, persistence, read-only user

> **Статус:** ✅ Accepted
> **Дата:** 2026-06-28
> **Область:** Deep-Agents-Live
> **Extends:** [ADR-0007 — Neo4j GraphRAG](0007-neo4j-graphrag.md), [ADR-0004 — WSL Docker](0004-windows-make-docker-wsl.md)

---

## Контекст

[ADR-0007](0007-neo4j-graphrag.md) фиксирует выбор Neo4j, версии образа/SDK и LPG-схему, но не описывает локальный Docker-стенд: порты, healthcheck, volume, переменные окружения и read-only пользователя для text2cypher (guardrail sprint-06, задача 07).

Задача 04 sprint-06 требует воспроизводимый локальный Neo4j рядом с Qdrant/Langfuse в `docker-compose.yml`.

---

## Решение

### Docker-образ

| Параметр | Значение |
|----------|----------|
| Образ | `neo4j:5.26.2-community` |
| Плагин | APOC (`NEO4J_PLUGINS='["apoc"]'`) |
| Volume | named `neo4j_data` → `/data` |
| Запуск | WSL2 через `make up` / `make graph-up` ([ADR-0004](0004-windows-make-docker-wsl.md)) |

Версия образа совпадает с pin в ADR-0007; Python driver `neo4j==5.28.2` совместим с сервером 5.26.x.

### Порты (host → container)

| Сервис | Host | Container | Назначение |
|--------|------|-----------|------------|
| HTTP (Browser) | **7474** | 7474 | Neo4j Browser, REST API |
| Bolt | **7687** | 7687 | Python driver, cypher-shell |

URL для backend на **Windows-хосте** (Docker в WSL):

- Browser: `http://localhost:7474` (или `http://<wsl-ip>:7474`, если localhost недоступен)
- Driver: `NEO4J_URI=bolt://localhost:7687` — при недоступности localhost backend автоматически пробует WSL IP (аналог `QDRANT_URL`, см. `app/graph/client.py`)

URL из контейнера `backend` (profile `full`): `bolt://neo4j:7687`.

### Переменные окружения

| Переменная | Пример (dev) | Назначение |
|------------|--------------|------------|
| `NEO4J_URI` | `bolt://localhost:7687` | Bolt URI для Python driver |
| `NEO4J_USER` | `neo4j` | Админ-пользователь (seed, graph-index) |
| `NEO4J_PASSWORD` | *(dev secret в `.env`)* | Пароль админа; также `NEO4J_AUTH` в compose |
| `NEO4J_DATABASE` | `neo4j` | Имя БД (Community — одна default) |
| `NEO4J_READONLY_USER` | `text2cypher` | Read-only user для Text2Cypher tool |
| `NEO4J_READONLY_PASSWORD` | *(dev secret в `.env`)* | Пароль read-only user |

Compose подставляет `NEO4J_AUTH=${NEO4J_USER}/${NEO4J_PASSWORD}`.

### Healthcheck

HTTP GET **`/db/neo4j/available`** на порту 7474 внутри контейнера:

```yaml
test: ["CMD-SHELL", "wget --no-verbose --tries=1 --spider http://127.0.0.1:7474/db/neo4j/available || exit 1"]
interval: 10s
timeout: 5s
retries: 10
start_period: 40s
```

Ожидаемый статус в `docker compose ps`: **healthy** перед smoke `make graph-status`.

### APOC (compose env)

```yaml
NEO4J_PLUGINS: '["apoc"]'
NEO4J_apoc_export_file_enabled: "true"
NEO4J_apoc_import_file_enabled: "true"
NEO4J_apoc_import_file_use__neo4j__config: "true"
NEO4J_dbms_security_procedures_unrestricted: apoc.*
NEO4J_dbms_security_procedures_allowlist: apoc.*
```

APOC нужен для import/export и вспомогательных процедур при индексации (задача 05); в runtime retrieval APOC не обязателен.

### Read-only пользователь (text2cypher)

Создаётся **один раз** после первого `make graph-up`: `make graph-init-readonly`. Процедура — [devops/README.md](../../devops/README.md).

#### Community Edition (локальный dev, `neo4j:5.26.2-community`)

**RBAC недоступен:** `CREATE ROLE` / `GRANT` не поддерживаются; все пользователи имеют **admin-привилегии** ([Neo4j docs — Manage users](https://neo4j.com/docs/operations-manual/5/authentication-authorization/manage-users/)).

`graph-init-readonly` выполняет только:

```cypher
CREATE USER text2cypher IF NOT EXISTS
  SET PASSWORD '...'
  CHANGE NOT REQUIRED;
```

Guardrail #1 на dev = **отдельные credentials** для text2cypher (не пароль admin seed). Блокировка write — **guardrails #2–#4** в приложении (задача 07: regex, LIMIT, timeout).

#### Enterprise / Aura (production roadmap)

Роль `text2cypher_reader` с `GRANT MATCH {*} ON GRAPH neo4j` — см. [devops/neo4j/init-readonly-enterprise.cypher](../../devops/neo4j/init-readonly-enterprise.cypher).

Проверка на Enterprise: `CREATE (n:Test) RETURN n` под read-only user → ошибка доступа.

### Make-цели

| Цель | Действие |
|------|----------|
| `make graph-up` | `docker compose up -d neo4j` |
| `make graph-down` | `docker compose stop neo4j` |
| `make graph-status` | `docker compose ps neo4j` + smoke `Connection OK` |
| `make graph-shell` | интерактивный `cypher-shell` в контейнере |
| `make graph-init-readonly` | создать read-only user (после первого up) |

`make up` поднимает **весь** стек, включая Neo4j (сервис без profile).

### Smoke-подключение

`backend/app/graph/client.py` — `verify_connectivity()` через официальный driver.  
`make graph-status` выводит `Connection OK` при успехе.

---

## Последствия

- Локальный graph store готов к задаче 05 (`make graph-index`)
- Read-only credentials изолированы от admin seed
- Персистентность данных между `graph-down`/`graph-up` и `make down`/`make up` (volume не удаляется без `down -v`)
- Windows: backend smoke использует WSL IP fallback для Bolt, как для Qdrant REST

---

## Ссылки

- [ADR-0007 — Neo4j GraphRAG](0007-neo4j-graphrag.md)
- [devops/README.md](../../devops/README.md)
- [Sprint-06 задача 04](../sprints/sprint-06-graphrag/README.md)

---

## История изменений

| Дата | Изменение |
|------|-----------|
| 2026-06-28 | Первая версия |
| 2026-06-28 | Community: RBAC недоступен; graph-init-readonly = CREATE USER + app guardrails |
