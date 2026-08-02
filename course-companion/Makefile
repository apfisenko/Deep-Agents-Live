.PHONY: dev test lint format typecheck ci

dev:
	uv sync --all-groups

test:
	uv run pytest tests/ -v

lint:
	uv run ruff check src/ tests/

format:
	uv run ruff format src/ tests/

typecheck:
	uv run mypy src/

ci: lint typecheck test
