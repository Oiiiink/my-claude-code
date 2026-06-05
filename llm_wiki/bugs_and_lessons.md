# Bugs And Lessons

This page captures reusable failure patterns. It is not a full bug tracker, but
it should name current source/test mismatches that future agents are likely to
trip over.

## Name Is Not Role

Pattern: never let a role string masquerade as an identity.

`ToolContext.actor` is the concrete runtime name. `ToolContext.role` is only the
capability class. The lead's configured identity is `MAIN_NAME`, currently
`"main"`. Some message/request paths still use literal `"lead"`, so future
multi-agent work must normalize this before claiming stability.

Why it matters: the program may keep running while messages or permissions go
to the wrong inbox or request target.

Evidence: `tools/contracts.py`, `config.py`, `tools/multi_agents.py`, and
`managers/team.py`.

## Tool Use Must Always Be Settled

Pattern: if an assistant response contains tool calls, every call needs a
matching `tool_result` block even when individual handlers fail.

`Runtime.agent_loop` scans assistant content for tool calls, wraps handler
exceptions as tool results through `run_tool_call`, and appends results back as a
user message. This is the fix direction from `bugs/1.md`, where `stop_reason`
was not reliable enough.

Evidence: `runtime.py`, `tools/registry.py`, and `bugs/1.md`.

## Tool Input Is Untrusted Input

Pattern: JSON Schema controls shape, not semantic safety.

Current source has useful first guards:

- `check_paras(...)` validates required fields and basic JSON Schema types;
- `filesystem._validate_path(...)` resolves paths under `ctx.workdir`;
- `filesystem._permission_check(...)` checks file existence and OS access;
- `shell.shell_prepare(...)` rejects empty commands and asks approval for a short risky-fragment list;
- shell/background execution has timeout and output caps.

Remaining Stage-1 hardening: sensitive path policy (`.env`, `.git`, `.venv`),
large-file policy, explicit shell allowlist or unsafe mode, stronger command
parsing, and tests for malicious cases.

Evidence: `tools/utils.py`, `tools/filesystem.py`, `tools/shell.py`,
`private/agent-plan/PLAN.md`, and `private/report/internship-alignment-plan.md`.

## Path Safety Requires Resolved Path Objects

Pattern: convert model-provided path strings into resolved `Path` objects before
file access.

The current helper is `_validate_path(workdir, path)`, not `safe_path`. It
rejects path escape by resolving against the runtime workdir. Future work should
add sensitive-path and size/type checks on top of this.

Evidence: `tools/filesystem.py`.

## Session Log Schema Must Match Tests

Pattern: once a log schema is tested, the implementation and test vocabulary
must stay aligned.

Current `SessionsManager.append_tool_result(...)` writes `nbytes` on
`ToolResultMessage`, but `test/test_sessions.py` expects `output_bytes`. A
verification run on 2026-06-05 produced one pass and one failure for that reason.
Resolve this in source/tests before treating session logging as green.

Evidence: `managers/sessions.py`, `managers/types/sessions.py`, and
`test/test_sessions.py`.

## Shared In-Memory State Must Really Be Shared

Pattern: when thread coordination depends on in-memory state, all runtimes must
reference the same owner object.

`TeamManager.requests` is in memory. Lead and teammate request tools only agree
if teammate runtimes receive the same `TeamManager` instance as the lead.

Evidence: `managers/team.py` creates teammate runtimes and assigns
`teammate.team = self`.

## One-Shot vs Long-Lived Teammate Lifecycle

Pattern: choose one lifecycle deliberately. Do not accidentally build a worker
that exits after one job.

Current `_teammate_loop` calls `agent_loop`, then marks the member `idle`.
Because the next loop check requires status `working`, the teammate exits unless
the lead recalls it with `spawn_teammate`. This is acceptable only if the
intended lifecycle is recallable one-shot teammates.

Evidence: `managers/team.py`.

## Destructive Auto-Drain Needs One Consumer

Pattern: do not expose two consumers for one destructive source.

`Runtime._inbox_notification` reads and truncates the actor inbox before the
model call. The `read_inbox` tool uses the same destructive
`MessageBus.read_inbox`. Automatic notification can consume messages before a
tool call can observe them.

Evidence: `runtime.py`, `tools/multi_agents.py`, and `managers/message_bus.py`.

## Parked Features Should Stay Hidden

Pattern: source can contain an experimental skeleton without making it part of
the demo surface.

Lead teammate tools are currently commented out in `tools/registry.py`, while
their handlers and managers still exist. Future agents should not re-document
teammate mode as stable until the role registry, tests, lifecycle, and inbox
semantics are deliberately finished.

Evidence: `tools/registry.py`, `tools/multi_agents.py`, `managers/team.py`, and
`README.md`.
