from __future__ import annotations

import json

from my_claude_code.tools.context import ToolContext, ToolSpec, object_schema


VALID_MSG_TYPES = {
    "message",
    "broadcast",
    "shutdown_request",
    "shutdown_response",
    "plan_request",
    "plan_response",
}


def spawn_teammate(ctx: ToolContext, name: str, role: str, prompt: str) -> str:
    return ctx.runtime.team.spawn(name, role, prompt)


def list_teammates(ctx: ToolContext) -> str:
    return ctx.runtime.team.list_all()


def send_message(
    ctx: ToolContext,
    to: str,
    content: str,
    msg_type: str = "message",
) -> str:
    return ctx.runtime.bus.send(ctx.actor, to, content, msg_type)


def read_inbox(ctx: ToolContext) -> str:
    return json.dumps(ctx.runtime.bus.read_inbox(ctx.actor), indent=2)


def broadcast(ctx: ToolContext, content: str) -> str:
    return ctx.runtime.bus.broadcast(ctx.actor, content, ctx.runtime.team.member_names())


def shutdown_request(ctx: ToolContext, name: str) -> str:
    return ctx.runtime.team.send_shutdown_request(ctx.actor, name)


def shutdown_response(
    ctx: ToolContext,
    request_id: str,
    approve: bool,
    reason: str | None = None,
) -> str:
    return ctx.runtime.team.handle_shutdown_request(ctx.actor, request_id, approve, reason)


def plan_request(ctx: ToolContext, plan: str) -> str:
    return ctx.runtime.team.send_plan_request(ctx.actor, "lead", plan)


def plan_response(
    ctx: ToolContext,
    request_id: str,
    approve: bool,
    feedback: str | None = None,
) -> str:
    return ctx.runtime.team.handle_plan_request(ctx.actor, request_id, approve, feedback or "")


def request_check(ctx: ToolContext, request_id: str) -> str:
    return ctx.runtime.team.check_request_status(ctx.actor, request_id)


SPECS = [
    ToolSpec(
        name="spawn_teammate",
        description="Spawn a persistent teammate, or recall an idle teammate with the same name.",
        input_schema=object_schema(
            {
                "name": {"type": "string"},
                "role": {"type": "string"},
                "prompt": {"type": "string"},
            },
            ["name", "role", "prompt"],
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
