# Dataset — LLMStart Agent (eval v0.1)

## Финальный артефакт

**[`v0.1.jsonl`](./v0.1.jsonl)** — 27 записей, типы **A** (faq-format), **B** (product-fit), **C** (segment-route).

Формат строки:

```json
{
  "id": "ext-001",
  "input": { "message": "...", "channel": "web" },
  "expected_output": "...",
  "metadata": {
    "dataset_type": "faq-format",
    "product_id": "ai-agents-combo",
    "segment": "b2c",
    "facts": ["..."]
  }
}
```

## Источники

| Файл | Записей |
|------|---------|
| `extracted/extracted.jsonl` | 15 (реальные чаты `source/`) |
| `synthetic/synthetic.jsonl` | 12 (`data/b2c/programs/`) |

Пересборка: `python3 dataset/scripts/merge_dataset.py`

## Langfuse (локально, :3300)

| Датасет | Тип | Папка | Items |
|---------|-----|-------|-------|
| `llmstart-type-a-v0.1` | A faq-format | [`langfuse/type-a-v0.1/`](./langfuse/type-a-v0.1/) | 14 |
| `llmstart-type-b-v0.1` | B product-fit | [`langfuse/type-b-v0.1/`](./langfuse/type-b-v0.1/) | 10 |
| `llmstart-type-c-v0.1` | C segment-route | [`langfuse/type-c-v0.1/`](./langfuse/type-c-v0.1/) | 3 |

Загрузка всех: `python3 dataset/langfuse/upload_all.py` (ключи из `.env`).

## Документация процесса

- [dataset-plan.md](./dataset-plan.md) — план и DoD  
- [summary.md](./summary.md) — итог задачи  
- [analysis-report.md](./analysis-report.md) — анализ 5 чатов  
