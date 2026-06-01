from __future__ import annotations

from collections.abc import Iterable

from my_claude_code.tools.context import Role, ToolCall, ToolContext, ToolSpec, ToolResult, ToolCheck
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
    #"spawn_teammate",
    #"list_teammates",
    #"send_message",
    #"read_inbox",
    #"broadcast",
    #"shutdown_request",
    #"request_check",
    #"plan_response",
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

def run_tool_call(ctx: ToolContext, tool_call: ToolCall) -> ToolResult:
    tool_check = prepare_tool_call(ctx, tool_call)
    if not tool_check.valid:
        return ToolResult(tool_name=tool_call.name, tool_call_id=tool_call.id, output=tool_check.error or "Invalid tool call", success=False)
    output = execute_tool_call(ctx, tool_call)
    return finalize_tool_call(ctx, tool_call, output)
    
def prepare_tool_call(ctx: ToolContext, tool_call: ToolCall) -> ToolCheck:
    spec = get_tool_spec(tool_call.name)
    if spec is None or tool_call.name not in TOOLS_BY_ROLE[ctx.role]:
        return ToolCheck(tool_name=tool_call.name, tool_call_id=tool_call.id, valid=False, error=f"Tool {tool_call.name} not found or not allowed for role {ctx.role}")
    
    return spec.prepare(ctx, tool_call) if spec.prepare else ToolCheck(tool_name=tool_call.name, tool_call_id=tool_call.id, valid=True)
    
def execute_tool_call(ctx: ToolContext, tool_call: ToolCall) -> str:
    return get_tool_spec(tool_call.name).handler(ctx, **tool_call.input)
    
def finalize_tool_call(ctx: ToolContext, tool_call: ToolCall, output: str) -> ToolResult:
    return get_tool_spec(tool_call.name).finalize(ctx, tool_call, output) if get_tool_spec(tool_call.name).finalize else ToolResult(tool_name=tool_call.name, tool_call_id=tool_call.id, output=output, success=True)
