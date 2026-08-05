# Course Companion — make-обёртки над командами запуска. `make` без цели = help.
#
# Все флаги из README (--no-reload, --n-jobs-per-worker, конфиги, env на швах)
# зашиты внутрь целей: make — удобство, не чёрный ящик. Развёрнутые сырые
# команды с пояснением флагов остаются в README по ступеням.
#
# Серверные цели (dev / checker / companion / frontend) запускают процессы
# ФОНОМ (nohup), логи пишут в .logs/, а «куда смотреть» печатают при старте —
# так вся портовая конфигурация поднимается из одного терминала. Гасить: make stop.

LOGS := .logs
# --n-jobs-per-worker: слоты воркера; про дефолт-грабли — README, ступень 2
JOBS := 10

.DEFAULT_GOAL := help
.PHONY: help dev checker companion frontend stop compose-up compose-down test lint cli webhook-demo

help: ## список целей с описаниями
	@grep -hE '^[a-zA-Z-]+:.*## ' $(MAKEFILE_LIST) | awk -F ':.*## ' '{printf "  \033[36m%-14s\033[0m %s\n", $$1, $$2}'

dev: ## co-deployed (ступени 1–2): оба графа на :2024 (langgraph.json) + веб-чат :5173, фоном
	@mkdir -p $(LOGS)
	@nohup uv run langgraph dev --no-reload --no-browser --n-jobs-per-worker $(JOBS) > $(LOGS)/server.log 2>&1 &
	@cd frontend && nohup npm run dev > ../$(LOGS)/frontend.log 2>&1 &
	@printf 'Agent Server (оба графа):  http://localhost:2024/info · лог: $(LOGS)/server.log\n'
	@printf 'веб-чат:                   http://localhost:5173 (браузером на localhost)\n'
	@printf 'готовность: curl -s localhost:2024/info · погасить: make stop\n'

checker: ## распил (ступень 3): сервер чекера :2025 (langgraph.checker.json), фоном
	@mkdir -p $(LOGS)
	@nohup uv run langgraph dev --config langgraph.checker.json --port 2025 --no-reload --no-browser --n-jobs-per-worker $(JOBS) > $(LOGS)/checker.log 2>&1 &
	@printf 'checker: http://localhost:2025/info · лог: $(LOGS)/checker.log · погасить: make stop\n'

companion: ## распил (ступень 3): сервер companion :2024, адрес чекера — через CHECKER_URL, фоном
	@mkdir -p $(LOGS)
	@CHECKER_URL=http://localhost:2025 nohup uv run langgraph dev --config langgraph.companion.json --no-reload --no-browser --n-jobs-per-worker $(JOBS) > $(LOGS)/companion.log 2>&1 &
	@printf 'companion: http://localhost:2024/info · лог: $(LOGS)/companion.log · погасить: make stop\n'

frontend: ## распил (ступень 3): веб-чат :5173, поллер целит в чекер через CHECKER_PROXY_TARGET, фоном
	@mkdir -p $(LOGS)
	@cd frontend && CHECKER_PROXY_TARGET=http://127.0.0.1:2025 nohup npm run dev > ../$(LOGS)/frontend.log 2>&1 &
	@printf 'веб-чат: http://localhost:5173 (браузером на localhost) · лог: $(LOGS)/frontend.log\n'

stop: ## погасить все портовые процессы (fuser -k по портам 2024/2025/5173)
	-@fuser -k 2024/tcp 2025/tcp 5173/tcp >/dev/null 2>&1; true
	@printf 'порты 2024/2025/5173 свободны\n'

compose-up: ## docker compose up --build -d: вся система тремя контейнерами
	docker compose up --build -d
	@printf 'веб-чат: http://localhost:5173 · companion: :2024 · checker: :2025 (agent card курлится с хоста)\n'

compose-down: ## погасить контейнеры (state dev-сервера пропадёт — он в памяти)
	docker compose down

test: ## pytest: тесты без LLM (корень + drill-модуль)
	uv run pytest -q

lint: ## ruff по нашему коду (vendor заморожен — не наш) + tsc фронта
	uv run ruff check companion checker_service tests examples
	cd frontend && npx tsc --noEmit

cli: ## интерактивный CLI-чат — нулевая точка, без сервера и Node
	uv run companion

webhook-demo: ## бонус ступени 1: background run + webhook (нужен поднятый сервер — make dev)
	@mkdir -p $(LOGS)
	@nohup uv run uvicorn examples.webhook_receiver:app --port 8080 > $(LOGS)/webhook-receiver.log 2>&1 &
	@sleep 2
	uv run python examples/run_background_webhook.py
	@sleep 1
	@printf -- '--- лог приёмника ---\n'; cat $(LOGS)/webhook-receiver.log
	-@fuser -k 8080/tcp >/dev/null 2>&1; true
