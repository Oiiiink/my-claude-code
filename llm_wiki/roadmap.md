# Roadmap

Authoritative roadmap source: `private/agent-plan/PLAN.md` (2026-05-30).
Current supplement: `private/agent-plan/PLAN_0604.md` (backend/RL learning,
internship timing, and application tactics). Older positioning source:
`private/report/internship-alignment-plan.md`.

Source code remains authoritative for what exists. The private plans are
authoritative for order and priority.

## Strategic Direction

Present the project as a Coding Agent Engineering Harness: a bounded
tool-calling loop with execution boundaries, test/verify feedback, a small
SWE-bench-style evaluation harness that prints a headline number, RL-ready
trajectory/reward logging, and persistent cross-session memory.

Thesis from the build plan: "Model + Harness = Agent." The value of this repo is
the harness layer, not a generic chatbot surface.

## Priority

Depth on eval beats breadth on features:

1. Stage 2: eval harness + feedback loop + headline number.
2. Stage 1: bounded harness core / execution boundary.
3. Stage 3: RL-ready trajectories + failure analysis.
4. Stage 0: always-runs reliability.
5. Stage 4: persistent memory.
6. Stage 5: multi-agent, finished only after 1-3 are solid.
7. Stage 6: Ray/queue scale only on a real eval bottleneck.

The 2026-06-04 supplement confirms that eval and RL-data come before
multi-agent/backend. Do not pull multi-agent forward just because skeleton code
already exists.

## Stage Status Against Current Source

### Stage 0: Always-runs reliability

Status: incomplete. The package entrypoint exists, the src-layout refactor is in
place, and a no-write AST parse of `src/my_claude_code/**/*.py` passed on
2026-06-05. However, the current local session test run is not green:
`test/test_sessions.py` has one passing test and one failure because the test
expects `output_bytes` while current source emits `nbytes`.

Remaining:

- decide and stabilize the session tool-output byte-count field;
- add a smoke test that imports the package with a configured `MODEL`;
- validate every tool schema;
- keep unfinished teammate tools hidden from the lead demo surface;
- add a regression test for the `tool_use`/`tool_result` settlement bug.

Checkpoint: cold clone can run a simple read/edit/check/summarize task with zero
unhandled exceptions, and `uv run pytest` is green.

### Stage 1: Bounded harness core / execution boundary

Status: in progress. Current source has `tools/contracts.py`,
`tools/registry.py`, role-gated tool lists, workdir path containment in
`filesystem._validate_path`, shell timeouts/output caps, and approval prompts for
a small risky-fragment list.

Remaining:

- block sensitive paths such as `.env`, `.git`, and `.venv`;
- add file size/type limits before reading;
- make shell policy explicit with allowlist or unsafe mode;
- avoid relying on ad hoc command-string fragments;
- capture duration/outcome/args for every tool call;
- write tests for unsafe path, command, and output cases.

Checkpoint: a threat table with at least six unsafe actions, each
blocked/bounded and backed by a test.

### Stage 2: Feedback loop + evaluation harness

Status: pending. No `my_claude_code.eval` package, eval runner, benchmark task
fixtures, or report exists in the current tree.

Build:

- a structured `run_tests` tool with parsed pass/fail output;
- a bounded plan -> edit -> run-tests -> inspect-failure -> retry loop;
- mini SWE-bench-style task specs and isolated fixtures;
- patch-apply failure separate from test failure;
- generated report with pass rate, iterations, tool calls, wall time, and cost if available.

Checkpoint: a reproducible eval report under the current private/public report
layout with a headline pass-rate from a local task set.

### Stage 3: RL-ready trajectories + failure analysis

Status: pending. Current `.sessions/` JSONL is a useful capture seed, but it is
not yet an RL-ready trajectory schema.

Build:

- one episode format: observation, assistant action/tool call, result, final outcome, reward, metadata;
- reward fields for test pass, safety violations, edit size, cost, and wall time;
- a replay/round-trip check;
- a failure-analysis report grouping failures by planning, localization, modification, execution, and recovery.

Checkpoint: trajectory file round-trips, reward function has a unit test, and a
short failure-analysis writeup names one concrete harness improvement.

### Stage 4: Persistent cross-session memory

Status: pending. The repo has compaction, local skills, durable tasks, and
session logs, but no deliberate cross-session memory module.

Build:

- on-disk progress artifacts;
- initializer vs per-session coding steps;
- structured state that a fresh process can read;
- compaction that points to durable full-content artifacts instead of losing detail.

Checkpoint: kill mid-task, restart cold, reconstruct state from disk, and finish.

### Stage 5: Multi-agent, finished

Status: experimental and intentionally hidden from lead tools. `TeamManager`,
`MessageBus`, teammate handlers, and request tools exist, but lead-facing
teammate tools are commented out in `tools/registry.py`.

Remaining:

- deliberate teammate lifecycle;
- validated teammate names and recipients;
- durable inbox history, not only destructive reads;
- request IDs/status persistence;
- tests for send, read, broadcast, invalid recipient, plan, and shutdown flows.

Checkpoint: a deterministic two-teammate task with a complete message log and
tests for no dead-inbox/lost-request failures.

### Stage 6: Scale / backend

Status: pending and gated. Add only when serial eval becomes a real bottleneck.

Build:

- local `Job` / `JobStore` queue interface first;
- Ray executor for parallel eval rollouts only after isolation and eval are real;
- optional service mode only after CLI reliability.

Checkpoint: N eval tasks run in parallel with isolation preserved, and the repo
records speedup plus cost/stability tradeoff.

## Backend And RL Learning Track

`private/agent-plan/PLAN_0604.md` reframes backend and RL as one pipeline:
harness environment -> rollout/backend infra -> RL training loop. Backend here
means eval/rollout infra such as async execution, queueing, sandboxing, model
serving, Ray, vLLM, Docker, and eventually verl-style rollout systems. It does
not mean a separate CRUD web project.

Confirmed sequencing:

- learn RL theory now in parallel at low bandwidth;
- learn backend by scaling Stage-2 eval into Stage 6;
- answer RL first through Stage-3 trajectory and reward data;
- do not fake RL training before data and eval are real.
