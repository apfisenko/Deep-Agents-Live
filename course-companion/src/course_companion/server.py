"""Точка экспорта для Agent Server (см. langgraph.json).

Тот же build_graph, что и в CLI. Отличие — server=True: без локального
checkpointer (threads/checkpoints ведёт платформа).

Запуск (co-deployed, ступени 1–2):
    uv run langgraph dev --no-reload --n-jobs-per-worker 10

Распил (ступень 3, Sprint 12):
    uv run langgraph dev --config langgraph.checker.json --port 2025 \\
        --no-reload --n-jobs-per-worker 10
    CHECKER_URL=http://localhost:2025 uv run langgraph dev \\
        --config langgraph.companion.json --no-reload --n-jobs-per-worker 10

`--no-reload` обязателен: проверка ДЗ пишет в .mentor-workspace/, hot reload
dev-сервера следит за проектом и перезапускает процесс посреди рана.
"""

from course_companion.graph.graph import build_graph

graph = build_graph(server=True)
