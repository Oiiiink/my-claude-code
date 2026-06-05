# Bugs And Lessons

This page captures reusable failure patterns. It is not a current bug tracker.

## Name Is Not Role

Pattern: never let a role string masquerade as an identity.

`ToolContext.actor` is the concrete runtime name. `ToolContext.role` is only the
capability class. The lead's configured identity is `MAIN_NAME`, currently
`"main"`, but some paths still use literal `"lead"`.

Why it matters: the program may keep running while messages or permissions go
to the wrong inbox or request target.

Evidence: `tools/context.py`, `config.py`, `tools/multi_agents.py`, and
`managers/team.py`.

## Shared In-Memory State Must Really Be Shared

Pattern: when thread coordination depends on in-memory state, all runtimes must
reference the same owner object.

`TeamManager.requests` is in memory. Lead and teammate request tools only agree
if teammate runtimes receive the same `TeamManager` instance as the lead.

Evidence: `managers/team.py` creates teammate runtimes and assigns
`teammate.team = self`.

## One-Shot vs Long-Lived Teammate Lifecycle

Pattern: choose one lifecycle deliberately. Do not accidentally build a poller
that exits after one job.

Current `_teammate_loop` calls `agent_loop`, then marks the member `idle`.
Because the next loop check requires status `working`, the teammate exits unless
the lead recalls it with `spawn_teammate`.

Evidence: `managers/team.py`.

## Destructive Auto-Drain Needs One Consumer

Pattern: do not expose two consumers for one destructive source.

`Runtime._inbox_notification` reads and truncates the actor inbox before the
model call. The `read_inbox` tool uses the same destructive `MessageBus.read_inbox`.
For the lead, automatic notification can consume messages before the tool can
observe them.

Evidence: `runtime.py`, `tools/multi_agents.py`, and `managers/message_bus.py`.

## Tool Use Must Always Be Settled

Pattern: if an assistant response contains tool calls, every call needs a
matching `tool_result` block even when individual handlers fail.

`Runtime.agent_loop` scans assistant content for tool calls, wraps handler
exceptions as tool results, and appends results back as a user message.

Evidence: `runtime.py`.

## Tool Input Is Untrusted Input

Pattern: JSON Schema controls shape, not semantic safety.

Handlers still need runtime validation for paths, file sizes, sensitive files,
timeouts, output length, and command policy.

Evidence: `tools/context.py`, `tools/filesystem.py`, `tools/shell.py`, and
`internship-alignment-plan.md`.

## Path Safety Requires Path Objects

Pattern: convert model-provided path strings into resolved `Path` objects before
file access.

`safe_path` resolves paths under the runtime workdir and rejects escapes. Future
work should add sensitive-path and size/type checks on top of this.

Evidence: `tools/filesystem.py`.
