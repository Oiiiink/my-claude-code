from __future__ import annotations

import os
from pathlib import Path

from my_claude_code.tools.context import ToolContext, ToolResult, ToolSpec, ToolCall, ToolCheck, object_schema
from my_claude_code.tools.utils import check_paras

MAX_FILE_OUTPUT_CHARS = 50_000

def _validate_path(workdir: Path, path: str) -> Path:
    if not isinstance(path, str) or not path.strip():
        raise ValueError("path must be a non-empty string")

    root = workdir.resolve()
    raw = Path(path)

    candidate = raw if raw.is_absolute() else root / raw
    fp = candidate.resolve(strict=False)

    if not fp.is_relative_to(root):
        raise ValueError(f"Path escape working directory: {fp}")
    return fp

def _permission_check(operation: str, path: Path) -> None:
    if operation == "read_file":
        if not path.is_file():
            raise ValueError(f"File does not exist: {path}")
        if not os.access(path, os.R_OK):
            raise ValueError(f"File is not readable: {path}")
    elif operation in ("write_file", "edit_file"):
        if path.exists() and not os.access(path, os.W_OK):
            raise ValueError(f"File is not writable: {path}")
        if path.parent.exists() and not os.access(path.parent, os.W_OK):
            raise ValueError(f"Directory is not writable: {path.parent}")
    else:
        raise ValueError(f"Unknown file operation: {operation}")

def fs_prepare(ctx: ToolContext, tool_call: ToolCall) -> ToolCheck:
    # Check parameters
    try:
        check_paras(tool_call, SPECS_BY_NAME[tool_call.name].input_schema)
    except Exception as e:
        return ToolCheck(tool_name=tool_call.name, tool_call_id=tool_call.id, valid=False,
                         error=f"<ERROR>Invalid parameters: {e}</ERROR>")

    # Resolve and validate path
    try:
        fp = _validate_path(ctx.workdir, tool_call.input["path"])
    except Exception as e:
        return ToolCheck(tool_name=tool_call.name, tool_call_id=tool_call.id, valid=False,
                         error=f"<ERROR>Invalid path: {e}</ERROR>")

    # Make sure the file operation is allowed by the current file system state (e.g. read-only, file exists for write/edit, etc.)
    try:
        _permission_check(tool_call.name, fp)
    except Exception as e:
        return ToolCheck(tool_name=tool_call.name, tool_call_id=tool_call.id, valid=False,
                         error=f"<ERROR>Operation not allowed: {e}</ERROR>")

    # Special check
    if tool_call.name == "edit_file":
        # Ensure old_text exists in the file for edit_file operation
        if not fp.is_file():
            return ToolCheck(tool_name=tool_call.name, tool_call_id=tool_call.id, valid=False,
                             error=f"<ERROR>File does not exist for editing: {fp}</ERROR>")
        content = fp.read_text(encoding='utf-8')
        if tool_call.input["old_text"] not in content:
            return ToolCheck(tool_name=tool_call.name, tool_call_id=tool_call.id, valid=False,
                             error=f"<ERROR>File does not contain old_text: {fp}</ERROR>")

    return ToolCheck(tool_name=tool_call.name, tool_call_id=tool_call.id, valid=True)

def read_file(ctx: ToolContext, path: str, limit: int | None = None) -> str:
    try:
        fp = _validate_path(ctx.workdir, path)
    except Exception as e:
        return f"<ERROR>Invalid path: {e}</ERROR>"
    text = fp.read_text(encoding="utf-8")
    lines = text.splitlines()
    if limit and limit < len(lines):
        lines = lines[:limit] + [f"... ({len(lines) - limit} more lines)"]
    return "\n".join(lines)

def write_file(ctx: ToolContext, path: str, content: str) -> str:
    try:
        fp = _validate_path(ctx.workdir, path)
    except Exception as e:
        return f"<ERROR>Invalid path: {e}</ERROR>"
    fp.parent.mkdir(parents=True, exist_ok=True)
    fp.write_text(content, encoding="utf-8")
    return f"Wrote {len(content)} bytes to {path}"

def edit_file(ctx: ToolContext, path: str, old_text: str, new_text: str) -> str:
    try:
        fp = _validate_path(ctx.workdir, path)
    except Exception as e:
        return f"<ERROR>Invalid path: {e}</ERROR>"
    content = fp.read_text(encoding="utf-8")
    fp.write_text(content.replace(old_text, new_text, 1), encoding="utf-8")
    return f"Edited {path}"

def fs_finalize(ctx: ToolContext, tool_call: ToolCall, output: str) -> ToolResult:
    if tool_call.name == "read_file" and len(output) > MAX_FILE_OUTPUT_CHARS:
        output = output[:MAX_FILE_OUTPUT_CHARS] + f"\n... (output truncated, total {len(output)} chars)"
    return ToolResult(tool_name=tool_call.name, tool_call_id=tool_call.id, output=output, success=True)


SPECS = [
    ToolSpec(
        name="read_file",
        description="Read a UTF-8 text file inside the working directory.",
        input_schema=object_schema(
            {
                "path": {"type": "string", "description": "Relative path or Full path to the file."},
                "limit": {"type": "integer", "description": "Maximum lines to read."},
            },
            ["path"],
        ),
        handler=read_file,
        prepare=fs_prepare,
        finalize=fs_finalize,
    ),
    ToolSpec(
        name="write_file",
        description="Write a UTF-8 text file inside the working directory.",
        input_schema=object_schema(
            {
                "path": {"type": "string", "description": "Relative path or Full path to the file."},
                "content": {"type": "string"},
            },
            ["path", "content"],
        ),
        handler=write_file,
        prepare=fs_prepare,
        finalize=fs_finalize,
    ),
    ToolSpec(
        name="edit_file",
        description="Replace the first occurrence of text in a file inside the working directory.",
        input_schema=object_schema(
            {
                "path": {"type": "string", "description": "Relative path or Full path to the file."},
                "old_text": {"type": "string"},
                "new_text": {"type": "string"},
            },
            ["path", "old_text", "new_text"],
        ),
        handler=edit_file,
        prepare=fs_prepare,
        finalize=fs_finalize,
    ),
]

SPECS_BY_NAME = {spec.name: spec for spec in SPECS}
