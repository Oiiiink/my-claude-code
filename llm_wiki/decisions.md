# Decisions

This page records durable choices that should guide future implementation.

## Src-Layout Package

Use `src/my_claude_code/` as live code and `python -m my_claude_code` as the
entrypoint. This makes the project closer to a real package and avoids treating
the old root monolith as current architecture.

Evidence: `pyproject.toml`, `src/my_claude_code/__main__.py`, and `cli.py`.

## Unified Agent Loop

Use one `Runtime.agent_loop` across lead, subagent, and teammate roles. This
keeps tool settlement, compaction, reminders, and notifications in one place
instead of maintaining divergent loops.

Evidence: `runtime.py`; subagent and teammate creation in `tools/multi_agents.py`
and `managers/team.py`.

## Role Gates, Names Route

Use role strings only for capability gating. Use actor names for identity,
message routing, and request permissions. This prevents semantic bugs where
`"lead"` or `"teammate"` is treated as a concrete agent name.

Evidence: `ToolContext` in `tools/context.py` and `MAIN_NAME` in `config.py`.

## Managers vs Tools Split

Keep `tools/` mostly stateless: schema plus handler functions over a
`ToolContext`. Keep mutable state in `managers/`: todos, skills, tasks,
background jobs, team members, and inbox files.

This split makes tool exposure easier to reason about and keeps state ownership
out of schema modules.

Evidence: `tools/registry.py`, `tools/*`, and `managers/*`.

## Two Registries

Keep a tool registry and a manager registry instead of one combined registry.
Tool availability and state instantiation change for different reasons; keeping
them separate makes role design explicit.

Evidence: `tools/registry.py` and `managers/registry.py`.

## Shared TeamManager In Teammate Runtime

Teammate runtimes must point at the same `TeamManager` instance as the lead
when request status lives in memory. Otherwise plan and shutdown responses can
look up a different request table and silently fail.

Evidence: `managers/team.py` injects `teammate.team = self`.

## Local JSONL Before External Queues

Use local JSONL files for the message bus before adding Redis, Ray, or service
mode. It is simple enough for learning, debugging, and early evaluation.

Evidence: `managers/message_bus.py` writes `.team/inbox/*.jsonl`.

## Evidence Before Claims

When documenting behavior, cite current source or durable artifacts. Do not
infer current behavior from upstream `learn-claude-code` or old monolith files.

## Append-Only JSONL Run Log

Log each run to one append-only `.runs/<run_id>/events.jsonl` with four record
kinds (`session`, `message`, `tool_call`, `compaction`) keyed by a monotonic
`seq`. JSONL is chosen for O(1), crash-safe appends and streamable reads; the
flat `seq` replaces pi's `id`/`parentId` tree until branching is actually needed.
The `tool_call` record (outcome + duration) is the per-call metrics layer pi
omits and the seed of later trajectory/eval data.

Evidence: `design/logging.md`.
