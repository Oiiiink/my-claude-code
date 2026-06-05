# Decisions

This page records durable choices that should guide future implementation.

## Root `llm_wiki/` Is The Active Wiki

Use the root `llm_wiki/` directory as the maintained repo wiki. Mentions of
`.agents/llm_wiki/` in older instructions or logs are path drift unless the
checkout is changed again.

Evidence: current repo tree has root `llm_wiki/`; `.agents/` is empty.

## Src-Layout Package

Use `src/my_claude_code/` as live code and `python -m my_claude_code` as the
entrypoint. This makes the project closer to a real Python package and prevents
old root monolith files from being treated as current architecture.

Evidence: `pyproject.toml`, `src/my_claude_code/__main__.py`, and
`src/my_claude_code/cli.py`.

## Tool Contracts Live In `tools/contracts.py`

Keep shared tool dataclasses and schema helpers in `tools/contracts.py`.
`ToolContext` carries actor, role, workdir, and runtime; `ToolSpec` carries the
schema, handler, and optional prepare/finalize hooks.

Evidence: `src/my_claude_code/tools/contracts.py`. `tools/context.py` is stale.

## Unified Agent Loop

Use one `Runtime.agent_loop` across lead, subagent, and teammate roles. This
keeps tool settlement, compaction, reminders, session logging, and notifications
in one place instead of maintaining divergent loops.

Evidence: `src/my_claude_code/runtime.py`; subagent and teammate creation in
`tools/multi_agents.py` and `managers/team.py`.

## Role Gates, Names Route

Use role strings only for capability gating. Use actor names for identity,
message routing, and request permissions. This prevents semantic bugs where
`"lead"` or `"teammate"` is treated as a concrete agent name.

Evidence: `ToolContext` in `tools/contracts.py`, `MAIN_NAME` in `config.py`, and
message/request handling in `tools/multi_agents.py` plus `managers/team.py`.

## Managers vs Tools Split

Keep `tools/` mostly stateless: schema plus handler functions over
`ToolContext`. Keep mutable state in `managers/`: todos, skills, tasks,
background jobs, sessions, team members, request state, and inbox files.

This split makes tool exposure easier to reason about and keeps state ownership
out of schema modules.

Evidence: `tools/registry.py`, `tools/*`, `managers/registry.py`, and
`managers/*`.

## Two Registries

Keep a tool registry and a manager registry instead of one combined registry.
Tool availability and state instantiation change for different reasons; keeping
them separate makes role design explicit.

Evidence: `tools/registry.py` and `managers/registry.py`.

## Hide Teammate Mode Until Foundations Are Solid

Teammate code exists, but lead-facing teammate tools are commented out in the
current role registry. This matches the README instruction to hide multi-agent
first. Keep multi-agent work behind the registry until Stage 0-3 reliability,
safety, and eval evidence exist.

Evidence: `README.md` and `LEAD_TOOL_NAMES` in `tools/registry.py`.

## Shared TeamManager In Teammate Runtime

Teammate runtimes must point at the same `TeamManager` instance as the lead when
request status lives in memory. Otherwise plan and shutdown responses can look
up a different request table and silently fail.

Evidence: `managers/team.py` injects `teammate.team = self`.

## Local JSONL Before External Queues

Use local JSONL capture before adding Redis, Ray, or service mode. Current code
already uses JSONL for session capture and inboxes. Future trajectory and eval
views should be projections from durable capture rather than parallel logging
systems.

Evidence: `managers/sessions.py`, `managers/message_bus.py`, and
`private/design/logging.md`.

## Current Roadmap Sources Are Under `private/`

Use `private/agent-plan/PLAN.md` as the stage roadmap and
`private/agent-plan/PLAN_0604.md` as the backend/RL and internship-timing
supplement. Use `private/report/internship-alignment-plan.md` as older
positioning context. Do not cite missing root `internship-alignment-plan.md` or
root `report/` paths.

Evidence: current repo tree under `private/agent-plan/` and `private/report/`.

## Evidence Before Claims

When documenting behavior, cite current source or durable artifacts. Do not
infer current behavior from upstream `learn-claude-code`, old root monoliths, or
stale wiki logs.
