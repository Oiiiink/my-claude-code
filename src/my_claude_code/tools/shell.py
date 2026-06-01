from __future__ import annotations

import subprocess

from my_claude_code.tools.contracts import ToolContext, ToolSpec, object_schema


MAX_COMMAND_OUTPUT_CHARS = 50_000
BLOCKED_COMMAND_FRAGMENTS = ("rm -rf /", "sudo", "shutdown", "reboot", "> /dev/")


def bash(ctx: ToolContext, command: str) -> str:
    if any(fragment in command for fragment in BLOCKED_COMMAND_FRAGMENTS):
        return "<ERROR>Error: Dangerous command blocked</ERROR>"

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
    return ctx.runtime.background.run(command)


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
    ),
    ToolSpec(
        name="background_run",
        description="Run a shell command in a background thread. Returns task_id immediately.",
        input_schema=object_schema({"command": {"type": "string"}}, ["command"]),
        handler=background_run,
    ),
    ToolSpec(
        name="check_background",
        description="Check background task status. Omit task_id to list all.",
        input_schema=object_schema({"task_id": {"type": "string"}}),
        handler=check_background,
    ),
]
