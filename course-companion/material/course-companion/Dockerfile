# Один Python-образ на ОБА сервиса (companion и checker): кодовая база у них
# общая, различаются только команда запуска (--config + порт) — см.
# docker-compose.yml. Это сознательное решение: граница сервисов — граница
# деплоя (свой контейнер/конфиг/жизненный цикл), а не граница репозитория.
#
# Честная пометка: внутри крутится `langgraph dev` — dev-сервер с state
# в памяти. Для учебного стенда это ок, для прода — нет (см. README).

FROM python:3.12-slim

# git — для проверки сдач по GitHub-URL (пайплайн ментора клонирует репозиторий)
RUN apt-get update \
    && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:0.11 /uv /uvx /usr/local/bin/

WORKDIR /app
ENV UV_LINK_MODE=copy UV_COMPILE_BYTECODE=1

# Слой зависимостей: pyproject + lock + vendor (editable path-зависимость),
# сами пакеты проекта ставим позже — правки кода не инвалидируют этот слой.
COPY pyproject.toml uv.lock ./
COPY vendor ./vendor
RUN uv sync --frozen --no-install-project

# Код обоих пакетов + конфиги Agent Server
COPY companion ./companion
COPY checker_service ./checker_service
COPY data ./data
COPY langgraph.json langgraph.companion.json langgraph.checker.json README.md ./
RUN uv sync --frozen

# Команду задаёт docker-compose (свой --config и порт на сервис).
# `--host 0.0.0.0` обязателен: по умолчанию langgraph dev слушает 127.0.0.1
# и снаружи контейнера невидим.
CMD ["uv", "run", "langgraph", "dev", "--host", "0.0.0.0", "--no-reload", "--no-browser", "--n-jobs-per-worker", "10"]
