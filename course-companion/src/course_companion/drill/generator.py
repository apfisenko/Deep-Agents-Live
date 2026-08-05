"""Генератор A2UI-формы кейса: один отдельный LLM-вызов."""

from __future__ import annotations

import logging
import os
from collections.abc import AsyncIterator, Callable
from pathlib import Path
from typing import Any

from a2ui.basic_catalog.provider import BasicCatalog
from a2ui.core import A2uiParseError
from a2ui.parser.streaming import A2uiStreamParser
from a2ui.schema.constants import VERSION_0_9_1
from a2ui.schema.manager import A2uiSchemaManager

from course_companion.drill.case import RATIONALE_KEY, SUBMIT_EVENT, DrillCase

log = logging.getLogger(__name__)

CATALOG_ID = "https://a2ui.org/specification/v0_9/catalogs/basic/catalog.json"
SPEC_VERSION = "v0.9"

EXAMPLES_DIR = Path(__file__).parent / "examples" / "0.9.1"

ROLE_DESCRIPTION = (
    "You render training-case forms for an AI engineering course companion. "
    "Given a drill case (scenario, choice axes, free-form question) you MUST "
    "answer with an a2ui UI JSON response that renders the case as a form."
)

UI_RULES = f"""
- Build exactly ONE surface, following the drill form template from the examples.
- The createSurface catalogId MUST be exactly "{CATALOG_ID}".
- The surfaceId is given in the user message; use it verbatim in every message.
- The form MUST contain, top to bottom, inside a Card with a Column:
  1. the case title (Text, variant h3);
  2. the case scenario text, verbatim (Text);
  3. one ChoicePicker per axis, variant mutuallyExclusive, label = the axis
     question, options = the axis options (label/value verbatim), value bound
     to path "/<axis id>";
  4. one longText TextField for the free-form question, bound to "/{RATIONALE_KEY}";
  5. a primary Button labelled "Отправить".
- The Button action event MUST be named "{SUBMIT_EVENT}" and its context MUST
  bind every axis id to its path and "{RATIONALE_KEY}" to "/{RATIONALE_KEY}".
- Finish with an updateDataModel initialising every axis path to [] and
  "/{RATIONALE_KEY}" to "".
- Keep user-visible texts in the language of the case (Russian).
"""

TokenStreamFactory = Callable[[DrillCase], AsyncIterator[str]]


class FormGenerationError(Exception):
    """Все попытки генерации формы исчерпаны."""


class DrillFormGenerator:
    """Форма кейса из одного LLM-вызова, с валидацией и retry."""

    def __init__(
        self,
        *,
        model: str | None = None,
        api_key: str | None = None,
        base_url: str | None = None,
        token_stream_factory: TokenStreamFactory | None = None,
        max_attempts: int = 3,
    ) -> None:
        self._model = model or os.environ.get("OPENAI_MODEL", "google/gemini-3.5-flash")
        self._api_key = api_key or os.environ.get("OPENAI_API_KEY") or os.environ.get(
            "OPENROUTER_API_KEY", ""
        )
        self._base_url = base_url or os.environ.get(
            "OPENAI_BASE_URL", "https://openrouter.ai/api/v1"
        )
        self._tokens: TokenStreamFactory = token_stream_factory or self._live_tokens
        self._max_attempts = max_attempts

        schema_manager = A2uiSchemaManager(
            VERSION_0_9_1,
            catalogs=[
                BasicCatalog.get_config(version=VERSION_0_9_1, examples_path=EXAMPLES_DIR.as_uri())
            ],
        )
        self._catalog = schema_manager.get_selected_catalog()
        self._system_prompt = schema_manager.generate_system_prompt(
            role_description=ROLE_DESCRIPTION,
            ui_description=UI_RULES,
            include_schema=True,
            include_examples=True,
            validate_examples=True,
        )

    @property
    def system_prompt(self) -> str:
        return self._system_prompt

    def user_prompt(self, case: DrillCase) -> str:
        axis_paths = ", ".join(f'"/{axis.id}"' for axis in case.axes)
        return (
            f"Render this drill case as a form.\n"
            f'surfaceId (use verbatim): "{case.surface_id}"\n'
            f"Axis data model paths: {axis_paths}\n"
            f"Case JSON:\n{case.model_dump_json(indent=2)}"
        )

    async def _live_tokens(self, case: DrillCase) -> AsyncIterator[str]:
        from openai import AsyncOpenAI

        async with AsyncOpenAI(base_url=self._base_url, api_key=self._api_key) as client:
            stream = await client.chat.completions.create(
                model=self._model,
                stream=True,
                messages=[
                    {"role": "system", "content": self._system_prompt},
                    {"role": "user", "content": self.user_prompt(case)},
                ],
            )
            async for chunk in stream:
                delta = chunk.choices[0].delta.content if chunk.choices else None
                if delta:
                    yield delta

    async def astream_form(self, case: DrillCase) -> AsyncIterator[dict[str, Any]]:
        last_error: Exception | None = None
        for attempt in range(1, self._max_attempts + 1):
            emitted_surfaces: list[str] = []
            try:
                async for msg in self._attempt(case, emitted_surfaces):
                    yield msg
                return
            except ValueError as exc:
                last_error = exc
                log.warning(
                    "form generation attempt %d/%d failed: %s",
                    attempt,
                    self._max_attempts,
                    exc,
                )
                for sid in emitted_surfaces:
                    yield {"version": SPEC_VERSION, "deleteSurface": {"surfaceId": sid}}
        raise FormGenerationError(
            f"form generation failed after {self._max_attempts} attempts: {last_error}"
        )

    async def _attempt(
        self, case: DrillCase, emitted_surfaces: list[str]
    ) -> AsyncIterator[dict[str, Any]]:
        parser = A2uiStreamParser(self._catalog)
        components_seen: dict[str, dict[str, Any]] = {}
        surface_created = False
        data_model_initialized = False

        async for token in self._tokens(case):
            for part in parser.process_chunk(token):
                if not part.a2ui_json:
                    continue
                for msg in part.a2ui_json:
                    if "createSurface" in msg:
                        sid = msg["createSurface"].get("surfaceId", "")
                        emitted_surfaces.append(sid)
                        surface_created = surface_created or sid == case.surface_id
                    if msg.get("updateDataModel", {}).get("surfaceId") == case.surface_id:
                        data_model_initialized = True
                    for comp in msg.get("updateComponents", {}).get("components", []):
                        components_seen[comp.get("id", "")] = comp
                    yield msg

        self._check_completeness(case, surface_created, components_seen, data_model_initialized)

    def _check_completeness(
        self,
        case: DrillCase,
        surface_created: bool,
        components: dict[str, dict[str, Any]],
        data_model_initialized: bool,
    ) -> None:
        problems: list[str] = []
        if not surface_created:
            problems.append(f'no createSurface for "{case.surface_id}"')
        if not components:
            problems.append("no components")
        if not any(
            comp.get("action", {}).get("event", {}).get("name") == SUBMIT_EVENT
            for comp in components.values()
        ):
            problems.append(f'no Button with "{SUBMIT_EVENT}" action')
        bound_paths = {
            comp.get("value", {}).get("path")
            for comp in components.values()
            if isinstance(comp.get("value"), dict)
        }
        missing = [axis.id for axis in case.axes if f"/{axis.id}" not in bound_paths]
        if missing:
            problems.append(f"no inputs bound to axes: {missing}")
        if f"/{RATIONALE_KEY}" not in bound_paths:
            problems.append(f'no input bound to "/{RATIONALE_KEY}"')
        if not data_model_initialized:
            problems.append("no updateDataModel init")

        if problems:
            raise A2uiParseError(f"form incomplete: {'; '.join(problems)}")
