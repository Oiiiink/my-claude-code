# Project Overview

`my-claude-code` is a personal Coding Agent Engineering Harness inspired by
`learn-claude-code`, but the local direction is now broader than cloning. The
project studies the harness layer around a model: tool calling, execution
boundaries, task feedback, state capture, helper agents, memory, and evaluation.

## Current Identity

The live implementation is the `src/my_claude_code/` package. The runnable entry
is `python -m my_claude_code`, wired through `__main__.py` and `cli.py`.
Packaging is declared in `pyproject.toml` with project name `my-claude-code` and
import package `my_claude_code`.

The strategic goal is documented in `private/agent-plan/PLAN.md` and refined by
`private/agent-plan/PLAN_0604.md`: build a practical coding-agent harness
portfolio artifact, with evaluation and execution-boundary depth valued above
feature breadth. `private/report/internship-alignment-plan.md` is older but
still useful for positioning.

## Current Source Snapshot

The current skeleton centers on a CLI agent harness:

- `Runtime.agent_loop` in `runtime.py` is the shared Anthropic tool-calling loop.
- `tools/contracts.py` defines `Role`, `ToolContext`, `ToolSpec`, `ToolCall`, `ToolCheck`, and `ToolResult`.
- `tools/registry.py` builds Anthropic tool schemas, enforces role-specific tool availability, validates inputs, requests approval for risky tools, executes handlers, and finalizes results.
- Tool groups exist for filesystem, shell/background shell, todo, skill loading, task board, compaction, subagents, and experimental teammates.
- Managers under `managers/` own mutable state: todos, skills, tasks, background jobs, sessions, team membership, and message bus state.
- Runtime state is local: `.skills/`, `.tasks/`, `.team/`, `.sessions/`, and `.transcripts/`.

## Current Status

The package refactor skeleton is in place. The core loop, tool contracts,
registries, managers, compaction, session capture, and task-board pieces exist.
Multi-agent teammate code exists but is intentionally not lead-facing in the
current registry. `README.md` also says to hide multi-agent first.

Evaluation is not present yet. The current durable logging evidence is session
JSONL under `.sessions/`, not a benchmark or trajectory layer. The existing
`test/test_sessions.py` is a session-log regression test, not an eval harness.

## Direction

Near-term work should keep the package reliable and demonstrable before adding
larger systems features:

1. restore always-runs reliability and keep smoke tests green;
2. harden tool safety and execution boundaries;
3. add a coding feedback loop and a small eval harness with a headline number;
4. derive trajectory/reward data from the capture layer;
5. add persistent memory after the core loop is trustworthy;
6. finish multi-agent only after single-agent eval and safety are solid;
7. add Ray/queue scale only when eval throughput creates a real bottleneck.
