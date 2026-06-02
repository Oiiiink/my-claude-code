from __future__ import annotations

from my_claude_code.tools.contracts import ToolContext, ToolSpec, object_schema

def load_skill(ctx: ToolContext, name: str) -> str:
    return ctx.runtime.skills.get_content(name)


SPECS = [
    ToolSpec(
        name="load_skill",
        description="Load specialized knowledge by skill name.",
        input_schema=object_schema({"name": {"type": "string"}}, ["name"]),
        handler=load_skill,
    ),
]
