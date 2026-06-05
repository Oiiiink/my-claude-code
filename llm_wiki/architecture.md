# Architecture

This page maps the current `src/my_claude_code/` skeleton. Source files remain
authoritative.

## Entry And Config

The package entrypoint is `python -m my_claude_code`. `__main__.py` calls
`cli.main()`, and `cli.py` creates one runtime, reads user input from the TUI,
appends each user message, runs the agent loop, and prints the last assistant
text.

`config.py` loads `.env`, requires `MODEL`, and defines paths relative to the
current workdir: `.skills/`, `.tasks/`, `.team/`, `.team/inbox/`, `.sessions/`,
and `.transcripts/`.

## Runtime Loop

`Runtime` in `runtime.py` owns the model id, actor name, role, workdir, managers,
message history, session logger, and Anthropic client. All roles use the same
`Runtime.agent_loop`.

Each loop iteration:

1. micro-compacts old tool results;
2. auto-compacts when the context estimate crosses `DEFAULT_CTX_THRESHOLD`;
3. injects background and inbox notifications into history;
4. calls Anthropic with `build_tools(self.role)`;
5. appends the assistant response and session-log entry;
6. executes every returned `tool_use` through `run_tool_call`;
7. appends matching `tool_result` blocks back to history;
8. triggers full auto-compaction if the manual `compact` tool was called.

The loop scans response content for `tool_use` blocks rather than trusting only
`stop_reason`, which preserves the lesson from `bugs/1.md`.

## Tool Contract Layer

`tools/contracts.py` is the current contract layer. It defines:

- `Role = Literal["lead", "subagent", "teammate"]`;
- `ToolContext(actor, role, workdir, runtime)`;
- `ToolSpec(name, description, input_schema, handler, prepare, finalize)`;
- `ToolCall(name, input, id)`;
- `ToolCheck(valid, needs_approval, error)`;
- `ToolResult(output, success)` plus Anthropic tool-result conversion;
- `object_schema(...)` for strict object schemas.

There is no live `tools/context.py`; references to that path are stale.

## Tool Registry

`tools/registry.py` is the capability registry. It builds `TOOL_REGISTRY` from
tool-group `SPECS`, exposes role-specific tool names, validates parameters with
`tools/utils.py`, runs optional `prepare`, requests user approval for risky lead
calls, executes the handler, and then runs optional `finalize`.

Current role exposure:

- lead: shell, filesystem, todo, skills, `subagent`, task board, background shell;
- subagent: shell, filesystem, todo, skills, `compact`, background shell;
- teammate: shell, filesystem, todo, skills, background shell, `compact`, message bus, plan/shutdown request tools.

Lead-facing teammate orchestration tools are present in `tools/multi_agents.py`
but commented out in `LEAD_TOOL_NAMES`. Treat teammate mode as experimental
skeleton, not stable user-facing behavior.

## Managers

`managers/registry.py` is the state registry. It decides which manager objects a
runtime receives by role.

Current managers:

- `TodoManager`: in-memory task list for the current runtime.
- `SkillLoader`: reads `.skills/**/SKILL.md` and exposes descriptions/bodies.
- `TaskManager`: stores durable task-board JSON files in `.tasks/`.
- `BackgroundManager`: runs shell commands in daemon threads and queues notifications.
- `SessionsManager`: appends session/message/tool/compact entries to `.sessions/session_<id>.jsonl`.
- `TeamManager`: stores team membership in `.team/config.json` and starts teammate threads.
- `MessageBus`: writes inbox JSONL files under `.team/inbox/`; reads are destructive.

The manager/tool split is intentional: tools are schema plus handlers over
`ToolContext`; managers own mutable state.

## Subagent Flow

The lead exposes `subagent`. Its handler in `tools/multi_agents.py` lazily
imports `create_runtime`, builds a fresh runtime with role `subagent`, shared
model/workdir, a smaller token budget, and fresh history containing only the
subtask prompt.

The subagent shares the filesystem but not the lead conversation history.

## Teammate Flow

The teammate system is present but parked. `TeamManager.spawn` records a member,
starts a daemon thread, creates a role `teammate` runtime, and injects the lead's
shared `MessageBus` and `TeamManager` into that runtime so in-memory request
state is shared.

`MessageBus.send` appends JSONL records to `.team/inbox/<name>.jsonl`.
`MessageBus.read_inbox` reads and truncates the inbox file. Because inbox reads
are destructive and runtime notification also reads inboxes, this design needs
one-consumer discipline before teammate mode is made prominent.

## Logging And Compaction

Current durable capture is session JSONL under `.sessions/`. `SessionsManager`
records a session entry, user/assistant/tool-result messages, token counts for
assistant responses, truncated tool output text, byte counts as `nbytes`, and
compact entries with before/after token estimates.

`compaction/compaction.py` has two layers:

- `micro_compact(messages)`: replaces old long tool-result content with a short marker after `KEEP_RECENT`;
- `auto_compact(...)`: writes a full transcript to `.transcripts/transcript_<timestamp>.jsonl`, asks the model for a continuity summary, and replaces history with that summary.
