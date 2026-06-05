# Wiki Log

## [2026-05-24] init | repo wiki seeded

Initialized `.agents/llm_wiki/` as the repo-scoped LLM-maintained knowledge
layer. Seeded it from `AGENTS.md`, `README.md`, `internship-alignment-plan.md`,
`main.py`, `report/*.md`, `bugs/1.md`, and
`tmp/minimal_team_task_report.md`.

## [2026-05-24] report | OSS coding-agent harness survey added

Added `report/agent_harness_OSS.md`, a GitHub-sourced survey of open-source
coding-agent harnesses grouped by primary implementation language. Updated the
wiki source map to include OSS coding-agent harness references under reports.

## [2026-05-24] evals | minimal eval layer added

Added the first case-based local eval layer under `evals/`. Documented static
artifact scoring, optional live-agent smoke runs through `main.py --prompt-file`,
`MCC_TRACE_PATH` JSONL trace output, and report output under `tmp/eval_runs/`.

## [2026-05-24] report | TypeScript startup guide added

Added `report/TS_basic/`, a focused TypeScript startup guide for reading
coding-agent repositories. Updated the wiki source map to include the new
report directory.

## [2026-05-24] report | OSS harness survey source-readability pass

Revised `report/agent_harness_OSS.md` with a stricter source-readable filter.
Promoted concrete source roots for each kept project, switched OpenHands
guidance to prefer `OpenHands/software-agent-sdk` for harness internals, and
moved archived, shut-down, or adjacent projects out of the main learning list.

## [2026-05-28] wiki | src package rewrite

Rewrote the wiki around `src/my_claude_code/`, the unified `Runtime.agent_loop`,
role-based tool and manager registries, package entrypoints, persistence dirs,
and current team/message-bus design lessons.

## [2026-06-03] design | logging design recorded

Wrote `design/logging.md`: the agreed append-only JSONL run-log design
(`session`/`message`/`tool_call`/`compaction` records, a monotonic `seq` instead
of pi's `parentId` tree, truncate-with-byte-count capture, a swappable `Recorder`
sink, and the `run_tool_call`/`agent_loop`/`compaction` seams). Not yet
implemented.

## [2026-06-04] roadmap | realigned to deep-research/PLAN.md + backend/RL learning track

Rewrote `roadmap.md` to match `deep-research/PLAN.md` (2026-05-30) as the
authoritative source. Fixed phase drift: PLAN.md orders eval (Stage 2) and
RL-data (Stage 3) BEFORE multi-agent (Stage 5) and backend (Stage 6); the old
page had multi-agent early and RL/backend last. Adopted PLAN.md's blunt priority
(Stage 2 = interview-getter, depth-on-eval-over-breadth) and per-stage
checkpoints. Added a "Learning Track: Backend & RL (Seed-aligned)" section:
harness→backend→RL is one pipeline; RL theory starts now in parallel; backend
enters by scaling the Stage-2 eval harness into Stage 6 (Ray); RL answered by
Stage-3 data design first, tiny GRPO capstone optional. Note: `.agents/llm_wiki/`
is untracked by git, so it lives only in the main checkout.

## [2026-06-04] roadmap | RL deep-research + external curriculum at ~/Topic/RL/

Ran a 2026 web research pass on agentic RL (GRPO standard; DAPO/GSPO refinements;
RLVR = test pass/fail as reward; verl/HybridFlow = ByteDance Seed stack; Spinning
Up + CleanRL + TRL GRPOTrainer as the learn-by-implementing path). Created a full
RL curriculum at `~/Topic/RL/` (`README.md`, `LEARNING_PLAN.md`, `RESEARCH.md`) —
6 phases + capstone, each mapped to an MCC stage, grounded with sources. Added a
back-pointer subsection to `roadmap.md` and an addendum (§7) to
`deep-research/PLAN_0604.md`. Fit: Phases 3–4 → Stage 3 reward design; Phase 5 →
Stage 6 Ray rollouts; capstone = GRPO with the eval harness as the RLVR
environment. `~/Topic/RL/` is outside this repo (separate topic dir).
