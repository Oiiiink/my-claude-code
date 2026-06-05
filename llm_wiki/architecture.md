# Architecture

This page maps current `src/my_claude_code/`; source files remain authoritative.

## Runtime And Unified Loop

`Runtime` in `src/my_claude_code/runtime.py` owns the model id, actor name,
role, workdir, managers, message history, and Anthropic client. All roles call
the same `Runtime.agent_loop`; subagents and teammates are no longer separate
hand-written loops.

Each loop iteration compacts old tool results, injects notifications, asks
Anthropic with `build_tools(self.role)`, executes returned tool calls, and
appends matching `tool_result` blocks. Manual compaction is routed to
`compaction/compaction.py`.

Tool execution receives a `ToolContext` from `tools/context.py`. Its `actor` is
the runtime name, while `role` is only the capability class.

## Role Model

Roles are `lead`, `subagent`, and `teammate` (`tools/context.py` and
`managers/registry.py`). The lead identity is `MAIN_NAME`, currently `"main"`,
from `config.py`. Role gates capabilities; actor names route messages,
inboxes, and request permissions.

## Two Registries

`tools/registry.py` is the capability registry. It builds Anthropic tool schemas
from grouped `ToolSpec` objects and exposes tool-name lists per role.

`managers/registry.py` is the state registry. It decides which mutable manager
objects a runtime receives per role.

These registries cooperate but stay separate: tools are stateless handlers over
`ToolContext`, while managers own mutable state such as todos, tasks,
background jobs, team membership, and inbox files.

Lead-only tools include task-board and teammate orchestration. Subagents get
local work tools and compaction. Teammates also get message, plan, shutdown,
and request-status tools. Canonical lists live in `tools/registry.py`.

## Lead To Subagent Flow

The lead exposes the `subagent` tool through `tools/registry.py`. Its handler in
`tools/multi_agents.py` lazily imports `create_runtime`, builds a fresh
`Runtime` with role `subagent`, shared workdir and model id, a smaller token
budget, and a fresh history containing only the prompt.

The subagent runs one bounded loop and returns text from its last assistant
message. It shares the filesystem, not the lead conversation history.

## Lead To Teammate To Bus Flow

The lead calls `spawn_teammate` from `tools/multi_agents.py`, which delegates to
`TeamManager.spawn` in `managers/team.py`.

`TeamManager` persists member status in `.team/config.json`, starts a daemon
thread, and runs `_teammate_loop`. That loop creates a teammate `Runtime`, then
injects the shared `MessageBus` and same `TeamManager` so request state is
visible across lead and teammate threads.

Messages are JSONL records written by `MessageBus` in `managers/message_bus.py`.
`read_inbox` returns messages and truncates the inbox file. Current teammates
are effectively one-shot: after `agent_loop` returns, status becomes `idle`, so
the loop exits on the next check unless recalled.

## Persistence Dirs

Paths are defined in `config.py` relative to the current workdir:

- `.skills/`: input skill files loaded by `SkillLoader`; deleting removes local
  skills.
- `.tasks/`: durable task-board JSON files; deleting resets task state.
- `.team/config.json`: durable team membership/status; deleting resets team
  membership.
- `.team/inbox/*.jsonl`: message inboxes; reads are destructive, so deleting
  drops pending messages.
- `.transcripts/`: compaction transcript output; safe to delete when old
  summaries are no longer needed.
