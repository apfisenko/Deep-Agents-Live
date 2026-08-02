"""Router — детерминированный LLM-классификатор интента студента.

Паттерн: Router «classify → configure» — отдельная позиция в графе;
LLM внутри, но результат — фиксированный Pydantic-объект Intent.
"""

from course_companion.router.intent import Intent, RouteDecision, RouterInput
from course_companion.router.router import route

__all__ = ["Intent", "RouteDecision", "RouterInput", "route"]
