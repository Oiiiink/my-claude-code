# Wiki Index

Start here before using the repo wiki. The root `llm_wiki/` directory is the
current repo-scoped wiki. Current source remains authoritative.

## Core Pages

- [README.md](README.md): wiki purpose, scope, update rules, and authority.
- [project_overview.md](project_overview.md): project identity and current source snapshot.
- [architecture.md](architecture.md): current `src/my_claude_code/` runtime, contracts, roles, tools, managers, and state.
- [roadmap.md](roadmap.md): current stage status against the private build plans.
- [decisions.md](decisions.md): durable design choices and why they exist.
- [bugs_and_lessons.md](bugs_and_lessons.md): reusable failure patterns and current source/test lessons.
- [evals.md](evals.md): current evaluation evidence and target eval direction.
- [log.md](log.md): append-only wiki maintenance history.

## Current Source Map

- Live package: `src/my_claude_code/`.
- Entrypoint and packaging: `python -m my_claude_code`, `src/my_claude_code/__main__.py`, `src/my_claude_code/cli.py`, `pyproject.toml`.
- Public docs: `README.md`; agent instructions: `AGENTS.md` and `CLAUDE.md`.
- Current roadmap sources: `private/agent-plan/PLAN.md` plus `private/agent-plan/PLAN_0604.md`.
- Older positioning source: `private/report/internship-alignment-plan.md`.
- Runtime state dirs: `.skills/`, `.tasks/`, `.team/`, `.sessions/`, `.transcripts/`.

## Known Stale External References

Do not copy these paths back into wiki pages without rechecking the checkout:
older wiki log entries and pre-refactor notes may mention `.agents/llm_wiki/`,
root `internship-alignment-plan.md`, root `report/`, root `main.py`, or
`tools/context.py`. The current repo wiki is `llm_wiki/`, current
roadmap/report sources live under `private/`, the package entrypoint is
`python -m my_claude_code`, and tool contracts live in `tools/contracts.py`.
