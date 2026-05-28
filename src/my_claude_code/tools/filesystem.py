from __future__ import annotations

from pathlib import Path

from my_claude_code.tools.context import ToolContext, ToolSpec, object_schema


MAX_FILE_OUTPUT_CHARS = 50_000


def safe_path(workdir: Path, path: str) -> Path:
    fp = (workdir / path).resolve()
    if not fp.is_relative_to(workdir):
        raise ValueError(f"Path escape working directory: {fp}")
    return fp


def read_file(ctx: ToolContext, path: str, limit: int | None = None) -> str:
    text = safe_path(ctx.workdir, path).read_text(encoding="utf-8")
    lines = text.splitlines()
    if limit and limit < len(lines):
        lines = lines[:limit] + [f"... ({len(lines) - limit} more lines)"]
    return "\n".join(lines)[:MAX_FILE_OUTPUT_CHARS]


def write_file(ctx: ToolContext, path: str, content: str) -> str:
    fp = safe_path(ctx.workdir, path)
    fp.parent.mkdir(parents=True, exist_ok=True)
    fp.write_text(content, encoding="utf-8")
    return f"Wrote {len(content)} bytes to {path}"


def edit_file(ctx: ToolContext, path: str, old_text: str, new_text: str) -> str:
    fp = safe_path(ctx.workdir, path)
    content = fp.read_text(encoding="utf-8")
    if old_text not in content:
        return f"<ERROR>Error: Text not found in {path}</ERROR>"
    fp.write_text(content.replace(old_text, new_text, 1), encoding="utf-8")
    return f"Edited {path}"


SPECS = [
    ToolSpec(
        name="read_file",
        description="Read a UTF-8 text file inside the working directory.",
        input_schema=object_schema(
            {
                "path": {"type": "string"},
                "limit": {"type": "integer", "description": "Maximum lines to read."},
            },
            ["path", "limit"],
        ),
        handler=read_file,
    ),
    ToolSpec(
        name="write_file",
        description="Write a UTF-8 text file inside the working directory.",
        input_schema=object_schema(
            {
                "path": {"type": "string"},
                "content": {"type": "string"},
            },
            ["path", "content"],
        ),
        handler=write_file,
    ),
    ToolSpec(
        name="edit_file",
        description="Replace the first occurrence of text in a file inside the working directory.",
        input_schema=object_schema(
            {
                "path": {"type": "string"},
                "old_text": {"type": "string"},
                "new_text": {"type": "string"},
            },
            ["path", "old_text", "new_text"],
        ),
        handler=edit_file,
    ),
]
