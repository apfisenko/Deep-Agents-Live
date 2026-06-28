# DevOps — локальная инфраструктура

Операционные процедуры для Docker-сервисов Deep-Agents-Live. Архитектурные решения — в [Docs/decisions](../Docs/decisions/).

---

## Neo4j (graph DB, sprint-06)

Спецификация: [ADR-0008](../Docs/decisions/0008-neo4j-docker-infra.md), [ADR-0007](../Docs/decisions/0007-neo4j-graphrag.md).

| | |
|---|---|
| **Образ** | `neo4j:5.26.2-community` + APOC |
| **Browser** | http://localhost:7474 |
| **Bolt** | `bolt://localhost:7687` |
| **Volume** | `neo4j_data` (persist между `down`/`up`) |
| **Health** | `GET http://localhost:7474/db/neo4j/available` |

### Поднять / проверить

```powershell
.\make.ps1 graph-up
.\make.ps1 graph-status
# Ожидается: neo4j healthy + Connection OK

# или весь стек (Langfuse + Qdrant + Neo4j):
.\make.ps1 up
.\make.ps1 ps
```

Linux/macOS/WSL: `make graph-up`, `make graph-status`.

Интерактивный Cypher (без ручного `docker exec`):

```powershell
.\make.ps1 graph-shell
```

### Пользователь text2cypher (`NEO4J_READONLY_*`)

Text2Cypher в runtime использует **отдельные** credentials, не admin (`NEO4J_USER`).

**Один раз** после первого `graph-up`:

```powershell
.\make.ps1 graph-init-readonly
```

#### Community Edition (наш dev-образ)

Neo4j **Community** не поддерживает RBAC: команды `CREATE ROLE` / `GRANT` выдают `Unsupported administration command`. Все пользователи имеют admin-привилегии.

`graph-init-readonly` на Community:

1. `CREATE USER` (`NEO4J_READONLY_USER` / `NEO4J_READONLY_PASSWORD`)
2. Проверка логина: `RETURN 1 AS ok`

Guardrail #1 на dev = **изоляция credentials** (text2cypher не использует пароль seed).  
Блокировка write — **guardrails #2–#4 в приложении** (задача 07: regex на write-клаузы, LIMIT, timeout).

#### Enterprise / Aura (production)

Полный read-only RBAC: [devops/neo4j/init-readonly-enterprise.cypher](neo4j/init-readonly-enterprise.cypher).

Проверка на Enterprise — `CREATE (n:Test)` под `text2cypher` → ошибка доступа.

#### Проверка логина (Community)

```powershell
wsl -e bash -lc "cd '$(wslpath -a .)' && docker compose exec -T neo4j cypher-shell -u text2cypher -p '<NEO4J_READONLY_PASSWORD>' 'RETURN 1 AS ok;'"
```

Или через Browser: http://localhost:7474, Connect URL `bolt://localhost:7687`, user `text2cypher`.

### Переменные (.env)

См. `.env.example`: `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`, `NEO4J_DATABASE`, `NEO4J_READONLY_USER`, `NEO4J_READONLY_PASSWORD`.

На Windows backend автоматически пробует WSL IP, если `bolt://localhost:7687` недоступен (как для Qdrant).

### Сброс данных

```powershell
.\make.ps1 compose down -v   # удалит все volumes, включая neo4j_data
.\make.ps1 up
.\make.ps1 graph-init-readonly
```

После сброса нужно заново создать read-only user и выполнить `make graph-index` (задача 05).
