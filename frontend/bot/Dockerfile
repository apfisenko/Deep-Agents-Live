FROM python:3.11-slim-bookworm AS builder

WORKDIR /build
COPY frontend/bot/pyproject.toml frontend/bot/uv.lock ./
RUN pip install --no-cache-dir uv \
    && uv sync --frozen --no-dev

FROM python:3.11-slim-bookworm AS runtime

WORKDIR /app
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1

COPY --from=builder /build/.venv /app/.venv
COPY frontend/bot/ ./

CMD ["python", "main.py"]
