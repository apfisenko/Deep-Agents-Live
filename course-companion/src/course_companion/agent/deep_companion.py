"""Deep companion — deepagents-агент для Agent Server (async checker)."""

from __future__ import annotations

import shutil
import uuid
from pathlib import Path

from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend
from langchain_openai import ChatOpenAI

from course_companion.agent.server_modes import QA_PROMPT, build_server_modes_middleware
from course_companion.config import Config
from course_companion.subagents.async_checker import (
    build_async_checker,
    build_homework_checker_subagent,
)
from course_companion.subagents.course_qa import build_course_qa_subagent

KB_DIR = Path(__file__).resolve().parents[3] / "data" / "kb"
SKILLS_SRC = Path(__file__).resolve().parents[3] / "data" / "skills"
WORKSPACE_DIR = Path(__file__).resolve().parents[3] / ".companion-workspace"


def _make_llm() -> ChatOpenAI:
    cfg = Config()
    return ChatOpenAI(
        model="openai/gpt-4o-mini",
        openai_api_key=cfg.openrouter_api_key,  # type: ignore[arg-type, call-arg]
        openai_api_base="https://openrouter.ai/api/v1",  # type: ignore[call-arg]
    )


def build_deep_companion(*, async_checker: bool = True):
    """Собрать deepagents companion для Agent Server."""
    model = _make_llm()
    modes = build_server_modes_middleware(async_checker=async_checker)
    checker = build_async_checker() if async_checker else build_homework_checker_subagent()

    session_root = WORKSPACE_DIR / uuid.uuid4().hex[:8]
    session_root.mkdir(parents=True, exist_ok=True)
    if SKILLS_SRC.is_dir():
        shutil.copytree(SKILLS_SRC, session_root / "skills", dirs_exist_ok=True)
    backend = FilesystemBackend(root_dir=str(session_root), virtual_mode=True)

    return create_deep_agent(
        model=model,
        system_prompt=QA_PROMPT,
        backend=backend,
        middleware=[modes],
        subagents=[checker, build_course_qa_subagent(KB_DIR)],  # type: ignore[list-item]
        skills=["/skills/"] if SKILLS_SRC.is_dir() else None,
    )
