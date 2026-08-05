"""Генератор A2UI-формы кейса: один отдельный LLM-вызов (решение Р7).

Companion решает, ЧТО спросить (кейс), генератор — КАК отрисовать: схемный
system-промпт A2UI (~11K токенов: правила + JSON-схемы каталога + наш шаблон
`examples/0.9.1/drill_form.json`) изолирован здесь и не раздувает промпт
самого companion.

Пайплайн: LLM-токены -> A2uiStreamParser (инкрементальный, с auto-healing) ->
валидированные A2UI-сообщения наружу по мере генерации (форма «проявляется»
в браузере). Невалидная генерация -> retry: частично построенные поверхности
убираются deleteSurface'ом и попытка повторяется с нуля.
"""

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

from companion.drill.case import RATIONALE_KEY, SUBMIT_EVENT, DrillCase

log = logging.getLogger(__name__)

# Литеральный v0_9-URL: клиентский basicCatalog зарегистрирован именно под ним,
# а BasicCatalog.get_catalog_id("0.9.1") вернул бы несуществующий v0_9_1-URL
# ("Unknown catalog" на клиенте). Грабля версий №2 (см. README модуля).
CATALOG_ID = "https://a2ui.org/specification/v0_9/catalogs/basic/catalog.json"
# В сообщениях всегда "v0.9": схема принимает v0.9|v0.9.1, но zod-схемы клиента
# заточены только под "v0.9". Грабля версий №4 (см. README модуля).
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

# Токены LLM для кейса; фабрика подменяется в тестах фейком.
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
        self._api_key = api_key or os.environ.get("OPENAI_API_KEY", "")
        self._base_url = base_url or os.environ.get(
            "OPENAI_BASE_URL", "https://openrouter.ai/api/v1"
        )
        self._tokens: TokenStreamFactory = token_stream_factory or self._live_tokens
        self._max_attempts = max_attempts

        schema_manager = A2uiSchemaManager(
            VERSION_0_9_1,
            catalogs=[
                BasicCatalog.get_config(
                    version=VERSION_0_9_1, examples_path=str(EXAMPLES_DIR)
                )
            ],
        )
        self._catalog = schema_manager.get_selected_catalog()
        # validate_examples=True: наш шаблон проверяется валидатором уже при
        # сборке промпта — сломанный пример не доедет до LLM.
        self._system_prompt = schema_manager.generate_system_prompt(
            role_description=ROLE_DESCRIPTION,
            ui_description=UI_RULES,
            include_schema=True,
            include_examples=True,
            validate_examples=True,
        )

    # --- промпт -----------------------------------------------------------------

    @property
    def system_prompt(self) -> str:
        return self._system_prompt

    def user_prompt(self, case: DrillCase) -> str:
        """Пер-кейсовая часть: сам кейс + жёсткие идентификаторы для связки."""
        axis_paths = ", ".join(f'"/{axis.id}"' for axis in case.axes)
        return (
            f"Render this drill case as a form.\n"
            f'surfaceId (use verbatim): "{case.surface_id}"\n'
            f"Axis data model paths: {axis_paths}\n"
            f"Case JSON:\n{case.model_dump_json(indent=2)}"
        )

    # --- LLM --------------------------------------------------------------------

    async def _live_tokens(self, case: DrillCase) -> AsyncIterator[str]:
        """Живой стрим токенов (OpenAI-совместимый API, у нас OpenRouter)."""
        # Ленивый импорт: openai нужен только живому пути, тестам с фейком — нет.
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

    # --- генерация с retry --------------------------------------------------------

    async def astream_form(self, case: DrillCase) -> AsyncIterator[dict[str, Any]]:
        """A2UI-сообщения формы по мере генерации; retry на невалидную попытку.

        Ошибка попытки — это и A2uiParseError из стрим-парсера (грабля №4:
        синтаксис он не лечит), и ValueError от строгой валидации полных
        сообщений внутри парсера, и «форма пришла неполной» (невалидные куски
        валидатор молча дропает — поэтому в конце проверяем комплектность).
        После неудачной попытки частично отрисованные поверхности убираются
        deleteSurface'ом, чтобы у клиента не оставался мусор.
        """
        last_error: Exception | None = None
        for attempt in range(1, self._max_attempts + 1):
            emitted_surfaces: list[str] = []
            try:
                async for msg in self._attempt(case, emitted_surfaces):
                    yield msg
                return
            # A2uiParseError/A2uiIntegrityError — подклассы ValueError
            # (a2ui.core.exceptions); строгая валидация в парсере кидает ValueError.
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
        """Одна попытка: свежий LLM-вызов через свежий парсер + проверка комплектности."""
        parser = A2uiStreamParser(self._catalog)
        components_seen: dict[str, dict[str, Any]] = {}
        surface_created = False
        data_model_initialized = False

        async for token in self._tokens(case):
            for part in parser.process_chunk(token):
                if not part.a2ui_json:
                    continue  # разговорный текст вокруг <a2ui-json> нам не нужен
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

        self._check_completeness(
            case, surface_created, components_seen, data_model_initialized
        )

    def _check_completeness(
        self,
        case: DrillCase,
        surface_created: bool,
        components: dict[str, dict[str, Any]],
        data_model_initialized: bool,
    ) -> None:
        """Функциональный минимум формы; иначе A2uiParseError -> retry.

        Валидатор гарантирует только схемную корректность отдельных сообщений;
        что форма ЦЕЛИКОМ пригодна (та поверхность, есть чем ответить и что
        нажать) — проверяем сами.
        """
        problems: list[str] = []
        if not surface_created:
            problems.append(f'no createSurface for "{case.surface_id}"')
        if not components:
            problems.append("no components")
        # Кнопка с событием ответа: без неё round-trip невозможен.
        if not any(
            comp.get("action", {}).get("event", {}).get("name") == SUBMIT_EVENT
            for comp in components.values()
        ):
            problems.append(f'no Button with "{SUBMIT_EVENT}" action')
        # Хотя бы по одному инпуту на ось (биндинг по пути /<axis id>).
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
        # Инициализация data model: без неё нетронутые поля не попадут в userAction.
        if not data_model_initialized:
            problems.append("no updateDataModel init")

        if problems:
            raise A2uiParseError(f"form incomplete: {'; '.join(problems)}")
