"""Course Companion — верхний диалоговый агент (единственный говорящий).

Собирается из:
- двух субагентов двух видов: homework-checker (CompiledSubAgent — обёрнутый
  менторский пайплайн) и course-qa (declarative dict-SubAgent с kb-тулами);
- handoffs-машины трёх режимов (companion/modes.py) — middleware подменяет
  промпт и фильтрует тулы по state["mode"];
- статический system_prompt = QA_PROMPT (дефолтное «лицо»; middleware заменяет
  его на промпт активного режима при каждом вызове модели).

Импорт ментора приносит глобальный HarnessProfile для провайдера "openai"
(general-purpose субагент выключен, штатная SummarizationMiddleware исключена).
Регистрируем его явно ДО create_deep_agent, чтобы поведение не зависело от
порядка инициализации, и добавляем свою SummarizationMiddleware вручную —
так же, как это делает сам ментор.
"""

from __future__ import annotations

import shutil
import uuid

from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend
from deepagents.middleware.summarization import SummarizationMiddleware

from mentor.agent.orchestrator import mentor_harness_profile
from mentor.config import get_config

from companion.checker import build_async_checker, build_homework_checker
from companion.config import PROJECT_ROOT, WORKSPACE_DIR, build_model
from companion.modes import QA_PROMPT, build_modes_middleware
from companion.review_tools import build_review_tools
from companion.subagents.course_qa import build_course_qa_subagent

KB_DIR = PROJECT_ROOT / "data" / "kb"
# Скиллы проекта (SKILL.md-каталоги): data/skills/<имя>/SKILL.md.
SKILLS_SRC = PROJECT_ROOT / "data" / "skills"


def build_companion(model=None, *, async_checker: bool = False):
    """Собрать companion-агента.

    Развилка `async_checker` — способ проверки домашек:
    - False (CLI): синхронный CompiledSubAgent из Т11 — проверка блокирует ход,
      зато агент полностью живёт в одном процессе без Agent Server;
    - True (сервер): AsyncSubAgent — фоновая задача на графе "checker".
      В локальный CLI-инвок этот путь не отдаём: ASGI-транспорт co-deployed
      субагента живёт только внутри Agent Server (в `.invoke()` он падает,
      а поднимать сервер ради CLI — против «запасного входа без Node»).
    """
    model = model or build_model()
    session_root = WORKSPACE_DIR / uuid.uuid4().hex[:8]
    session_root.mkdir(parents=True, exist_ok=True)
    backend = FilesystemBackend(root_dir=str(session_root), virtual_mode=True)

    # Скиллы — штатная механика deepagents (`skills=`): SKILL.md-каталоги
    # читаются С БЭКЕНДА агента (progressive disclosure через file-тулы).
    # Бэкенд у нас — изолированный сессионный workspace, поэтому проектные
    # скиллы материализуем в него копией; путь "/skills/" — виртуальный
    # (virtual_mode резолвит его внутрь session_root).
    if SKILLS_SRC.is_dir():
        shutil.copytree(SKILLS_SRC, session_root / "skills", dirs_exist_ok=True)

    mentor_harness_profile()  # детерминированно применяем профиль ментора

    summarization = SummarizationMiddleware(
        model=model,
        backend=backend,
        trigger=("fraction", 0.55),
        keep=("fraction", 0.15),
    )
    review_tools = build_review_tools(get_config().workspace_base)
    modes = build_modes_middleware(review_tools, async_checker=async_checker)

    checker = build_async_checker() if async_checker else build_homework_checker()
    return create_deep_agent(
        model=model,
        system_prompt=QA_PROMPT,
        backend=backend,
        middleware=[summarization, modes],
        subagents=[checker, build_course_qa_subagent(KB_DIR)],
        skills=["/skills/"] if SKILLS_SRC.is_dir() else None,
    )
