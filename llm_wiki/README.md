# LLM Wiki

This is the repo-scoped, LLM-maintained knowledge layer for `my-claude-code`.
It helps future agents start from stable project facts instead of rediscovering
the same architecture, roadmap, and failure lessons from source every session.

The wiki is not the source of truth for implementation details. Current code in
`src/my_claude_code/`, plus `AGENTS.md`, `CLAUDE.md`, and the project reports,
are authoritative when they disagree with this wiki.

## What Belongs Here

- project identity and internship-facing direction;
- current architecture at the level of modules and boundaries;
- durable design decisions and the reason behind them;
- reusable bug lessons and semantic failure patterns;
- stable evaluation observations backed by repo artifacts.

## What Does Not Belong Here

- stale inventories of every file or function;
- temporary status notes that belong in commits, issues, or `tmp/`;
- copied project instructions already maintained in `AGENTS.md`;
- claims about upstream `learn-claude-code` that were not checked locally;
- legacy `main.py` internals now replaced by the package layout.

## Maintenance

Follow the wiki protocol in `AGENTS.md`. In short: read [index.md](index.md)
before non-trivial project work, update pages when stable knowledge changes,
and append exactly one entry to [log.md](log.md) for each wiki update.

Prefer concise synthesis with links to source paths. If a claim about runtime
behavior cannot be tied to current source or a durable artifact, verify it or
leave it out.
