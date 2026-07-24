"""Minimal FastAPI app fixture — not executed in review."""

from fastapi import FastAPI

from app.api.routes import router

app = FastAPI(title="fixture-api")
app.include_router(router, prefix="/api")
