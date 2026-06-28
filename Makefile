.PHONY: help dev dev-backend dev-frontend dev-bot stop-dev stop-backend stop-frontend stop-bot \
	lint format typecheck test test-backend test-frontend test-bot index \
	up down ps status logs compose docker migrate migrate-new ci compose-dev \
	check-health check-reindex check-chat check-chat-stream check-langfuse check-traces check-telegram check-api \
	check-rag-search-e2e check-rag-audience-filter \
	graph-up graph-down graph-status graph-shell graph-init-readonly \
	chat-telegram chat-stream langfuse-upload-dataset \
	eval-help eval-validate eval-build eval-sync eval-experiment eval-analyze eval-compare

BACKEND_DIR := backend
FRONTEND_DIR := frontend
BOT_DIR := frontend/bot
EVALS_DIR := evals
REPO_ROOT := $(CURDIR)
WSL_REPO := $(shell wslpath -a '$(REPO_ROOT)' 2>/dev/null || echo '/mnt/c/FISENKO/AI/Deep-Agents-Live')
DOCKER_WSL = wsl -e bash -lc "cd '$(WSL_REPO)' && $(1)"

ARGS ?=
SVC ?=
TAIL ?= 50
DATASET_JSONL ?= datasets/dataset-v1.jsonl
DATASET_NAME ?= llmstart-agent-v1

help:
	@echo "Deep-Agents-Live - available targets:"
	@echo "  dev            - backend + frontend + bot (3 terminals / make.ps1)"
	@echo "  dev-backend    - Agent Core (uvicorn :8000)"
	@echo "  dev-frontend   - Next.js widget (sprint-03)"
	@echo "  dev-bot        - Telegram bot (sprint-04)"
	@echo "  stop-dev       - stop backend + frontend + bot"
	@echo "  stop-backend   - stop uvicorn on :8000"
	@echo "  stop-frontend  - stop Next.js on :3000"
	@echo "  stop-bot       - stop Telegram bot (main.py)"
	@echo "  lint           - ruff + eslint"
	@echo "  format         - ruff format backend"
	@echo "  typecheck      - mypy + tsc"
	@echo "  test           - backend + frontend tests"
	@echo "  test-backend   - pytest backend"
	@echo "  test-frontend  - vitest frontend"
	@echo "  test-bot       - pytest bot"
	@echo "  index          - index data/ into vector DB (Qdrant); ARGS=\"--force\" to reindex all"
	@echo "  up             - docker compose up -d (WSL)"
	@echo "  down           - docker compose down (WSL)"
	@echo "  graph-up       - docker compose up -d neo4j only"
	@echo "  graph-down     - stop Neo4j container"
	@echo "  graph-status   - neo4j container status + Connection OK smoke"
	@echo "  graph-shell    - interactive cypher-shell in neo4j container"
	@echo "  graph-init-readonly - create text2cypher read-only user (devops/README.md)"
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
	@echo "  langfuse-upload-dataset - upload/reload JSONL dataset to Langfuse (DATASET_JSONL, DATASET_NAME)"
	@echo "  check-telegram - TCP/getMe to api.telegram.org (VPN/proxy)"
	@echo "  check-api      - all checks above"
	@echo "  check-rag-search-e2e - RAG search smoke (Qdrant up + make index; task 04 p.3)"
	@echo "  check-rag-audience-filter - b2b/b2c filter smoke (task 04 p.4)"
	@echo "  chat-telegram  - POST /api/v1/chat (telegram JSON, raw output)"
	@echo "  chat-stream    - POST /api/v1/chat/stream (web SSE, raw output)"
	@echo "  eval-help      - eval contour help (see evals/README.md)"
	@echo "  eval-build     - build dataset manifest YAML (DATASET=)"
	@echo "  eval-validate  - pytest + dry-run all configs/datasets"
	@echo "  eval-sync      - sync datasets to Langfuse (DATASET=)"
	@echo "  eval-experiment - run eval experiment (CONFIG=, DATASET=)"
	@echo "  eval-analyze   - error analysis (RUN=, EMIT_ITEMS=1)"
	@echo "  eval-compare   - compare runs (RUN_A=, RUN_B=)"
	@echo "  check-traces   - verify Langfuse traces for web+telegram chat"

dev:
	@echo "Run: make dev-backend & make dev-frontend & make dev-bot (3 terminals)"

stop-dev: stop-backend stop-frontend stop-bot

stop-backend:
	-@lsof -ti:8000 | xargs kill -9 2>/dev/null || true
	-@pkill -f "uvicorn app.main:app" 2>/dev/null || true

stop-frontend:
	-@lsof -ti:3000 | xargs kill -9 2>/dev/null || true
	-@pkill -f "next dev" 2>/dev/null || true

stop-bot:
	-@pkill -f "$(BOT_DIR)/.venv" 2>/dev/null || true
	-@pkill -f "uv run python main.py" 2>/dev/null || true

dev-backend: stop-backend
	cd $(BACKEND_DIR) && uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-frontend: stop-frontend
	cd $(FRONTEND_DIR) && pnpm dev

dev-bot: stop-bot
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

index:
	cd $(BACKEND_DIR) && uv run python -m app.rag.index_cli $(ARGS)

up:
	$(call DOCKER_WSL,docker compose up -d)

down:
	$(call DOCKER_WSL,docker compose down)

graph-up:
	$(call DOCKER_WSL,docker compose up -d neo4j)

graph-down:
	$(call DOCKER_WSL,docker compose stop neo4j)

graph-status:
	$(call DOCKER_WSL,docker compose ps neo4j)
	cd $(BACKEND_DIR) && uv run python scripts/check_neo4j.py status

graph-shell:
	$(call DOCKER_WSL,docker compose exec -it neo4j cypher-shell)

graph-init-readonly:
	$(call DOCKER_WSL,bash devops/neo4j/create-readonly-user.sh)

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

check-traces:
	cd $(BACKEND_DIR) && uv run python scripts/check_api.py traces

langfuse-upload-dataset:
	cd $(BACKEND_DIR) && uv run python scripts/upload_langfuse_dataset.py \
		--input ../$(DATASET_JSONL) \
		--dataset-name $(DATASET_NAME) \
		--reload

check-telegram:
	cd $(BOT_DIR) && uv run python -m scripts.check_telegram

check-api:
	cd $(BACKEND_DIR) && uv run python scripts/check_api.py api

check-rag-search-e2e:
	cd $(BACKEND_DIR) && uv run python scripts/check_rag_search.py e2e

check-rag-audience-filter:
	cd $(BACKEND_DIR) && uv run python scripts/check_rag_search.py audience-filter

chat-telegram:
	cd $(BACKEND_DIR) && CHAT_MESSAGE='$(CHAT_MESSAGE)' uv run python scripts/request_chat.py telegram

chat-stream:
	cd $(BACKEND_DIR) && CHAT_MESSAGE='$(CHAT_MESSAGE)' uv run python scripts/request_chat.py stream

eval-help eval-validate eval-build eval-sync eval-experiment eval-analyze eval-compare:
	$(MAKE) -C $(EVALS_DIR) $(subst eval-,,$@)
