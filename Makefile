.PHONY: help dev dev-backend dev-frontend dev-bot lint format typecheck test test-backend test-frontend test-bot \
	up down ps status logs compose docker migrate migrate-new ci compose-dev \
	check-health check-reindex check-chat check-chat-stream check-langfuse check-telegram check-api \
	chat-telegram chat-stream

BACKEND_DIR := backend
FRONTEND_DIR := frontend
BOT_DIR := frontend/bot
REPO_ROOT := $(CURDIR)
WSL_REPO := $(shell wslpath -a '$(REPO_ROOT)' 2>/dev/null || echo '/mnt/c/FISENKO/AI/Deep-Agents-Live')
DOCKER_WSL = wsl -e bash -lc "cd '$(WSL_REPO)' && $(1)"

ARGS ?=
SVC ?=
TAIL ?= 50
CHAT_MESSAGE ?= Какой курс для новичка?

help:
	@echo "Deep-Agents-Live - available targets:"
	@echo "  dev            - backend + frontend + bot (3 terminals / make.ps1)"
	@echo "  dev-backend    - Agent Core (uvicorn :8000)"
	@echo "  dev-frontend   - Next.js widget (sprint-03)"
	@echo "  dev-bot        - Telegram bot (sprint-04)"
	@echo "  lint           - ruff + eslint"
	@echo "  format         - ruff format backend"
	@echo "  typecheck      - mypy + tsc"
	@echo "  test           - backend + frontend tests"
	@echo "  test-backend   - pytest backend"
	@echo "  test-frontend  - vitest frontend"
	@echo "  test-bot       - pytest bot"
	@echo "  up             - docker compose up -d (WSL)"
	@echo "  down           - docker compose down (WSL)"
	@echo "  ps / status    - docker compose ps (WSL)"
	@echo "  logs           - docker compose logs (SVC=, TAIL=50)"
	@echo "  compose        - docker compose <ARGS>  e.g. make compose ARGS=\"logs -f langfuse-web\""
	@echo "  docker         - docker <ARGS>           e.g. make docker ARGS=\"ps -a\""
	@echo "  ci             - lint + typecheck + test"
	@echo "  compose-dev    - full stack in Docker (profile full)"
	@echo "  check-health   - GET /health (backend must be running)"
	@echo "  check-reindex  - POST /admin/reindex"
	@echo "  check-chat     - POST /api/v1/chat (telegram)"
	@echo "  check-chat-stream - POST /api/v1/chat/stream (SSE)"
	@echo "  check-langfuse - Langfuse /api/public/health"
	@echo "  check-telegram - TCP/getMe to api.telegram.org (VPN/proxy)"
	@echo "  check-api      - all checks above"
	@echo "  chat-telegram  - POST /api/v1/chat (telegram JSON, raw output)"
	@echo "  chat-stream    - POST /api/v1/chat/stream (web SSE, raw output)"

dev:
	@echo "Run: make dev-backend & make dev-frontend & make dev-bot (3 terminals)"

dev-backend:
	cd $(BACKEND_DIR) && uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-frontend:
	cd $(FRONTEND_DIR) && pnpm dev

dev-bot:
	cd $(BOT_DIR) && uv run python main.py

lint:
	cd $(BACKEND_DIR) && uv run ruff check app tests
	cd $(FRONTEND_DIR) && pnpm lint
	cd $(BOT_DIR) && uv run ruff check .

format:
	cd $(BACKEND_DIR) && uv run ruff format app tests

typecheck:
	cd $(BACKEND_DIR) && uv run mypy app
	cd $(FRONTEND_DIR) && pnpm typecheck
	cd $(BOT_DIR) && uv run mypy .

test: test-backend test-frontend test-bot

test-backend:
	cd $(BACKEND_DIR) && uv run pytest

test-frontend:
	cd $(FRONTEND_DIR) && pnpm test

test-bot:
	cd $(BOT_DIR) && uv run pytest

up:
	$(call DOCKER_WSL,docker compose up -d)

down:
	$(call DOCKER_WSL,docker compose down)

ps status:
	$(call DOCKER_WSL,docker compose ps)

logs:
	$(call DOCKER_WSL,docker compose logs $(SVC) --tail $(TAIL))

compose:
	$(call DOCKER_WSL,docker compose $(ARGS))

docker:
	$(call DOCKER_WSL,docker $(ARGS))

migrate:
	@echo "Not implemented - Postgres is out of MVP scope (ADR-0002)"
	@exit 1

migrate-new:
	@echo "Not implemented - Postgres is out of MVP scope (ADR-0002)"
	@exit 1

ci: lint typecheck test

compose-dev:
	$(call DOCKER_WSL,docker compose --profile full up -d --build)

compose-down:
	$(call DOCKER_WSL,docker compose --profile full down)

check-health:
	cd $(BACKEND_DIR) && uv run python scripts/check_api.py health

check-reindex:
	cd $(BACKEND_DIR) && uv run python scripts/check_api.py reindex

check-chat:
	cd $(BACKEND_DIR) && uv run python scripts/check_api.py chat

check-chat-stream:
	cd $(BACKEND_DIR) && uv run python scripts/check_api.py chat-stream

check-langfuse:
	cd $(BACKEND_DIR) && uv run python scripts/check_api.py langfuse

check-telegram:
	cd $(BOT_DIR) && uv run python -m scripts.check_telegram

check-api:
	cd $(BACKEND_DIR) && uv run python scripts/check_api.py api

chat-telegram:
	cd $(BACKEND_DIR) && CHAT_MESSAGE='$(CHAT_MESSAGE)' uv run python scripts/request_chat.py telegram

chat-stream:
	cd $(BACKEND_DIR) && CHAT_MESSAGE='$(CHAT_MESSAGE)' uv run python scripts/request_chat.py stream
