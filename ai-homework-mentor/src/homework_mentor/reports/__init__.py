"""Run and compare reports (S8)."""

from homework_mentor.reports.builder import build_failed_run_report, build_run_report
from homework_mentor.reports.compare import (
    compare_modes_path,
    render_compare_modes_markdown,
    write_compare_modes_report,
)
from homework_mentor.reports.models import (
    ReviewerTokenRow,
    RunReport,
    RunReportParams,
    RunReportTiming,
    RunReportTotals,
)
from homework_mentor.reports.review_report import (
    build_review_report_markdown,
    render_partial_review_report_markdown,
    render_review_report_markdown,
    review_report_path,
    write_partial_review_report,
    write_review_report,
)
from homework_mentor.reports.writer import (
    render_run_report_markdown,
    run_report_path,
    write_run_report,
)

__all__ = [
    "ReviewerTokenRow",
    "RunReport",
    "RunReportParams",
    "RunReportTiming",
    "RunReportTotals",
    "build_failed_run_report",
    "build_review_report_markdown",
    "build_run_report",
    "compare_modes_path",
    "render_compare_modes_markdown",
    "render_partial_review_report_markdown",
    "render_review_report_markdown",
    "render_run_report_markdown",
    "review_report_path",
    "run_report_path",
    "write_compare_modes_report",
    "write_partial_review_report",
    "write_review_report",
    "write_run_report",
]
