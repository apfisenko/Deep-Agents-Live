.PHONY: help install sync lint format test ci check check-bot check-bot-verbose \
	check-backend check-backend-verbose check-self check-self-verbose \
	check-docker check-docker-verbose chat

help: ## Показать цели
	@grep -E '^[a-zA-Z0-9_.-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-22s\033[0m %s\n", $$1, $$2}'

install: sync ## Установить зависимости

sync: ## uv sync
	uv sync --all-groups

lint: ## ruff check
	uv run ruff check .

format: ## ruff format
	uv run ruff format .

test: ## pytest
	uv run pytest -q

ci: lint test ## lint + test

chat: ## S00: простой ответ LLM
	uv run mentor check "hello" --chat-only --verbose

check-bot: ## Проверить bot/ (компактный режим)
	uv run mentor check ../bot --topic "Python Telegram bot"

check-bot-verbose: ## Проверить bot/ (расширенный режим)
	uv run mentor check ../bot --topic "Python Telegram bot" --verbose

check-backend: ## Проверить backend/ (компактный режим)
	uv run mentor check ../backend --topic "FastAPI REST API"

check-backend-verbose: ## Проверить backend/ (расширенный режим)
	uv run mentor check ../backend --topic "FastAPI REST API" --verbose

check-docker: ## Проверить devops/ Docker (компактный)
	uv run mentor check ../devops --topic "Docker compose"

check-docker-verbose: ## Проверить devops/ Docker (verbose)
	uv run mentor check ../devops --topic "Docker compose" --verbose

check-self: ## Dogfooding: DeepAgents rubric на себе
	uv run mentor check . --topic "DeepAgents homework mentor"

check-self-verbose: ## Dogfooding verbose + report.md
	uv run mentor check . --topic "DeepAgents homework mentor" --verbose

check: check-bot-verbose ## Алиас: полная проверка bot/
