from __future__ import annotations

from collections.abc import Iterable

from my_claude_code.tools.contracts import Role, ToolCall, ToolContext, ToolSpec, ToolResult, ToolCheck
from my_claude_code.tools import filesystem, multi_agents, shell, skills, task_board, todo, compaction
from my_claude_code.tools.utils import check_paras


LEAD_TOOL_NAMES = [
    "bash",
    "read_file",
    "write_file",
    "edit_file",
    "todo",
    "load_skill",
    "subagent",
    "compact",
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
SPECS_BY_NAME = {spec.name: spec for spec in TOOL_REGISTRY.values()}


def get_tool_spec(tool_name: str) -> ToolSpec:
    return TOOL_REGISTRY.get(tool_name)


def build_tools(role: Role) -> list[dict]:
    return [TOOL_REGISTRY[tool_name].to_anthropic_tool() for tool_name in TOOLS_BY_ROLE[role]]

def run_tool_call(ctx: ToolContext, tool_call: ToolCall) -> ToolResult:
    tool_check = prepare_tool_call(ctx, tool_call)
    if not tool_check.valid:
        return ToolResult(tool_name=tool_call.name, tool_call_id=tool_call.id, output=tool_check.error or "<ERROR>Invalid tool call</ERROR>", success=False)
    if tool_check.needs_approval and not _request_approval(ctx, tool_call, tool_check):
        reason = "Approval denied by user." if ctx.role == "lead" else "This command is risky and ask lead to run it if you really want the result."
        return ToolResult(tool_name=tool_call.name, tool_call_id=tool_call.id, output=f"<ERROR>{reason}</ERROR>", success=False)
        
    try:
        output = execute_tool_call(ctx, tool_call)
        return finalize_tool_call(ctx, tool_call, output)
    except Exception as e:
        return ToolResult(tool_name=tool_call.name, tool_call_id=tool_call.id, output=f"<ERROR>Failed to execute tool: {e}</ERROR>", success=False)

def prepare_tool_call(ctx: ToolContext, tool_call: ToolCall) -> ToolCheck:
    spec = get_tool_spec(tool_call.name)
    if spec is None or tool_call.name not in TOOLS_BY_ROLE[ctx.role]:
        return ToolCheck(tool_name=tool_call.name, tool_call_id=tool_call.id, valid=False, error=f"<ERROR>Tool {tool_call.name} not found or not allowed for role {ctx.role}</ERROR>")
    
    try:
        check_paras(tool_call, spec.input_schema)
    except Exception as e:
        return ToolCheck(tool_name=tool_call.name, tool_call_id=tool_call.id, valid=False,
                         error=f"<ERROR>Invalid parameters: {e}</ERROR>")
    
    return spec.prepare(ctx, tool_call) if spec.prepare else ToolCheck(tool_name=tool_call.name, tool_call_id=tool_call.id, valid=True)
    
def execute_tool_call(ctx: ToolContext, tool_call: ToolCall) -> str:
    return get_tool_spec(tool_call.name).handler(ctx, **tool_call.input)
    
def finalize_tool_call(ctx: ToolContext, tool_call: ToolCall, output: str) -> ToolResult:
    return get_tool_spec(tool_call.name).finalize(ctx, tool_call, output) if get_tool_spec(tool_call.name).finalize else ToolResult(tool_name=tool_call.name, tool_call_id=tool_call.id, output=output, success=not output.startswith("<ERROR>"))

def _request_approval(ctx: ToolContext, tool_call: ToolCall, tool_check: ToolCheck) -> bool:
    if ctx.role != "lead":                   
        return False
    detail = tool_call.input.get("command", "")
    answer = input(f"\n[approval] {tool_call.name}: {detail}\n  run this? [y/N] ")
    return answer.strip().lower() in ("y", "yes")