"""S2-S6 session pipeline: parse -> clarify | workspace + review + synthesis."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal

from homework_mentor.code_fetch import (
    CodeFetchError,
    FetchResult,
    fetch_github_repository,
    fetch_local_directory,
)
from homework_mentor.config import (
    DEFAULT_REVIEW_MODE,
    ReviewMode,
    load_runtime_settings,
    load_yaml_config,
    project_root,
)
from homework_mentor.logging_setup import setup_logging
from homework_mentor.orchestrator.agent import ReviewError
from homework_mentor.orchestrator.review import ReviewRunResult, build_review_message, run_review
from homework_mentor.reviewers.notes import (
    materialize_review_notes_from_handoffs,
    materialize_single_agent_note_from_reply,
)
from homework_mentor.reviewers.registry import load_reviewer_specs
from homework_mentor.rubric import select_rubric
from homework_mentor.skills import resolve_skills
from homework_mentor.submission import SourceType, Submission, parse_submission
from homework_mentor.synthesis.pipeline import discover_review_note_names, run_synthesis
from homework_mentor.workspace import WorkspaceSession, create_session

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

    from homework_mentor.config import RuntimeSettings
    from homework_mentor.rubric.loader import RubricSelection
    from homework_mentor.skills.models import SkillsSelection
    from homework_mentor.synthesis.pipeline import SynthesisResult


@dataclass(frozen=True)
class SessionResult:
    kind: Literal["clarification", "ok"]
    submission: Submission
    fetch: FetchResult | None = None
    workspace: WorkspaceSession | None = None
    rubric: RubricSelection | None = None
    skills: SkillsSelection | None = None
    review: ReviewRunResult | None = None
    reply: str | None = None
    review_mode: ReviewMode = DEFAULT_REVIEW_MODE


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


def _attach_synthesis(  # noqa: PLR0913 — session wiring needs explicit deps
    review: ReviewRunResult,
    *,
    session: WorkspaceSession,
    submission: Submission,
    rubric: RubricSelection,
    settings: RuntimeSettings | None,
    synthesis_runner: Callable[..., SynthesisResult] | None,
    review_mode: ReviewMode = DEFAULT_REVIEW_MODE,
) -> ReviewRunResult:
    if review.final_feedback is not None and review.fix_plan is not None:
        return review

    if review_mode == "subagents":
        materialize_review_notes_from_handoffs(session, review.subagent_handoffs)
    else:
        materialize_single_agent_note_from_reply(session, review.reply)

    yaml_cfg = settings.yaml if settings is not None else load_yaml_config()
    notes = discover_review_note_names(session.notes_dir)
    if synthesis_runner is None and not notes:
        return review

    try:
        if synthesis_runner is not None:
            synth = synthesis_runner(
                session=session,
                submission=submission,
                rubric=rubric.rubric,
                reflection_prompts=yaml_cfg.synthesis_reflection_prompts,
                final_prompts=yaml_cfg.synthesis_final_prompts,
                settings=settings,
                handoffs=review.subagent_handoffs,
            )
        else:
            synth = run_synthesis(
                session=session,
                submission=submission,
                rubric=rubric.rubric,
                reflection_prompts=yaml_cfg.synthesis_reflection_prompts,
                final_prompts=yaml_cfg.synthesis_final_prompts,
                settings=settings,
                handoffs=review.subagent_handoffs,
            )
    except Exception as exc:
        raise ReviewError(str(exc), session_id=session.session_id) from exc

    review.final_feedback = synth.feedback
    review.fix_plan = synth.plan
    review.reflection = synth.reflection
    return review


def run_homework_session(  # noqa: PLR0913 — injectable deps for tests
    *,
    raw_text: str,
    explicit_path: str | Path | None = None,
    settings: RuntimeSettings | None = None,
    topic_extractor: Callable[[str], str | None] | None = None,
    fetch_local: Callable[..., FetchResult] | None = None,
    fetch_github: Callable[..., FetchResult] | None = None,
    review_runner: Callable[..., ReviewRunResult] | None = None,
    synthesis_runner: Callable[..., SynthesisResult] | None = None,
    session_factory: Callable[[], WorkspaceSession] | None = None,
    use_llm_topic: bool = True,
    review_mode: ReviewMode = DEFAULT_REVIEW_MODE,
) -> SessionResult:
    """Parse input, clarify or fetch into workspace, review, then synthesize."""
    runtime = settings
    if runtime is None and review_runner is None:
        runtime = load_runtime_settings()

    log_level = runtime.log_level if runtime is not None else "INFO"
    logger = setup_logging(level=log_level)
    logger.info("session review_mode=%s", review_mode)

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
        return SessionResult(
            kind="clarification",
            submission=submission,
            review_mode=review_mode,
        )

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
    skills = resolve_skills(
        submission.topic,
        code_manifest=fetch.files,
        session=session,
    )
    skills_by_aspect = {
        spec.aspect: skills.for_aspect(spec.aspect) for spec in load_reviewer_specs()
    }
    logger.info(
        "fetch ok source=%s files=%s workspace=%s rubric=%s skills=%s api=%s",
        fetch.source,
        fetch.file_count,
        session.root,
        rubric.template_name,
        [ref.id for ref in skills.all_refs()],
        skills.api_detected,
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
        skills=skills,
        review_mode=review_mode,
    )
    if review_runner is not None:
        try:
            review = review_runner(
                message=review_message,
                session=session,
                settings=runtime,
                skills=skills,
                skills_by_aspect=skills_by_aspect,
                review_mode=review_mode,
            )
        except TypeError:
            # Test doubles may not accept skills/mode kwargs.
            try:
                review = review_runner(message=review_message, session=session, settings=runtime)
            except Exception as exc:
                raise ReviewError(str(exc), session_id=session.session_id) from exc
        except Exception as exc:
            raise ReviewError(str(exc), session_id=session.session_id) from exc
    else:
        try:
            review = run_review(
                message=review_message,
                session=session,
                settings=runtime,
                skills=skills,
                skills_by_aspect=skills_by_aspect,
                review_mode=review_mode,
            )
        except Exception as exc:
            raise ReviewError(str(exc), session_id=session.session_id) from exc

    if review.skills is None:
        review.skills = skills
    review.review_mode = review_mode

    review = _attach_synthesis(
        review,
        session=session,
        submission=submission,
        rubric=rubric,
        settings=runtime,
        synthesis_runner=synthesis_runner,
        review_mode=review_mode,
    )

    return SessionResult(
        kind="ok",
        submission=submission,
        fetch=fetch,
        workspace=session,
        rubric=rubric,
        skills=skills,
        review=review,
        reply=review.reply,
        review_mode=review_mode,
    )
