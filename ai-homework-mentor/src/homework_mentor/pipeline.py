"""S2 session pipeline: parse → clarify | workspace + rubric + review."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal

from homework_mentor.code_fetch import (
    CodeFetchError,
    FetchResult,
    fetch_github_repository,
    fetch_local_directory,
)
from homework_mentor.config import load_runtime_settings, load_yaml_config, project_root
from homework_mentor.logging_setup import setup_logging
from homework_mentor.orchestrator.review import ReviewRunResult, build_review_message, run_review
from homework_mentor.rubric import select_rubric
from homework_mentor.submission import SourceType, Submission, parse_submission
from homework_mentor.workspace import WorkspaceSession, create_session

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

    from homework_mentor.config import RuntimeSettings
    from homework_mentor.rubric.loader import RubricSelection


@dataclass(frozen=True)
class SessionResult:
    kind: Literal["clarification", "ok"]
    submission: Submission
    fetch: FetchResult | None = None
    workspace: WorkspaceSession | None = None
    rubric: RubricSelection | None = None
    review: ReviewRunResult | None = None
    reply: str | None = None


def fetch_for_submission(
    submission: Submission,
    *,
    settings: RuntimeSettings | None = None,
    staging_dir: Path | None = None,
    fetch_local: Callable[..., FetchResult] | None = None,
    fetch_github: Callable[..., FetchResult] | None = None,
) -> FetchResult:
    yaml_cfg = settings.yaml if settings is not None else load_yaml_config()
    ignore = yaml_cfg.agent.code_fetch.ignore_names
    timeout = yaml_cfg.agent.code_fetch.clone_timeout_seconds
    staging = staging_dir or (project_root() / "workspace" / "code")

    if submission.source_type is SourceType.LOCAL_PATH:
        if not submission.source_value:
            msg = "Local path source is missing"
            raise CodeFetchError(msg)
        local_fn = fetch_local or fetch_local_directory
        return local_fn(
            submission.source_value,
            staging_dir=staging,
            ignore_names=ignore,
        )

    if submission.source_type is SourceType.GITHUB_URL:
        if not submission.source_value:
            msg = "GitHub URL source is missing"
            raise CodeFetchError(msg)
        github_fn = fetch_github or fetch_github_repository
        return github_fn(
            submission.source_value,
            staging_dir=staging,
            timeout_seconds=timeout,
        )

    msg = "Cannot fetch code: source is unknown"
    raise CodeFetchError(msg)


def run_homework_session(  # noqa: PLR0913 — injectable deps for tests
    *,
    raw_text: str,
    explicit_path: str | Path | None = None,
    settings: RuntimeSettings | None = None,
    topic_extractor: Callable[[str], str | None] | None = None,
    fetch_local: Callable[..., FetchResult] | None = None,
    fetch_github: Callable[..., FetchResult] | None = None,
    review_runner: Callable[..., ReviewRunResult] | None = None,
    session_factory: Callable[[], WorkspaceSession] | None = None,
    use_llm_topic: bool = True,
) -> SessionResult:
    """Parse input, clarify or fetch into workspace, then run single-agent review."""
    runtime = settings
    if runtime is None and review_runner is None:
        runtime = load_runtime_settings()

    log_level = runtime.log_level if runtime is not None else "INFO"
    logger = setup_logging(level=log_level)

    parse_settings = runtime if (topic_extractor is None and use_llm_topic) else None
    submission = parse_submission(
        raw_text,
        explicit_path=explicit_path,
        topic_extractor=topic_extractor,
        settings=parse_settings,
    )
    logger.info(
        "parse done source_type=%s needs_clarification=%s topic_set=%s",
        submission.source_type.value,
        submission.needs_clarification,
        bool(submission.topic),
    )

    if submission.needs_clarification:
        logger.info("clarification required; skip fetch")
        return SessionResult(kind="clarification", submission=submission)

    session = (session_factory or create_session)()
    session.write_submission(submission)

    try:
        fetch = fetch_for_submission(
            submission,
            settings=runtime,
            staging_dir=session.code_dir,
            fetch_local=fetch_local,
            fetch_github=fetch_github,
        )
    except CodeFetchError:
        logger.exception("fetch failed")
        raise

    rubric = select_rubric(submission.topic, session=session)
    logger.info(
        "fetch ok source=%s files=%s workspace=%s rubric=%s",
        fetch.source,
        fetch.file_count,
        session.root,
        rubric.template_name,
    )

    review_message = build_review_message(
        submission=submission,
        fetch=fetch,
        rubric=rubric,
        prompts=(
            runtime.yaml.review_prompts
            if runtime is not None
            else load_yaml_config().review_prompts
        ),
    )
    if review_runner is not None:
        review = review_runner(message=review_message, session=session, settings=runtime)
    else:
        review = run_review(message=review_message, session=session, settings=runtime)

    return SessionResult(
        kind="ok",
        submission=submission,
        fetch=fetch,
        workspace=session,
        rubric=rubric,
        review=review,
        reply=review.reply,
    )
