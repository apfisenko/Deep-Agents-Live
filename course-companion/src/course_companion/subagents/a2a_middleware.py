"""Middleware и job-tools для A2A checker (та же сигнатура, что у AsyncSubAgent)."""

from __future__ import annotations

import asyncio
import json
import logging
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Annotated, Any, Literal, NotRequired

import httpx
from langchain.agents.middleware.types import (
    AgentMiddleware,
    AgentState,
    ContextT,
    ModelRequest,
    ModelResponse,
    ResponseT,
)
from langchain.tools import ToolRuntime  # noqa: TC002
from langchain_core.messages import ToolMessage
from langchain_core.tools import StructuredTool
from langgraph.types import Command
from pydantic import BaseModel, Field
from typing_extensions import TypedDict

from course_companion.checker_config import a2a_allow_followup, get_a2a_checker_url
from course_companion.subagents.a2a_checker import A2A_AGENT_NAME, A2ACheckerClient, A2ACheckerError
from course_companion.subagents.async_checker import ASYNC_CHECKER_DESCRIPTION

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

logger = logging.getLogger(__name__)

_TERMINAL = frozenset({"cancelled", "success", "error"})


class A2AAsyncTask(TypedDict):
    task_id: str
    agent_name: str
    thread_id: str
    run_id: str
    status: str
    created_at: str
    last_checked_at: str
    last_updated_at: str
    transport: str
    a2a_rpc_path: str
    brief: NotRequired[str]


def _tasks_reducer(
    existing: dict[str, A2AAsyncTask] | None,
    update: dict[str, A2AAsyncTask],
) -> dict[str, A2AAsyncTask]:
    merged = dict(existing or {})
    merged.update(update)
    return merged


class A2AAsyncTaskState(AgentState):
    async_tasks: Annotated[NotRequired[dict[str, A2AAsyncTask]], _tasks_reducer]


class _StartSchema(BaseModel):
    description: str = Field(description="Brief for the async checker.")
    subagent_type: str = Field(description="Must be homework-checker-async.")


class _TaskIdSchema(BaseModel):
    task_id: str = Field(description="Exact task_id from start_async_task.")


class _UpdateSchema(_TaskIdSchema):
    message: str = Field(description="Follow-up instructions for the checker.")


class _ListSchema(BaseModel):
    status_filter: Literal["running", "success", "error", "cancelled", "all"] | None = Field(
        default=None,
        description="Filter by status.",
    )


def _now() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def _build_task_record(  # noqa: PLR0913
    client: A2ACheckerClient,
    *,
    task_id: str,
    context_id: str,
    status: str,
    brief: str = "",
    created_at: str | None = None,
) -> A2AAsyncTask:
    now = _now()
    return {
        "task_id": task_id,
        "agent_name": A2A_AGENT_NAME,
        "thread_id": context_id,
        "run_id": task_id,
        "status": status,
        "created_at": created_at or now,
        "last_checked_at": now,
        "last_updated_at": now,
        "transport": "a2a",
        "a2a_rpc_path": client.rpc_path,
        "brief": brief,
    }


def _resolve_task(task_id: str, runtime: ToolRuntime) -> A2AAsyncTask | str:
    tasks: dict[str, A2AAsyncTask] = runtime.state.get("async_tasks") or {}
    tracked = tasks.get(task_id.strip())
    if not tracked:
        return f"No tracked task found for task_id: {task_id!r}"
    return tracked


def _check_result(client: A2ACheckerClient, task: A2AAsyncTask) -> dict[str, Any]:
    remote = client.get_task(task["task_id"])
    status = client.map_task_status(remote)
    result: dict[str, Any] = {
        "status": status,
        "thread_id": task["thread_id"],
        "transport": "a2a",
    }
    if status == "success":
        result["result"] = client.extract_result_text(remote)
    elif status == "error":
        remote_status = remote.get("status") or {}
        result["error"] = (
            remote_status.get("message", "A2A task failed")
            if isinstance(remote_status, dict)
            else "A2A task failed"
        )
    return result


def _check_command(
    result: dict[str, Any],
    task: A2AAsyncTask,
    tool_call_id: str | None,
) -> Command:
    now = _now()
    last_updated = now if task["status"] != result["status"] else task["last_updated_at"]
    updated = dict(task)
    updated["status"] = result["status"]
    updated["last_checked_at"] = now
    updated["last_updated_at"] = last_updated
    return Command(
        update={
            "messages": [ToolMessage(json.dumps(result), tool_call_id=tool_call_id)],
            "async_tasks": {task["task_id"]: updated},
        }
    )


def build_a2a_job_tools(client: A2ACheckerClient) -> list[StructuredTool]:  # noqa: C901, PLR0915
    """Пять job-tools с той же сигнатурой, что у deepagents AsyncSubAgent."""
    launch_desc = (
        "Start an async homework check via A2A. Returns immediately with task_id.\n\n"
        f"Available async agent types:\n- {A2A_AGENT_NAME}: {ASYNC_CHECKER_DESCRIPTION}"
    )

    def start_async_task(
        description: str,
        subagent_type: str,
        runtime: ToolRuntime,
    ) -> str | Command:
        if subagent_type != A2A_AGENT_NAME:
            return f"Unknown async subagent type `{subagent_type}`. Available: `{A2A_AGENT_NAME}`"
        try:
            client.discover()
            remote = client.send_message(description)
        except (A2ACheckerError, httpx.HTTPError) as exc:
            logger.warning("A2A start failed: %s", exc)
            return f"Failed to launch async subagent '{subagent_type}': {exc}"

        task_id = str(remote.get("id", ""))
        context_id = str(remote.get("contextId", task_id))
        if not task_id:
            return "Failed to launch async subagent: empty task id in A2A response"
        status = client.map_task_status(remote)
        task = _build_task_record(
            client,
            task_id=task_id,
            context_id=context_id,
            status=status,
            brief=description,
        )
        msg = f"Launched async subagent. task_id: {task_id}"
        return Command(
            update={
                "messages": [ToolMessage(msg, tool_call_id=runtime.tool_call_id)],
                "async_tasks": {task_id: task},
            }
        )

    async def astart_async_task(
        description: str,
        subagent_type: str,
        runtime: ToolRuntime,
    ) -> str | Command:
        return await asyncio.to_thread(start_async_task, description, subagent_type, runtime)

    def check_async_task(task_id: str, runtime: ToolRuntime) -> str | Command:
        task = _resolve_task(task_id, runtime)
        if isinstance(task, str):
            return task
        try:
            result = _check_result(client, task)
        except (A2ACheckerError, httpx.HTTPError) as exc:
            return f"Failed to get A2A task status: {exc}"
        return _check_command(result, task, runtime.tool_call_id)

    async def acheck_async_task(task_id: str, runtime: ToolRuntime) -> str | Command:
        return await asyncio.to_thread(check_async_task, task_id, runtime)

    def update_async_task(
        task_id: str,
        message: str,
        runtime: ToolRuntime,
    ) -> str | Command:
        tracked = _resolve_task(task_id, runtime)
        if isinstance(tracked, str):
            return tracked
        brief = tracked.get("brief", "")
        try:
            if a2a_allow_followup():
                remote = client.send_message(
                    message,
                    task_id=tracked["task_id"],
                    context_id=tracked["thread_id"],
                )
            else:
                client.cancel_task(tracked["task_id"])
                merged = f"{brief}\n\n[instruction update]\n{message}".strip()
                remote = client.send_message(merged)
        except (A2ACheckerError, httpx.HTTPError) as exc:
            logger.warning("A2A update failed: %s", exc)
            return f"Failed to update async subagent: {exc}"

        new_id = str(remote.get("id", tracked["task_id"]))
        context_id = str(remote.get("contextId", tracked["thread_id"]))
        status = client.map_task_status(remote)
        new_brief = (
            message
            if a2a_allow_followup()
            else f"{brief}\n\n[instruction update]\n{message}".strip()
        )
        task = _build_task_record(
            client,
            task_id=new_id,
            context_id=context_id,
            status=status,
            brief=new_brief,
            created_at=tracked["created_at"],
        )
        updates: dict[str, A2AAsyncTask] = {new_id: task}
        if new_id != tracked["task_id"]:
            cancelled = dict(tracked)
            cancelled["status"] = "cancelled"
            cancelled["last_updated_at"] = _now()
            updates[tracked["task_id"]] = cancelled
        msg = f"Updated async subagent. task_id: {new_id}"
        return Command(
            update={
                "messages": [ToolMessage(msg, tool_call_id=runtime.tool_call_id)],
                "async_tasks": updates,
            }
        )

    async def aupdate_async_task(
        task_id: str,
        message: str,
        runtime: ToolRuntime,
    ) -> str | Command:
        return await asyncio.to_thread(update_async_task, task_id, message, runtime)

    def cancel_async_task(task_id: str, runtime: ToolRuntime) -> str | Command:
        tracked = _resolve_task(task_id, runtime)
        if isinstance(tracked, str):
            return tracked
        try:
            client.cancel_task(tracked["task_id"])
        except (A2ACheckerError, httpx.HTTPError) as exc:
            return f"Failed to cancel A2A task: {exc}"
        now = _now()
        updated = dict(tracked)
        updated["status"] = "cancelled"
        updated["last_checked_at"] = now
        updated["last_updated_at"] = now
        msg = f"Cancelled async subagent task: {tracked['task_id']}"
        return Command(
            update={
                "messages": [ToolMessage(msg, tool_call_id=runtime.tool_call_id)],
                "async_tasks": {tracked["task_id"]: updated},
            }
        )

    async def acancel_async_task(task_id: str, runtime: ToolRuntime) -> str | Command:
        return await asyncio.to_thread(cancel_async_task, task_id, runtime)

    def list_async_tasks(
        runtime: ToolRuntime,
        status_filter: Literal["running", "success", "error", "cancelled", "all"] | None = None,
    ) -> str | Command:
        tasks: dict[str, A2AAsyncTask] = runtime.state.get("async_tasks") or {}
        filtered = [
            t
            for t in tasks.values()
            if not status_filter or status_filter == "all" or t["status"] == status_filter
        ]
        if not filtered:
            return "No async subagent tasks tracked."
        entries: list[str] = []
        updates: dict[str, A2AAsyncTask] = {}
        now = _now()
        for task in filtered:
            status = task["status"]
            if status not in _TERMINAL:
                try:
                    status = client.map_task_status(client.get_task(task["task_id"]))
                except (A2ACheckerError, httpx.HTTPError):
                    logger.warning(
                        "list_async_tasks: live fetch failed for %s",
                        task["task_id"],
                        exc_info=True,
                    )
            entries.append(
                f"- task_id: {task['task_id']}  agent: {task['agent_name']}  status: {status}"
            )
            updated = dict(task)
            updated["status"] = status
            updated["last_checked_at"] = now
            if status != task["status"]:
                updated["last_updated_at"] = now
            updates[task["task_id"]] = updated
        msg = f"{len(entries)} tracked task(s):\n" + "\n".join(entries)
        return Command(
            update={
                "messages": [ToolMessage(msg, tool_call_id=runtime.tool_call_id)],
                "async_tasks": updates,
            }
        )

    async def alist_async_tasks(
        runtime: ToolRuntime,
        status_filter: Literal["running", "success", "error", "cancelled", "all"] | None = None,
    ) -> str | Command:
        return await asyncio.to_thread(list_async_tasks, runtime, status_filter)

    return [
        StructuredTool.from_function(
            name="start_async_task",
            func=start_async_task,
            coroutine=astart_async_task,
            description=launch_desc,
            infer_schema=False,
            args_schema=_StartSchema,
        ),
        StructuredTool.from_function(
            name="check_async_task",
            func=check_async_task,
            coroutine=acheck_async_task,
            description=(
                "Check A2A homework task status. Returns current status and result when complete."
            ),
            infer_schema=False,
            args_schema=_TaskIdSchema,
        ),
        StructuredTool.from_function(
            name="update_async_task",
            func=update_async_task,
            coroutine=aupdate_async_task,
            description=(
                "Send updated instructions to a running A2A check. "
                "Default: cancel + resend merged brief; set A2A_ALLOW_FOLLOWUP for follow-up."
            ),
            infer_schema=False,
            args_schema=_UpdateSchema,
        ),
        StructuredTool.from_function(
            name="cancel_async_task",
            func=cancel_async_task,
            coroutine=acancel_async_task,
            description="Cancel a running A2A homework check.",
            infer_schema=False,
            args_schema=_TaskIdSchema,
        ),
        StructuredTool.from_function(
            name="list_async_tasks",
            func=list_async_tasks,
            coroutine=alist_async_tasks,
            description="List tracked A2A homework tasks with live statuses.",
            infer_schema=False,
            args_schema=_ListSchema,
        ),
    ]


class A2ACheckerMiddleware(AgentMiddleware[Any, ContextT, ResponseT]):
    """Job-tools поверх A2A вместо AsyncSubAgentMiddleware."""

    state_schema = A2AAsyncTaskState

    def __init__(self, client: A2ACheckerClient) -> None:
        super().__init__()
        self.tools = build_a2a_job_tools(client)

    def wrap_model_call(
        self,
        request: ModelRequest[ContextT],
        handler: Callable[[ModelRequest[ContextT]], ModelResponse[ResponseT]],
    ) -> ModelResponse[ResponseT]:
        return handler(request)

    async def awrap_model_call(
        self,
        request: ModelRequest[ContextT],
        handler: Callable[[ModelRequest[ContextT]], Awaitable[ModelResponse[ResponseT]]],
    ) -> ModelResponse[ResponseT]:
        return await handler(request)


def build_a2a_checker_middleware() -> A2ACheckerMiddleware:
    client = A2ACheckerClient(get_a2a_checker_url())
    return A2ACheckerMiddleware(client)
