# Wiki Log

## [2026-05-24] init | repo wiki seeded

Initialized the repo-scoped LLM-maintained knowledge layer. Seeded it from
`AGENTS.md`, `README.md`, the internship alignment plan now located at
`private/report/internship-alignment-plan.md`, historical root prototype files,
`private/report/*.md`, `bugs/1.md`, and `tmp/minimal_team_task_report.md`.

## [2026-05-24] report | OSS coding-agent harness survey added

Added `private/report/agent_harness_OSS.md`, a GitHub-sourced survey of
open-source coding-agent harnesses grouped by primary implementation language.
Updated the wiki source map to include OSS coding-agent harness references under
reports.

## [2026-05-24] evals | minimal eval layer added

Added the first case-based local eval layer under `evals/`. Documented static
artifact scoring, optional live-agent smoke runs through `main.py --prompt-file`,
`MCC_TRACE_PATH` JSONL trace output, and report output under `tmp/eval_runs/`.

## [2026-05-24] report | TypeScript startup guide added

Added `private/report/TS_basic/`, a focused TypeScript startup guide for reading
coding-agent repositories. Updated the wiki source map to include the new report
directory.

## [2026-05-24] report | OSS harness survey source-readability pass

Revised `private/report/agent_harness_OSS.md` with a stricter source-readable
filter. Promoted concrete source roots for each kept project, switched OpenHands
guidance to prefer `OpenHands/software-agent-sdk` for harness internals, and
moved archived, shut-down, or adjacent projects out of the main learning list.

## [2026-05-28] wiki | src package rewrite

Rewrote the wiki around `src/my_claude_code/`, the unified `Runtime.agent_loop`,
role-based tool and manager registries, package entrypoints, persistence dirs,
and current team/message-bus design lessons.

## [2026-06-03] design | logging design recorded

Wrote `private/design/logging.md`: the agreed append-only JSONL run-log design
(`session`/`message`/`tool_call`/`compaction` records, a monotonic `seq` instead
of pi's `parentId` tree, truncate-with-byte-count capture, a swappable `Recorder`
sink, and the `run_tool_call`/`agent_loop`/`compaction` seams). Not yet
implemented.

## [2026-06-04] roadmap | realigned to private/agent-plan/PLAN.md + backend/RL learning track

Rewrote `roadmap.md` to match `private/agent-plan/PLAN.md` (2026-05-30) as the
authoritative source. Fixed phase drift: PLAN.md orders eval (Stage 2) and
RL-data (Stage 3) BEFORE multi-agent (Stage 5) and backend (Stage 6); the old
page had multi-agent early and RL/backend last. Adopted PLAN.md's blunt priority
(Stage 2 = interview-getter, depth-on-eval-over-breadth) and per-stage
checkpoints. Added a "Learning Track: Backend & RL (Seed-aligned)" section:
harness→backend→RL is one pipeline; RL theory starts now in parallel; backend
enters by scaling the Stage-2 eval harness into Stage 6 (Ray); RL answered by
Stage-3 data design first, tiny GRPO capstone optional.

## [2026-06-04] roadmap | RL research + external curriculum at ~/Topic/RL/

Ran a 2026 web research pass on agentic RL (GRPO standard; DAPO/GSPO refinements;
RLVR = test pass/fail as reward; verl/HybridFlow = ByteDance Seed stack; Spinning
Up + CleanRL + TRL GRPOTrainer as the learn-by-implementing path). Created a full
RL curriculum at `~/Topic/RL/` (`README.md`, `LEARNING_PLAN.md`, `RESEARCH.md`) —
6 phases + capstone, each mapped to an MCC stage, grounded with sources. Added a
back-pointer subsection to `roadmap.md` and an addendum (§7) to
`private/agent-plan/PLAN_0604.md`. Fit: Phases 3–4 → Stage 3 reward design;
Phase 5 → Stage 6 Ray rollouts; capstone = GRPO with the eval harness as the
RLVR environment. `~/Topic/RL/` is outside this repo (separate topic dir).

## [2026-06-05] wiki | root llm_wiki realigned to current package skeleton

Realigned the root `llm_wiki/` pages to the current `src/my_claude_code/`
skeleton: `tools/contracts.py` is the live contract layer, `llm_wiki/` is the
active wiki, roadmap sources are under `private/agent-plan/` and
`private/report/`, teammate mode is parked behind the lead registry, and current
session logging/eval status includes the `nbytes` vs `output_bytes` test
mismatch.

## [2026-06-05] wiki | post-review stale-reference cleanup

Adjusted `index.md` and `README.md` after the AGENTS rewrite so they no longer
claim `AGENTS.md` still points to `.agents/llm_wiki/`. Kept the stale-reference
warning scoped to older notes/log entries and other pre-refactor paths.
