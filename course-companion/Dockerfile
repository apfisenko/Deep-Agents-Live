# Один Python-образ на ОБА сервиса (companion и checker): кодовая база общая,
# различаются только команда запуска (--config + порт) — см. docker-compose.yml.
#
# Build context — корень монорепо (..), чтобы подтянуть ../ai-homework-mentor
# как editable path-зависимость без vendor-копии.
#
# Честная пометка: внутри крутится `langgraph dev` — dev-сервер с state
# в памяти. Для учебного стенда ок, для прода — нет (см. README).

FROM python:3.11-slim

# git — для проверки сдач по GitHub-URL (пайплайн ментора клонирует репозиторий)
RUN apt-get update \
    && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:0.11 /uv /uvx /usr/local/bin/

WORKDIR /app/course-companion
ENV UV_LINK_MODE=copy UV_COMPILE_BYTECODE=1 UV_HTTP_TIMEOUT=300 UV_NO_BUILD_ISOLATION=1

# Слой зависимостей: pyproject + lock + mentor (editable path ../ai-homework-mentor)
COPY course-companion/pyproject.toml course-companion/uv.lock ./
COPY ai-homework-mentor /app/ai-homework-mentor

# forbiddenfruit (transitive via langgraph-cli) собирается из setup.py без declared build-deps.
# setuptools/wheel ставим в .venv до sync, иначе uv не находит их при --no-build-isolation.
RUN uv venv \
    && uv pip install setuptools wheel \
    && uv sync --frozen --no-install-project --no-build-isolation

# Код + конфиги Agent Server
COPY course-companion/src ./src
COPY course-companion/data ./data
COPY course-companion/langgraph.json \
     course-companion/langgraph.companion.json \
     course-companion/langgraph.checker.json \
     course-companion/README.md \
     ./

RUN uv sync --frozen --no-build-isolation

# Команду задаёт docker-compose (свой --config и порт на сервис).
# `--host 0.0.0.0` обязателен: по умолчанию langgraph dev слушает 127.0.0.1
# и снаружи контейнера невидим.
CMD ["uv", "run", "langgraph", "dev", "--host", "0.0.0.0", "--no-reload", "--no-browser", "--n-jobs-per-worker", "10"]
