# Датасет: rag-format-facts

**Группа (слой):** rag  
**Текущая версия:** v001 (`v001_2026-06-15.yaml`)  
**Формат:** YAML (E-12)

## Что проверяет

Извлечение и формулировка **фактов формата / расписания / записей / live** по конкретному B2C SKU (G1). Component-level: retrieval vs generation отдельно от e2e.

## Источник items (v001)

| Источник | Кол-во | Примечание |
|----------|--------|------------|
| `dataset/v0.1.jsonl` faq-format (ext-*) | 6 | CHAT_0014, 0020, 0110 |
| `dataset/v0.1.jsonl` faq-format (syn-*) | 8 | из `data/b2c/programs/` |
| synthetic gaps (Deep Agents schedule, Agents recordings) | 2 | syn-015, syn-016 |
| **Итого v001** | **16** | target 15–18 |

## Product coverage

6 SKU: `ai-agents-combo`, `ai-coding-intensive-cursor`, `ai-coding-agents-base`, `ai-driven-fullstack`, `deep-agents-advanced`.

## Метрики (sprint-eval-02 task 07)

Из [metrics-map.md](../../../../Docs/eval/metrics-map.md): `fact_coverage`, `context_recall`, `answer_correctness`, `task_error`.

## Зеркало Langfuse (E-16)

`rag/rag-format-facts/v001` — synced 2026-06-15.
