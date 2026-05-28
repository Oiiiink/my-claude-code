from __future__ import annotations

from my_claude_code.tools.context import ToolContext, ToolSpec, object_schema


def task_create(
    ctx: ToolContext,
    subject: str,
    description: str = "",
    blockedBy: list[int] | None = None,
) -> str:
    return ctx.runtime.tasks.create(subject, description, blockedBy or [])


def task_update(
    ctx: ToolContext,
    task_id: int,
    status: str | None = None,
    addBlockedBy: list[int] | None = None,
    removeBlockedBy: list[int] | None = None,
) -> str:
    return ctx.runtime.tasks.update(task_id, status, addBlockedBy, removeBlockedBy)


def task_list(ctx: ToolContext) -> str:
    return ctx.runtime.tasks.list_all()


def task_get(ctx: ToolContext, task_id: int) -> str:
    return ctx.runtime.tasks.get(task_id)


SPECS = [
    ToolSpec(
        name="task_create",
        description="Create a durable task-board entry.",
        input_schema=object_schema(
            {
                "subject": {"type": "string"},
                "description": {
                    "type": "string",
                    "description": "More detailed information about this task.",
                },
                "blockedBy": {
                    "type": "array",
                    "items": {"type": "integer"},
                    "description": "Task IDs that must be completed first.",
                },
            },
            ["subject"],
        ),
        handler=task_create,
    ),
    ToolSpec(
        name="task_update",
        description="Update a task's status or dependencies.",
        input_schema=object_schema(
            {
                "task_id": {"type": "integer"},
                "status": {
                    "type": "string",
                    "enum": ["pending", "in_progress", "completed"],
                },
                "addBlockedBy": {"type": "array", "items": {"type": "integer"}},
                "removeBlockedBy": {"type": "array", "items": {"type": "integer"}},
            },
            ["task_id"],
        ),
        handler=task_update,
    ),
    ToolSpec(
        name="task_list",
        description="List all current task-board entries.",
        input_schema=object_schema(),
        handler=task_list,
    ),
    ToolSpec(
        name="task_get",
        description="Get full details of a task by ID.",
        input_schema=object_schema({"task_id": {"type": "integer"}}, ["task_id"]),
        handler=task_get,
    ),
]
