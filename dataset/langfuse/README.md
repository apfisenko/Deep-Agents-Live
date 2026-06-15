# Langfuse datasets (v0.1)

Локальный UI: http://localhost:3300 → **Datasets**

| Имя | Тип | Items |
|-----|-----|-------|
| `llmstart-type-a-v0.1` | faq-format | 14 |
| `llmstart-type-b-v0.1` | product-fit | 10 |
| `llmstart-type-c-v0.1` | segment-route | 3 |

```bash
# все три датасета
python3 dataset/langfuse/upload_all.py

# или по отдельности
python3 dataset/langfuse/type-a-v0.1/upload_to_langfuse.py
python3 dataset/langfuse/type-b-v0.1/upload_to_langfuse.py
python3 dataset/langfuse/type-c-v0.1/upload_to_langfuse.py
```

Источник items: `dataset/v0.1.jsonl` (фильтр по `metadata.dataset_type`).
