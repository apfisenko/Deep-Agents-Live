# Entity resolution — GraphRAG catalog (sprint-06 task 05)

> Дата: 2026-07-01  
> Источник: [analysis.md](../../Docs/sprints/sprint-06-graphrag/analysis.md) §5, [schema.md](../../Docs/sprints/sprint-06-graphrag/schema.md)

---

## Course level

| Кандидаты | Решение | Канон |
|-----------|---------|-------|
| `ai-driven-fullstack.md` + `aidd-program.md` | Один узел `:Course`; legacy-файл только в `sourcePaths[]` | `slug: ai-driven-fullstack` |
| `deep-agents-advanced` vs `products.json` Deep Agents | Legacy SKU **не** в seed; только ступень 4 | `slug: deep-agents-advanced`, 44 990 ₽ |
| `llm-start`, `deep-agents` (products.json) | **Exclude** из комбо-графа | — |

**Механизм:** seed.cypher + `entity_resolver.guard_course_duplicates()` + APOC `mergeNodes` при stray Course после extraction.

---

## Theme level

| Кандидаты | Канон `canonicalName` | Алиасы (→ merge) |
|-----------|----------------------|------------------|
| RAG / Retrieval-Augmented Generation / Naive RAG | **RAG** | Retrieval-Augmented Generation, Naive RAG |
| LangSmith / LangFuse | **Observability** | LangSmith, LangFuse, Langfuse |
| AI-driven / AIDD / Fullstack AI-driven | **AI-driven методология** | AIDD, AI-driven подход |
| ChromaDB / Qdrant / Vector DB | **Vector DB** | ChromaDB, Qdrant |
| GraphRAG / Graph DB / Knowledge Graph | **GraphRAG** | Graph DB, Knowledge Graph |
| MCP / Model Context Protocol | **MCP** | Model Context Protocol |
| Advanced RAG / Agentic RAG | **Advanced RAG** | Agentic RAG (отдельно от RAG) |

**Механизм:** `data/graph/theme_aliases.yaml` → Cypher `apoc.refactor.mergeNodes` → `FuzzyMatchResolver` (threshold 0.88) для остаточных пар.

**Не merge:** `RAG` и `GraphRAG` — разные узлы (eval M2).

---

## Числовые нестыковки (документировано, seed — канон)

| Поле | Канон в seed | Альтернатива в корпусе |
|------|--------------|------------------------|
| Сумма ступеней комбо | **139 960 ₽** | 134 960 ₽ (таблица в combo.md) |
| Цена комбо | **59 990 ₽** | — |
| Deep Agents | **44 990 ₽** | 99 000 ₽ (products.json) |
| Fullstack занятий | **10** | 12 (aidd-program.md) |

---

## Extraction constraints

- **Allowed nodes (LLM):** `Course`, `Theme` only  
- **Allowed rels:** `COVERS`, `REQUIRES` only  
- **Library:** `neo4j-graphrag` SimpleKGPipeline (не LLMGraphTransformer)  
- **Env:** `GRAPH_EXTRACT_MODEL`, `GRAPH_EXTRACT_STRICT=true`
