"""Точка экспорта для Agent Server (см. langgraph.json).

Весь «переезд в сервис» — этот файл плюс ~10 строк конфига: код агента
не меняется, тот же build_graph, что и в CLI. Единственное отличие —
без локального чекпоинтера: threads/checkpoints ведёт платформа.

Запуск (co-deployed: companion + checker на одном сервере :2024):
    uv run langgraph dev --no-reload --n-jobs-per-worker 10

Распил (чекер на своём сервере :2025, companion ходит к нему по HTTP;
у каждой деплой-единицы СВОЙ конфиг — граница сервисов = граница деплоя):
    uv run langgraph dev --config langgraph.checker.json --port 2025 \
        --no-reload --n-jobs-per-worker 10
    CHECKER_URL=http://localhost:2025 uv run langgraph dev \
        --config langgraph.companion.json --no-reload --n-jobs-per-worker 10

`--no-reload` обязателен: companion пишет рабочие файлы агента в папку
проекта (.companion-workspace/, vendor/.../.mentor-workspace/), а hot
reload dev-сервера следит за ней же — на длинной проверке домашки сервер
перезапускал сам себя посреди рана и проверка уходила в вечный retry.

`--n-jobs-per-worker 10` обязателен для фоновых проверок: реальный дефолт
dev-сервера — ОДИН воркер-слот (help врёт про 10), и активный ран чекера
съедает его целиком — «асинхронная» проверка снова блокирует чат.
"""

from companion.graph import build_graph

graph = build_graph(server=True)
