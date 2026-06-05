# LLM Wiki

This root `llm_wiki/` directory is the repo-scoped, LLM-maintained knowledge
layer for `my-claude-code`. It gives future agents a concise ground truth for
stable project facts: architecture, decisions, roadmap state, bug lessons, and
evaluation/logging direction.

The wiki is not more authoritative than the implementation. When facts conflict,
prefer current source in `src/my_claude_code/`, `pyproject.toml`, and `README.md`.
For roadmap intent, prefer `private/agent-plan/PLAN.md`,
`private/agent-plan/PLAN_0604.md`, and then
`private/report/internship-alignment-plan.md`.

## What Belongs Here

- project identity and internship-facing direction;
- current architecture at module and boundary level;
- durable design decisions and the reason behind them;
- reusable bug lessons and semantic failure patterns;
- current eval/logging evidence, plus next evaluation targets;
- notes on stale docs or path drift that future agents should not repeat.

## What Does Not Belong Here

- inventories of every function or line;
- temporary run status that belongs in commits, issues, or runtime dirs;
- copied instructions already maintained in `AGENTS.md`;
- claims about upstream `learn-claude-code` that were not checked locally;
- legacy root-monolith internals if the package layout has replaced them.

## Maintenance

Read [index.md](index.md) before non-trivial project work. Update pages when a
stable project fact, design decision, roadmap state, bug lesson, or evaluation
conclusion changes. Append exactly one concise entry to [log.md](log.md) for
each wiki update.

As of 2026-06-05, older notes or log entries may still mention
`.agents/llm_wiki/`, root `report/`, root `main.py`, or `tools/context.py`.
Treat those as historical path references unless current source reintroduces
them; the maintained wiki is this root `llm_wiki/`.
