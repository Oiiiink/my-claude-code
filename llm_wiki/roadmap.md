# Roadmap

Authoritative source: `deep-research/PLAN.md` (2026-05-30), graded against two
real JDs — the DeepSeek **Harness team** R&D JD and the ByteDance **Seed**
Engineering-Harness JD. This page mirrors that plan against the current
`src/my_claude_code/` package state. Source code remains authoritative for
*what exists*; PLAN.md is authoritative for *order and priority*.

## Strategic Direction

Present the project as a **Coding Agent Engineering Harness**: a bounded
tool-calling loop with an enforced execution boundary, a test/verify feedback
loop, a SWE-bench-style **evaluation harness that prints a headline number**,
RL-ready trajectory + reward logging, and persistent cross-session memory.
Thesis: **"Model + Harness = Agent."**

## Priority (blunt, from PLAN.md §7)

Depth on eval beats breadth on features. Order by signal, not by stage number:

1. **Stage 2 — Eval harness + feedback loop + headline number**  ← the interview-getter
2. **Stage 1 — Bounded harness core / execution boundary**       ← the JD's hardest line
3. **Stage 3 — RL-ready trajectories + failure analysis**        ← cheap, very high signal
4. **Stage 0 — Always-runs reliability**                         ← table stakes
5. **Stage 4 — Persistent memory**                               ← user's interest + real frontier
6. **Stage 5 — Multi-agent, finished**                           ← only after 1–3 are solid
7. **Stage 6 — Ray/queue scale**                                 ← only on a real bottleneck

> Correction note (2026-06-04): the previous version of this page ordered
> multi-agent as an early phase and pushed RL/backend to the very end. PLAN.md
> deliberately places **eval (2) and RL-data (3) before multi-agent (5)**.
> Multi-agent and backend are explicitly *resist-the-pull* items.

## Stage Status (PLAN.md stage ↔ current src state)

### Stage 0 — Always-runs reliability
Status: partly achieved. Runs via `python -m my_claude_code`; monolith retired.
Remaining: smoke test (import + validate every tool schema), regression test for
the `tool_use`/`tool_result` settlement bug (see `bugs/1.md`), hide unfinished
multi-agent tools behind the role registry so a demo can't crash.
Checkpoint: cold clone completes "read→edit→check→summarize" with zero unhandled
exceptions; `uv run pytest` green; a 30s GIF in README.

### Stage 1 — Bounded harness core / execution boundary
Status: in progress. `tools/registry.py` + `ToolContext`/`ToolSpec` exist;
`filesystem.py` has workdir path containment.
Remaining: `safe_path()` hardening (block escapes, `.env`/`.git`/`.venv`,
oversized reads); **bounded shell** (timeout, output-length cap, workdir jail,
allowlist or explicit unsafe-mode flag); structured **JSONL logging of every
tool call** (seed of Stage-3 trajectories); pi-style tree-structured JSONL
session storage.
Checkpoint: a written **threat table** — ≥6 unsafe actions, each blocked/bounded,
each with a test.

### Stage 2 — Feedback loop + evaluation harness (CENTERPIECE)
Status: pending. The single highest-signal stage; "the stage that gets you the
interview."
Build: a `run_tests` *structured* tool (parsed pass/fail, not raw shell); the
plan→edit→run-tests→read-failure→retry loop (bounded iterations, explicit
failure state, per-run transcript); a mini eval harness on SWE-bench mechanics
(task-spec schema, per-task isolation — git-reset fixture minimum, Docker per
task ideal; patch-apply as a *distinct* failure state from test-failure;
test-transition scoring). Run 5–10 tiny local tasks; do NOT run full SWE-bench.
Checkpoint: `report/eval-v1.md` with a reproducible **headline pass-rate** from
`uv run python -m my_claude_code.eval`.

### Stage 3 — RL-ready trajectories + failure analysis
Status: pending. Answers the RL JD lines via *data design*, not training.
Build: trajectory JSONL schema (ordered observation/action/result + final reward
+ metadata, replayable); reward fields (binary RLVR test-pass + auxiliary: edit
size, safety violations, cost, time; note which tokens are loss-masked); a
`report/failure-analysis-v1.md` with a failure taxonomy (planning / localization
/ modification / execution / recovery).
Checkpoint: trajectory file round-trips; reward fn has a unit test; 1–2pp
failure writeup with one harness improvement it drove.

### Stage 4 — Persistent cross-session memory
Status: pending. Compaction alone is insufficient (Anthropic, Nov 2025).
Build: on-disk memory artifacts (progress log, descriptive git commits,
structured state file); initializer step vs per-session coding step; layer with
block-based compaction (summary + full content on disk + lost-content labels).
Checkpoint: kill mid-task, restart cold, agent reconstructs state and finishes.

### Stage 5 — Multi-agent, finished
Status: experimental. `TeamManager`, `MessageBus`, teammate spawning exist.
Only after Stages 0–3 are solid.
Remaining: deliberate lifecycle, validated names, durable `.team/config.json`,
message IDs + `inbox_history.jsonl`, tests for send/read/broadcast/invalid/
shutdown.

### Stage 6 — Scale / backend (gated)
Status: pending. Add ONLY when serial eval becomes a real bottleneck.
Build: local `Job`/`JobStore` queue interface first, then **Ray** as the
executor for parallel eval rollouts with per-task isolation preserved; optional
FastAPI service mode only after the CLI is rock solid.
Checkpoint: N eval tasks run in parallel via Ray with isolation; you can state
the speedup and the cost/stability tradeoff.

## Learning Track: Backend & RL (Seed-aligned)

The Seed JD's agent-harness + backend + RL are one pipeline —
**harness (environment) → backend (rollout infra at scale) → RL (training loop
that consumes trajectories)**. MCC already owns the harness layer. "Backend" =
rollout/eval infra (async, queue, sandbox, model serving), **not** web/CRUD;
the on-target stack is Ray + vLLM + Docker (+ ByteDance's open-source **verl**
as the canonical agentic-RL framework to study). "RL" = the agentic slice
(policy-gradient → PPO/RLHF → **GRPO / RL-with-verifiable-rewards**), where the
harness's test pass/fail is the verifiable reward.

Sequencing decision (confirmed with user 2026-06-04):

- **RL theory** runs as a parallel low-bandwidth track starting now (Spinning Up
  → PPO → RLHF → GRPO/verl). Compounding, independent of project code state,
  serves the long-term base-model aim.
- **Backend** is inserted by scaling the **Stage 2** eval harness into **Stage 6**
  (run 1 task → run N tasks across workers via Ray). Learned by doing, not as a
  separate web project. Sandboxed execution upgrades Stage 1.
- **RL** is answered first by **Stage 3 data design** (trajectory + reward), then
  optionally a capstone: a tiny GRPO/PPO run on a small open model with the
  harness as environment. Do NOT fake RL training before the data is real.

### Detailed RL curriculum (external)

The full RL learning plan now lives at **`~/Topic/RL/`** (created 2026-06-04):
`LEARNING_PLAN.md` (6 phases + capstone, each mapped to an MCC stage),
`RESEARCH.md` (2026 deep-research digest — GRPO/DAPO/GSPO, RLVR, agentic RL, verl),
`README.md` (framing). The phase→stage map: Phases 3–4 (RLHF→RLVR→GRPO) feed
**Stage 3** reward design; Phase 5 (agentic RL + Ray/vLLM/Docker/verl) is the
blueprint for **Stage 6**; the capstone is a tiny GRPO run with the MCC eval
harness as the RLVR environment. Recheck against `~/Topic/RL/` before RL work.
