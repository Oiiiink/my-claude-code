from __future__ import annotations

import subprocess
import shlex

from my_claude_code.tools.contracts import ToolContext, ToolSpec, ToolCall, ToolCheck, object_schema


MAX_COMMAND_OUTPUT_CHARS = 50_000
RISKY_COMMAND_FRAGMENTS = ("rm ", "sudo", "shutdown", "reboot", ">", "mv ", "dd ", "git push")

def shell_prepare(ctx: ToolContext, tool_call: ToolCall) -> ToolCheck:
    try:
        tokens = shlex.split(tool_call.input.get("command", ""))
    except Exception as e:
        return ToolCheck(tool_name=tool_call.name, tool_call_id=tool_call.id, valid=False,
                         error=f"<ERROR>Error parsing command: {e}</ERROR>")
    
    if not tokens:
        return ToolCheck(tool_name=tool_call.name, tool_call_id=tool_call.id, valid=False,
                         error="<ERROR>Command cannot be empty.</ERROR>")
    risky = any(fragment in tool_call.input.get("command", "") for fragment in RISKY_COMMAND_FRAGMENTS)
    return ToolCheck(tool_name=tool_call.name, tool_call_id=tool_call.id, valid=True, needs_approval=bool(risky))
    

def bash(ctx: ToolContext, command: str) -> str:
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=ctx.workdir,
            capture_output=True,
            text=True,
            timeout=120,
        )
    except subprocess.TimeoutExpired:
        return "<ERROR>Error: Timeout (120s)</ERROR>"
    except (FileNotFoundError, OSError) as exc:
        return f"<ERROR>Error: {exc}</ERROR>"

    output = (result.stdout + result.stderr).strip()
    return output[:MAX_COMMAND_OUTPUT_CHARS] if output else "(no output)"


def background_run(ctx: ToolContext, command: str) -> str:
    return ctx.runtime.background.run(command, ctx.workdir)


def check_background(ctx: ToolContext, task_id: str | None = None) -> str:
    return ctx.runtime.background.check(task_id)


SPECS = [
    ToolSpec(
        name="bash",
        description="Run a shell command in the working directory.",
        input_schema=object_schema(
            {
                "command": {
                    "type": "string",
                    "description": "A shell command that is runnable directly.",
                }
            },
            ["command"],
        ),
        handler=bash,
        prepare=shell_prepare,
    ),
    ToolSpec(
        name="background_run",
        description="Run a shell command in a background thread. Returns task_id immediately.",
        input_schema=object_schema({"command": {"type": "string"}}, ["command"]),
        handler=background_run,
        prepare=shell_prepare,
    ),
    ToolSpec(
        name="check_background",
        description="Check background task status. Omit task_id to list all.",
        input_schema=object_schema({"task_id": {"type": "string"}}),
        handler=check_background,
    ),
]
