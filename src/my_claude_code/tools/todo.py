from __future__ import annotations

from my_claude_code.tools.contracts import ToolContext, ToolSpec, object_schema, ToolCall, ToolCheck
from my_claude_code.tools.utils import check_paras

def todo_prepare(ctx: ToolContext, tool_call: ToolCall) -> ToolCheck:
    items = tool_call.input.get("items", [])
    for item in items:
        if not item.get("id") or not item.get("content") or not item.get("status") or item["status"] not in ["pending", "in_progress", "done"]:
            return ToolCheck(tool_name=tool_call.name, tool_call_id=tool_call.id, valid=False,
                             error=f"<ERROR>Item with id '{item.get('id', 'unknown')}' is missing required fields or has invalid status. Each item must have 'id', 'content', and 'status'.</ERROR>")
    return ToolCheck(tool_name=tool_call.name, tool_call_id=tool_call.id, valid=True)

def update_todo(ctx: ToolContext, items: list[dict]) -> str:
    return ctx.runtime.todo.update(items)

SPECS = [
    ToolSpec(
        name="todo",
        description="Manage a local todo list for complex tasks.",
        input_schema=object_schema(
            {
                "items": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string"},
                            "content": {"type": "string"},
                            "status": {
                                "type": "string",
                                "enum": ["pending", "in_progress", "done"],
                            },
                        },
                        "required": ["id", "content", "status"],
                        "additionalProperties": False,
                    },
                }
            },
            ["items"],
        ),
        handler=update_todo,
        prepare=todo_prepare,
    ),
]
