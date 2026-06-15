# Langfuse — датасет type A (v0.1)

| Поле | Значение |
|------|----------|
| **Имя в Langfuse** | `llmstart-type-a-v0.1` |
| **Тип** | A — `faq-format` |
| **Версия** | v0.1 |
| **Записей** | 14 (из `../v0.1.jsonl`) |
| **UI** | http://localhost:3300 → Datasets |

## Файлы

- `items.jsonl` — экспорт для Langfuse
- `upload_to_langfuse.py` — загрузка в локальный Langfuse

## Загрузка

```bash
# из корня репозитория, credentials из .env
python3 dataset/langfuse/type-a-v0.1/upload_to_langfuse.py
```
