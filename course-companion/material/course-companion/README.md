# Course Companion

Общий диалоговый агент студента курса. **Учебный walkthrough — в [`../README.md`](../README.md).**
(Этот файл нужен hatchling'у для сборки пакета.)

Быстрый старт (нужен `.env` по образцу `.env.example`):

```bash
uv sync
uv run companion                   # интерактивный чат
uv run python -m companion.smoke   # one-shot прогон «сдал → фидбек»
uv run pytest -q                   # тесты без LLM
```
