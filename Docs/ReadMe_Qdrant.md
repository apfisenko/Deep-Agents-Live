# Qdrant Dashboard: поиск и отладка

Руководство по работе с Web UI Qdrant для проекта Deep-Agents-Live.

**Dashboard:** http://localhost:6333/dashboard  
**REST API:** http://localhost:6333  
**Документация Qdrant:** https://qdrant.tech/documentation/web-ui/

---

## Коллекция проекта

| Параметр | Значение |
|---|---|
| Коллекция | `knowledge_base` (env: `QDRANT_COLLECTION`) |
| Dense-вектор | `dense`, 1536 dim, Cosine |
| Sparse-вектор | `sparse` (hybrid, RRF) |
| Payload | `audience`, `source_path`, `doc_id`, `chunk_id`, `text` |
| Индекс payload | `audience` (keyword) |

Прямая ссылка на коллекцию:

http://localhost:6333/dashboard#/collections/knowledge_base

Конфигурация backend: `backend/app/rag/qdrant_store.py`, `backend/app/config.py`.

---

## Три уровня «поиска» в Dashboard

| Способ | Где | Что ищет |
|---|---|---|
| Фильтр по payload / ID | **Points** | Поля payload, ID точки — не semantic |
| Similarity от точки | **Find Similar**, **Graph** | Ближайшие векторы к выбранной точке |
| Полный vector search | **Console** | REST API: dense, фильтры, hybrid |

---

## 1. Points — просмотр и фильтр

**Путь:** Collections → `knowledge_base` → вкладка **Points**

Здесь можно:

- листать точки;
- искать **по ID** точки;
- фильтровать по payload, например `audience = b2b` или `source_path` содержит `PORTFOLIO`.

Это **не** поиск по смыслу текста — только по ID и полям payload.

---

## 2. Find Similar — быстрый similarity search

**Путь:** Points → открыть точку → **Find Similar**

Dashboard возьмёт dense-вектор этой точки и найдёт ближайшие. Эквивалент в REST API:

```http
POST /collections/knowledge_base/points/query
Content-Type: application/json
```

```json
{
  "query": "00675b96-6a85-587e-a1ed-3a868e08c02a",
  "using": "dense",
  "limit": 5,
  "with_payload": ["text", "source_path", "audience"]
}
```

Пример результата (живой инстанс):

```
score=1.0000  audience=b2b  source=b2b/PORTFOLIO.pdf
score=0.5751  audience=b2b  source=b2b/PORTFOLIO.pdf
...
```

Кнопка **Open Graph** у точки открывает вкладку **Graph** — визуализацию соседей в HNSW-графе.

---

## 3. Console — полноценный vector search

**Путь:** http://localhost:6333/dashboard#/console

Выберите HTTP-метод, вставьте путь и JSON, нажмите **Send**.

### A) Similarity по ID точки (как Find Similar)

```
POST collections/knowledge_base/points/query
```

```json
{
  "query": "00675b96-6a85-587e-a1ed-3a868e08c02a",
  "using": "dense",
  "limit": 5,
  "with_payload": true
}
```

> Для named vectors всегда указывайте `"using": "dense"`. Без этого Qdrant может вернуть ошибку.

### B) С фильтром по audience (как в RAG)

```json
{
  "query": "00675b96-6a85-587e-a1ed-3a868e08c02a",
  "using": "dense",
  "filter": {
    "must": [
      { "key": "audience", "match": { "value": "b2b" } }
    ]
  },
  "limit": 5,
  "with_payload": true
}
```

Допустимые значения `audience`: `b2b`, `b2c` (см. индексированные документы в `data/`).

### C) Hybrid search (dense + sparse, RRF)

Dashboard **не embed'ит текст** — нужны готовые векторы. Формат как в backend (`qdrant_store.py`):

```json
{
  "prefetch": [
    {
      "query": [0.01, -0.02],
      "using": "dense",
      "limit": 20
    },
    {
      "query": {
        "indices": [101, 2042, 5501],
        "values": [0.8, 0.5, 0.3]
      },
      "using": "sparse",
      "limit": 20
    }
  ],
  "query": { "fusion": "rrf" },
  "limit": 5,
  "with_payload": true
}
```

В `dense.query` подставьте массив из **1536** float (embedding запроса). Для sparse — `indices` и `values` из sparse-encoder.

### D) Scroll — просмотр точек без поиска

```
POST collections/knowledge_base/points/scroll
```

```json
{
  "limit": 10,
  "with_payload": true,
  "with_vector": false
}
```

---

## 4. Graph и Visualize

| Вкладка | URL | Назначение |
|---|---|---|
| **Graph** | `#/collections/knowledge_base/graph` | граф соседей от выбранной точки |
| **Visualize** | `#/collections/knowledge_base/visualize` | 2D-проекция (t-SNE / UMAP / PCA) |
| **Info** | `#/collections/knowledge_base` | статус, `points_count`, конфиг коллекции |

Это инструменты исследования данных, не production search.

---

## Поиск по тексту запроса (semantic)

Dashboard **не вызывает embedding-модель**. Произвольную фразу («Deep Agents курс») нельзя искать напрямую в UI без готового вектора.

Используйте backend:

```bash
make check-rag-search
```

или:

```bash
cd backend
uv run python scripts/check_rag_search.py --query "Deep Agents курс для разработчиков"
```

Скрипт embed'ит запрос через OpenRouter и вызывает `search_knowledge_base` против Qdrant.

---

## Маршруты Dashboard (шпаргалка)

| URL | Панель |
|---|---|
| `/dashboard#/` | Список коллекций |
| `/dashboard#/console` | REST playground |
| `/dashboard#/collections/knowledge_base` | Детали коллекции, Points |
| `/dashboard#/collections/knowledge_base/graph` | Similarity graph |
| `/dashboard#/collections/knowledge_base/visualize` | 2D scatter |
| `/dashboard#/tutorial` | Интерактивный tutorial |

---

## Что где использовать

```
Нужно найти по тексту запроса     →  backend / make check-rag-search
Нужно посмотреть chunk по source  →  Points + фильтр payload
Нужно «похожие на этот chunk»     →  Find Similar / Console query by id
Нужно отладить hybrid RRF         →  Console prefetch + fusion
```

---

## Связанные файлы проекта

| Файл | Описание |
|---|---|
| `backend/app/rag/qdrant_store.py` | upsert, hybrid search, audience filter |
| `backend/app/integrations/qdrant_url.py` | URL и health-check (WSL/Docker) |
| `backend/scripts/check_rag_search.py` | smoke search против live Qdrant |
| `.env.example` | `QDRANT_URL`, `QDRANT_COLLECTION`, `QDRANT_API_KEY` |
| `docker-compose.yml` | сервис `qdrant`, порты 6333/6334 |
| `Docs/sprints/sprint-05-vector-db/README.md` | спринт vector-db |

---

## Troubleshooting

**Dashboard не открывается на Windows + Docker в WSL**

Проверьте `QDRANT_URL` в `.env`. На Windows с Docker в WSL может понадобиться IP WSL вместо `localhost` — см. `backend/app/integrations/qdrant_url.py`.

**Коллекция пустая**

```bash
make index
```

**Console: Format error in JSON**

Проверьте валидность JSON (кавычки у ключей, без trailing comma). В PowerShell удобнее Console в браузере, чем `curl` с телом запроса.

**Hybrid не работает в Console**

Убедитесь, что в коллекции есть оба вектора (`dense` + `sparse`) и `HYBRID_SEARCH_ENABLED=true` при индексации.
