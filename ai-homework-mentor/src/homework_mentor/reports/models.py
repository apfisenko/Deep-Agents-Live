"""Models for a single-run metrics report (S8)."""

from __future__ import annotations

from pydantic import BaseModel, Field

from homework_mentor.config import ReviewMode  # noqa: TC001 — used in pydantic fields
from homework_mentor.context.models import ContextMetricEvent  # noqa: TC001


class RunReportParams(BaseModel):
    """Параметры, с которыми запускалась проверка."""

    review_mode: ReviewMode
    model: str
    topic: str | None = None
    source_type: str | None = None
    source_value: str | None = None
    verbose: bool = False
    version: str = "0.1.0"
    session_id: str | None = None
    workspace: str | None = None
    openrouter_api_base: str | None = None
    window_tokens: int | None = None
    summarize_threshold_tokens: int | None = None
    offload_threshold_tokens: int | None = None
    summarize_enabled: bool | None = None
    compact_enabled: bool | None = None


class RunReportTotals(BaseModel):
    """Итоговые метрики прогона."""

    max_parent_tokens: int = Field(ge=0)
    final_parent_tokens: int = Field(ge=0)
    total_tokens_estimate: int = Field(ge=0)
    summarize_count: int = Field(ge=0, default=0)
    offload_count: int = Field(ge=0, default=0)
    compact_count: int = Field(ge=0, default=0)
    handoffs_count: int = Field(ge=0, default=0)
    notes_count: int = Field(ge=0, default=0)
    reviewer_tokens_estimate: int = Field(ge=0, default=0)


class ReviewerTokenRow(BaseModel):
    """Токены одного окна reviewer-субагента."""

    aspect: str
    subagent_name: str
    max_tokens: int = Field(ge=0, default=0)
    total_tokens_estimate: int = Field(ge=0, default=0)
    model_calls: int = Field(ge=0, default=0)
    wall_ms: int | None = None
    source: str = "estimate"


class RunReportTiming(BaseModel):
    """Время выполнения."""

    wall_ms: int = Field(ge=0)
    handoffs_ms: int | None = None


class RunReport(BaseModel):
    """Полный отчёт одного прогона."""

    params: RunReportParams
    context_trace: list[ContextMetricEvent] = Field(default_factory=list)
    reviewer_windows: list[ReviewerTokenRow] = Field(default_factory=list)
    totals: RunReportTotals
    timing: RunReportTiming
    status: str = "ok"
