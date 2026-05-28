from __future__ import annotations

from collections.abc import Iterable

from my_claude_code.tools.context import Role, ToolContext, ToolSpec
from my_claude_code.tools import filesystem, multi_agents, shell, skills, task_board, todo, compaction


LEAD_TOOL_NAMES = [
    "bash",
    "read_file",
    "write_file",
    "edit_file",
    "todo",
    "load_skill",
    "subagent",
    "task_create",
    "task_update",
    "task_list",
    "task_get",
    "background_run",
    "check_background",
    "spawn_teammate",
    "list_teammates",
    "send_message",
    "read_inbox",
    "broadcast",
    "shutdown_request",
    "request_check",
    "plan_response",
]

SUBAGENT_TOOL_NAMES = [
    "bash",
    "read_file",
    "write_file",
    "edit_file",
    "todo",
    "load_skill",
    "compact",
    "background_run",
    "check_background",
]

TEAMMATE_TOOL_NAMES = [
    "bash",
    "read_file",
    "write_file",
    "edit_file",
    "todo",
    "load_skill",
    "background_run",
    "check_background",
    "compact",
    "send_message",
    "broadcast",
    "shutdown_response",
    "plan_request",
    "request_check",
]

TOOLS_BY_ROLE: dict[Role, list[str]] = {
    "lead": LEAD_TOOL_NAMES,
    "subagent": SUBAGENT_TOOL_NAMES,
    "teammate": TEAMMATE_TOOL_NAMES,
}


def _build_registry(groups: Iterable[Iterable[ToolSpec]]) -> dict[str, ToolSpec]:
    registry: dict[str, ToolSpec] = {}
    for specs in groups:
        for spec in specs:
            if spec.name in registry:
                raise ValueError(f"Duplicate tool spec: {spec.name}")
            registry[spec.name] = spec
    return registry


TOOL_REGISTRY = _build_registry(
    [
        filesystem.SPECS,
        shell.SPECS,
        todo.SPECS,
        skills.SPECS,
        task_board.SPECS,
        multi_agents.SPECS,
        compaction.SPECS,
    ]
)


def get_tool_spec(tool_name: str) -> ToolSpec:
    return TOOL_REGISTRY[tool_name]


def build_tools(role: Role) -> list[dict]:
    return [TOOL_REGISTRY[tool_name].to_anthropic_tool() for tool_name in TOOLS_BY_ROLE[role]]


def execute_tool(ctx: ToolContext, tool_name: str, tool_input: dict) -> str:
    if tool_name not in TOOLS_BY_ROLE[ctx.role]:
        return f"<ERROR>Tool '{tool_name}' is not available for role '{ctx.role}'</ERROR>"

    spec = TOOL_REGISTRY.get(tool_name)
    if spec is None:
        return f"<ERROR>Unknown tool: {tool_name}</ERROR>"

    try:
        return spec.handler(ctx, **tool_input)
    except Exception as exc:
        return f"<ERROR>Error executing tool {tool_name}: {exc}</ERROR>"
