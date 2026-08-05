# Course Companion — make-обёртки. `make` без цели = help.

#

# Серверные цели запускают Agent Server + Vite фронт фоном, логи в .logs/.

# Гасить: make stop



LOGS := .logs

JOBS := 10



.DEFAULT_GOAL := help

.PHONY: help dev checker companion frontend stop compose-up compose-up-build compose-down compose-ensure compose-status test lint format typecheck ci cli webhook-demo



help: ## список целей

	@grep -hE '^[a-zA-Z-]+:.*## ' $(MAKEFILE_LIST) | awk -F ':.*## ' '{printf "  \033[36m%-14s\033[0m %s\n", $$1, $$2}'



dev: ## co-deployed (ступени 1–2): оба графа на :2024 + веб-чат :5173, фоном

	@mkdir -p $(LOGS)

	@nohup uv run langgraph dev --no-reload --no-browser --n-jobs-per-worker $(JOBS) > $(LOGS)/server.log 2>&1 &

	@cd frontend && nohup npm run dev > ../$(LOGS)/frontend.log 2>&1 &

	@printf 'Agent Server (оба графа):  http://localhost:2024/info · лог: $(LOGS)/server.log\n'

	@printf 'веб-чат:                   http://localhost:5173 · лог: $(LOGS)/frontend.log\n'

	@printf 'готовность: curl -s localhost:2024/info · погасить: make stop\n'



checker: ## распил (ступень 3): сервер чекера :2025, фоном

	@mkdir -p $(LOGS)

	@nohup uv run langgraph dev --config langgraph.checker.json --port 2025 --no-reload --no-browser --n-jobs-per-worker $(JOBS) > $(LOGS)/checker.log 2>&1 &

	@printf 'checker: http://localhost:2025/info · лог: $(LOGS)/checker.log · погасить: make stop\n'



companion: ## распил (ступень 3): companion :2024, CHECKER_URL → :2025, фоном

	@mkdir -p $(LOGS)

	@CHECKER_URL=http://localhost:2025 nohup uv run langgraph dev --config langgraph.companion.json --no-reload --no-browser --n-jobs-per-worker $(JOBS) > $(LOGS)/companion.log 2>&1 &

	@printf 'companion: http://localhost:2024/info · лог: $(LOGS)/companion.log · погасить: make stop\n'



frontend: ## распил (ступень 3): веб-чат :5173, поллер → CHECKER_PROXY_TARGET

	@mkdir -p $(LOGS)

	@cd frontend && CHECKER_PROXY_TARGET=http://127.0.0.1:2025 nohup npm run dev > ../$(LOGS)/frontend.log 2>&1 &

	@printf 'веб-чат: http://localhost:5173 · лог: $(LOGS)/frontend.log\n'



stop: ## освободить порты 2024, 2025 и 5173 (не для compose — см. compose-down)

	@if docker compose ps --status running -q 2>/dev/null | grep -q .; then \
	  printf 'Compose контейнеры активны — stop/fuser убьёт docker-proxy. Используйте: make compose-down\n'; \
	  exit 1; \
	fi
	@if ss -ltn 2>/dev/null | grep -qE ':(2024|2025|5173) '; then \
	  if ss -ltnp 2>/dev/null | grep -E ':(2024|2025|5173) ' | grep -qE 'docker|docker-proxy'; then \
	    printf 'Порты заняты docker-proxy (compose). Используйте: make compose-down\n'; exit 1; \
	  fi; \
	fi
	-@fuser -k 2024/tcp 2025/tcp 5173/tcp >/dev/null 2>&1; true

	@printf 'порты 2024/2025/5173 свободны\n'



compose-up: ## docker compose up -d: поднять/перезапустить стек

	@if docker compose ps --status running -q 2>/dev/null | grep -q .; then \
	  printf 'Compose уже running — применяем конфиг без очистки портов\n'; \
	else \
	  if ss -ltnp 2>/dev/null | grep -E ':(2024|2025|5173) ' | grep -qvE 'docker|docker-proxy'; then \
	    fuser -k 2024/tcp 2025/tcp 5173/tcp >/dev/null 2>&1 || true; \
	  fi; \
	fi
	docker compose up -d --remove-orphans

	@printf 'веб-чат: http://localhost:5173 · companion: :2024 · checker: :2025\n'
	@printf 'проверка: make compose-status\n'



compose-up-build: ## docker compose up -d --build: пересборка образов

	docker compose up -d --build --remove-orphans

	@printf 'веб-чат: http://localhost:5173 · companion: :2024 · checker: :2025\n'



compose-down: ## погасить контейнеры (state dev-сервера пропадёт — он в памяти)

	docker compose down



compose-ensure: ## поднять стек, если контейнеры не running

	@if docker compose ps --status running -q 2>/dev/null | grep -q .; then \
	  printf 'Compose уже running\n'; \
	else \
	  $(MAKE) compose-up; \
	fi
	@$(MAKE) compose-status



compose-status: ## статус контейнеров + HTTP-probe :5173/:2024/:2025

	bash scripts/compose-status.sh



cli: ## интерактивный CLI (без сервера)

	uv run companion



test: ## pytest

	uv run pytest tests/ -v



lint: ## ruff + tsc фронта

	uv run ruff check src/ tests/

	cd frontend && npx tsc --noEmit



format: ## ruff format

	uv run ruff format src/ tests/



typecheck: ## mypy

	uv run mypy src/



ci: lint typecheck test ## lint + typecheck + test



webhook-demo: ## background run + webhook (нужен make dev)

	@mkdir -p $(LOGS)

	@nohup uv run uvicorn examples.webhook_receiver:app --port 8080 > $(LOGS)/webhook-receiver.log 2>&1 &

	@sleep 2

	uv run python examples/run_background_webhook.py

	@sleep 1

	@printf -- '--- лог приёмника ---\n'; cat $(LOGS)/webhook-receiver.log

	-@fuser -k 8080/tcp >/dev/null 2>&1; true

