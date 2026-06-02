from __future__ import annotations

from my_claude_code.tools.contracts import ToolCheck, ToolContext, ToolSpec, object_schema, ToolCall

def create_prepare(ctx: ToolContext, tool_call: ToolCall) -> ToolCheck:
    if tool_call.input.get("blockedBy"):
        blocked_by = tool_call.input["blockedBy"]
        invalid_task = [task_id for task_id in blocked_by if not ctx.runtime.tasks.have_task(task_id)]
        if invalid_task:
            return ToolCheck(tool_name=tool_call.name, tool_call_id=tool_call.id, valid=False,
                             error=f"<ERROR>Invalid blockedBy task_id: {invalid_task}. No such task.</ERROR>")
            
    return ToolCheck(tool_name=tool_call.name, tool_call_id=tool_call.id, valid=True)

def update_prepare(ctx: ToolContext, tool_call: ToolCall) -> ToolCheck:
    task_id = tool_call.input["task_id"]
    if not ctx.runtime.tasks.have_task(task_id):
        return ToolCheck(tool_name=tool_call.name, tool_call_id=tool_call.id, valid=False,
                         error=f"<ERROR>Invalid task_id: {task_id}. No such task. You should create it first.</ERROR>")
    if tool_call.input.get("removeBlockedBy") or tool_call.input.get("addBlockedBy"):
        mentioned_tasks = tool_call.input.get("removeBlockedBy", []) + tool_call.input.get("addBlockedBy", [])
        invalid_task = [task_id for task_id in mentioned_tasks if not ctx.runtime.tasks.have_task(task_id)]
        if invalid_task:
            return ToolCheck(tool_name=tool_call.name, tool_call_id=tool_call.id, valid=False,
                             error=f"<ERROR>Invalid mentioned task_id: {invalid_task}. No such task. You can't add/remove blocked by a task that doesn't exist.</ERROR>")
    from my_claude_code.managers.tasks import TASK_STATUS
    if tool_call.input.get("status") and tool_call.input["status"] not in TASK_STATUS:
        return ToolCheck(tool_name=tool_call.name, tool_call_id=tool_call.id, valid=False,
                         error=f"<ERROR>Invalid status: {tool_call.input['status']}. status should be in {TASK_STATUS}</ERROR>")

    return ToolCheck(tool_name=tool_call.name, tool_call_id=tool_call.id, valid=True)

def get_prepare(ctx: ToolContext, tool_call: ToolCall) -> ToolCheck:
    task_id = tool_call.input["task_id"]
    if not ctx.runtime.tasks.have_task(task_id):
        return ToolCheck(tool_name=tool_call.name, tool_call_id=tool_call.id, valid=False,
                         error=f"<ERROR>Invalid task_id: {task_id}. No such task.</ERROR>")
    return ToolCheck(tool_name=tool_call.name, tool_call_id=tool_call.id, valid=True)


def task_prepare(ctx: ToolContext, tool_call: ToolCall) -> ToolCheck:
    return PREPARE_BY_TOOL_NAME.get(tool_call.name)(ctx, tool_call) if PREPARE_BY_TOOL_NAME.get(tool_call.name) else ToolCheck(tool_name=tool_call.name, tool_call_id=tool_call.id, valid=True)

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
        prepare=task_prepare,
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
        prepare=task_prepare,
    ),
    ToolSpec(
        name="task_list",
        description="List all current task-board entries.",
        input_schema=object_schema(),
        handler=task_list,
        prepare=task_prepare,
    ),
    ToolSpec(
        name="task_get",
        description="Get full details of a task by ID.",
        input_schema=object_schema({"task_id": {"type": "integer"}}, ["task_id"]),
        handler=task_get,
        prepare=task_prepare,
    ),
]

PREPARE_BY_TOOL_NAME = {
    "task_create": create_prepare,
    "task_update": update_prepare,
    "task_get": get_prepare,
}
