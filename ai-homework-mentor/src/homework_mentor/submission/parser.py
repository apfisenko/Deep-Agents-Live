"""Parse free-text / path hints into a Submission."""

from __future__ import annotations

import re
from pathlib import Path
from typing import TYPE_CHECKING, Protocol

from langchain.chat_models import init_chat_model

from homework_mentor.submission.models import SourceType, Submission, TopicExtraction

if TYPE_CHECKING:
    from homework_mentor.config import RuntimeSettings, YamlConfig

_GITHUB_URL_RE = re.compile(
    r"https?://(?:www\.)?github\.com/[\w.-]+/[\w.-]+(?:\.git)?(?:/[^\s]*)?",
    re.IGNORECASE,
)
_TOPIC_RE = re.compile(
    r"(?im)(?:тема|topic)\s*[:\-]\s*(.+)$",
)
# Windows drive path or ./relative or /unix-ish path tokens
_PATH_RE = re.compile(
    r"(?P<path>(?:[A-Za-z]:\\|\\\\|\./|\.\\|/)[^\s\"']+)",
)
_GITHUB_REPO_PARTS = 5  # https / host / owner / repo


class TopicExtractor(Protocol):
    def __call__(self, raw_text: str) -> str | None: ...


def extract_github_url(text: str) -> str | None:
    match = _GITHUB_URL_RE.search(text)
    if not match:
        return None
    url = match.group(0).rstrip(").,;")
    # Drop tree/blob suffixes for source value — keep repo root
    parts = url.rstrip("/").split("/")
    if len(parts) >= _GITHUB_REPO_PARTS and parts[2].lower() == "github.com":
        url = "/".join(parts[:_GITHUB_REPO_PARTS])
    return url.removesuffix(".git")


def extract_topic_heuristic(text: str) -> str | None:
    match = _TOPIC_RE.search(text)
    if not match:
        return None
    topic = match.group(1).strip().strip(" \"'")
    return topic or None


def extract_path_heuristic(text: str) -> str | None:
    match = _PATH_RE.search(text)
    if not match:
        return None
    return match.group("path").rstrip(").,;")


def detect_source(
    raw_text: str,
    *,
    explicit_path: str | Path | None = None,
) -> tuple[SourceType, str | None]:
    if explicit_path is not None:
        return SourceType.LOCAL_PATH, str(Path(explicit_path))

    github = extract_github_url(raw_text)
    if github:
        return SourceType.GITHUB_URL, github

    path = extract_path_heuristic(raw_text)
    if path:
        return SourceType.LOCAL_PATH, path

    return SourceType.UNKNOWN, None


def build_clarification_question(
    *,
    source_type: SourceType,
    topic: str | None,
) -> str:
    missing_source = source_type is SourceType.UNKNOWN
    missing_topic = not topic
    if missing_source and missing_topic:
        return (
            "Уточните, пожалуйста: (1) путь к локальной папке с кодом "
            "или публичную ссылку GitHub и (2) тему задания."
        )
    if missing_source:
        return (
            "Укажите источник кода: путь к локальной директории "
            "или публичную ссылку на GitHub-репозиторий."
        )
    return (
        "Укажите тему задания (например: «Тема: FastAPI + Telegram bot»). "
        "Не буду угадывать тему сама."
    )


def parse_submission(
    raw_text: str,
    *,
    explicit_path: str | Path | None = None,
    topic_extractor: TopicExtractor | None = None,
    settings: RuntimeSettings | None = None,
) -> Submission:
    """Parse input into Submission. Never invents topic or source."""
    text = (raw_text or "").strip()
    source_type, source_value = detect_source(text, explicit_path=explicit_path)

    topic = extract_topic_heuristic(text)
    if topic is None and topic_extractor is not None:
        topic = topic_extractor(text)
    elif topic is None and settings is not None:
        topic = _llm_extract_topic(text, settings=settings)

    if topic is not None:
        topic = topic.strip() or None

    needs = source_type is SourceType.UNKNOWN or topic is None
    question = build_clarification_question(source_type=source_type, topic=topic) if needs else None

    return Submission(
        source_type=source_type,
        source_value=source_value,
        topic=topic,
        raw_text=text,
        needs_clarification=needs,
        clarification_question=question,
    )


def _llm_extract_topic(raw_text: str, *, settings: RuntimeSettings) -> str | None:
    model = init_chat_model(
        settings.yaml.agent.model,
        api_key=settings.openrouter_api_key.get_secret_value(),
        temperature=0.0,
        max_tokens=512,
    )
    structured = model.with_structured_output(TopicExtraction)
    system = settings.yaml.parse_submission_prompts.system_prompt
    result = structured.invoke(
        [
            {"role": "system", "content": system},
            {"role": "user", "content": raw_text},
        ],
    )
    if not isinstance(result, TopicExtraction):
        return None
    if result.confidence == "none" or not result.observed_topic:
        return None
    return result.observed_topic.strip() or None


def ensure_parse_prompt_loaded(yaml_cfg: YamlConfig) -> str:
    """Helper for tests: return parse system prompt from loaded config."""
    return yaml_cfg.parse_submission_prompts.system_prompt
