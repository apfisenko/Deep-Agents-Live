FROM python:3.11-slim-bookworm AS builder

WORKDIR /build
COPY backend/pyproject.toml backend/uv.lock ./
RUN pip install --no-cache-dir uv \
    && uv sync --frozen --no-dev

FROM python:3.11-slim-bookworm AS runtime

WORKDIR /app
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1

COPY --from=builder /build/.venv /app/.venv
COPY backend/app ./app

EXPOSE 8000

HEALTHCHECK --interval=10s --timeout=5s --retries=5 --start-period=30s \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health')"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
