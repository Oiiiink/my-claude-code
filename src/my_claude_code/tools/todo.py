from __future__ import annotations

from my_claude_code.tools.context import ToolContext, ToolSpec, object_schema


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
    ),
]
