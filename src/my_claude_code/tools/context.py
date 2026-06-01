from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Literal


Role = Literal["lead", "subagent", "teammate"]

@dataclass
class ToolContext:
    actor: str
    role: Role
    workdir: Path
    runtime: Any  # Avoid circular import, should be Runtime, but is not a good design.


@dataclass(frozen=True)
class ToolSpec:
    name: str
    description: str
    input_schema: dict[str, Any]
    handler: Callable[..., str]
    prepare: Callable[[ToolContext, ToolCall], ToolCheck] | None = None
    finalize: Callable[[ToolContext, ToolCall, str], ToolResult] | None = None

    def to_anthropic_tool(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.input_schema,
        }

@dataclass(frozen=True)
class ToolCall:
    name: str
    input: dict[str, Any]
    id: str

@dataclass(frozen=True)
class ToolCheck:
    tool_name: str
    tool_call_id: str
    valid: bool
    error: str | None = None

@dataclass
class ToolResult:
    tool_name: str
    tool_call_id: str
    output: str
    success: bool
    
    def to_anthropic_tool_result(self) -> dict[str, Any]:
        return {
            "type": "tool_result",
            "tool_use_id": self.tool_call_id,
            "content": self.output,
        }
    

def object_schema(
    properties: dict[str, Any] | None = None,
    required: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "type": "object",
        "properties": properties or {},
        "required": required or [],
        "additionalProperties": False,
    }
