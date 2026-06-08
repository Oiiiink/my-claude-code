# Ignored now
from __future__ import annotations

import json

from my_claude_code.config import MAIN_NAME
from my_claude_code.tools.contracts import ToolContext, ToolSpec, object_schema
from my_claude_code.managers import get_managers


VALID_MSG_TYPES = {
    "message",
    "broadcast",
    "shutdown_request",
    "shutdown_response",
    "plan_request",
    "plan_response",
}

def run_subagent(ctx, prompt: str, max_turn: int = 50) -> str:
    from my_claude_code.runtime import create_runtime
    subagent = create_runtime("subagent", role="subagent", model_id=ctx.runtime.model_id, workdir=ctx.workdir,
                              managers=get_managers("subagent"),
                              max_tokens=ctx.runtime.max_tokens // 4, max_turn=max_turn)
    subagent.history.append({"role": "user", "content": prompt})
    subagent.agent_loop()
    
    last_content = subagent.history[-1]["content"]
    if isinstance(last_content, str):
        return last_content
    return "".join(b.text for b in last_content if hasattr(b, "text")) or "(no summary)"


def spawn_teammate(ctx: ToolContext, name: str, prompt: str) -> str:
    return ctx.runtime.team.spawn(name, prompt, ctx.runtime.model_id, ctx.workdir, ctx.runtime.bus)


def list_teammates(ctx: ToolContext) -> str:
    return ctx.runtime.team.list_all()


def send_message(
    ctx: ToolContext,
    to: str,
    content: str,
    msg_type: str = "message",
    extra: dict | None = None,
) -> str:
    if msg_type not in VALID_MSG_TYPES:
        return f"<ERROR>Invalid message type '{msg_type}'. Valid types are: {', '.join(VALID_MSG_TYPES)}</ERROR>"
    return ctx.runtime.bus.send(ctx.actor, to, content, msg_type, extra)


def read_inbox(ctx: ToolContext) -> str:
    return json.dumps(ctx.runtime.bus.read_inbox(ctx.actor), indent=2)


def broadcast(ctx: ToolContext, content: str) -> str:
    return ctx.runtime.bus.broadcast(ctx.actor, content, ctx.runtime.team.member_names())


def shutdown_request(ctx: ToolContext, name: str) -> str:
    return ctx.runtime.team.send_shutdown_request(ctx.runtime.bus, ctx.actor, name)


def shutdown_response(
    ctx: ToolContext,
    request_id: str,
    approve: bool,
    reason: str | None = None,
) -> str:
    return ctx.runtime.team.handle_shutdown_request(ctx.runtime.bus, ctx.actor, request_id, approve, reason)


def plan_request(ctx: ToolContext, plan: str) -> str:
    return ctx.runtime.team.send_plan_request(ctx.runtime.bus, ctx.actor, MAIN_NAME, plan)


def plan_response(
    ctx: ToolContext,
    request_id: str,
    approve: bool,
    feedback: str | None = None,
) -> str:
    return ctx.runtime.team.handle_plan_request(ctx.runtime.bus, ctx.actor, request_id, approve, feedback or "")


def request_check(ctx: ToolContext, request_id: str) -> str:
    return ctx.runtime.team.check_request_status(ctx.actor, request_id)

SPECS = [
    ToolSpec(
        name="subagent",
        description="Spawn a subagent with fresh context to reduce context rot. It shares filesystems but not conversation history.",
        input_schema=object_schema(
            {
                "prompt": {"type": "string", "description": "The task prompt for the subagent."},
                "max_turn": {"type": "integer", "description": "The maximum number of conversation turns for the subagent before it is forcefully terminated.", "default": 50},
            },
            ["prompt"],
        ),
        handler=run_subagent,
    ),
    ToolSpec(
        name="spawn_teammate",
        description="Spawn a persistent teammate, or recall an idle teammate with the same name.",
        input_schema=object_schema(
            {
                "name": {"type": "string"},
                "prompt": {"type": "string"},
            },
            ["name", "prompt"],
        ),
        handler=spawn_teammate,
    ),
    ToolSpec(
        name="list_teammates",
        description="List all teammates with name, role, and status.",
        input_schema=object_schema(),
        handler=list_teammates,
    ),
    ToolSpec(
        name="send_message",
        description="Send a message to a teammate's inbox.",
        input_schema=object_schema(
            {
                "to": {"type": "string"},
                "content": {"type": "string"},
                "msg_type": {"type": "string", "enum": sorted(VALID_MSG_TYPES)},
            },
            ["to", "content"],
        ),
        handler=send_message,
    ),
    ToolSpec(
        name="read_inbox",
        description="Read and drain the caller's inbox.",
        input_schema=object_schema(),
        handler=read_inbox,
    ),
    ToolSpec(
        name="broadcast",
        description="Send a message to all teammates except the caller.",
        input_schema=object_schema({"content": {"type": "string"}}, ["content"]),
        handler=broadcast,
    ),
    ToolSpec(
        name="shutdown_request",
        description="Ask a teammate to shut down gracefully.",
        input_schema=object_schema({"name": {"type": "string"}}, ["name"]),
        handler=shutdown_request,
    ),
    ToolSpec(
        name="shutdown_response",
        description="Respond to a shutdown request.",
        input_schema=object_schema(
            {
                "request_id": {"type": "string"},
                "approve": {"type": "boolean"},
                "reason": {"type": "string"},
            },
            ["request_id", "approve"],
        ),
        handler=shutdown_response,
    ),
    ToolSpec(
        name="plan_request",
        description="Submit a teammate plan for lead approval.",
        input_schema=object_schema({"plan": {"type": "string"}}, ["plan"]),
        handler=plan_request,
    ),
    ToolSpec(
        name="plan_response",
        description="Approve or reject a teammate's plan.",
        input_schema=object_schema(
            {
                "request_id": {"type": "string"},
                "approve": {"type": "boolean"},
                "feedback": {"type": "string"},
            },
            ["request_id", "approve"],
        ),
        handler=plan_response,
    ),
    ToolSpec(
        name="request_check",
        description="Check the status of a request by request_id.",
        input_schema=object_schema({"request_id": {"type": "string"}}, ["request_id"]),
        handler=request_check,
    ),
]
