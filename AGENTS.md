# My Claude Code Agent Guide

This repo is a Python 3.12 `uv` project for building a minimal Coding Agent Engineering Harness: a runnable tool-calling coding agent with safer tools, session logging, compaction, task state, and early multi-agent pieces. It is inspired by `learn-claude-code`, but do not overfit to that repo. Treat `pi` as the higher-quality reference design when comparing agent architecture.

## Source Truth

- Live behavior is in `src/my_claude_code/`; current code beats wiki or stale docs.
- `pyproject.toml` defines package metadata, Python version, dependencies, and dev tools.
- `README.md` has quickstart and current project direction.
- Root `llm_wiki/` holds maintained architecture, roadmap, decisions, lessons, and eval notes.
- `bugs/` is for durable mistake notes. Tell the user before editing it.

## Current Skeleton

- `src/my_claude_code/__main__.py` and `cli.py`: CLI entrypoint and interactive prompt loop.
- `runtime.py`: `Runtime`, agent loop, Anthropic call, compaction triggers, background/inbox notifications, and manager composition.
- `config.py`: environment loading, model/workdir constants, and runtime state paths.
- `tools/contracts.py`: `ToolContext`, `ToolSpec`, `ToolCall`, `ToolCheck`, and `ToolResult`.
- `tools/registry.py`: tool registry, role allowlists, parameter checks, approval gate, execution, and finalization.
- `tools/`: filesystem, shell/background, todo, task board, skill loading, compaction, and multi-agent tool groups.
- `managers/`: todo, skills, tasks, background jobs, sessions, team state, and message bus.
- `compaction/`: token estimation plus micro/auto compaction helpers.
- `test/`: current pytest tests.

## Wiki Use

- Before non-trivial architecture, refactor, debugging, roadmap, memory, multi-agent, or evaluation work, read `llm_wiki/index.md` and then only the pages needed.
- Treat wiki pages as maintained context, not source of truth. Recheck current code, README, and pyproject before making factual claims.
- Update `llm_wiki/` only when a stable project fact, design decision, bug lesson, roadmap state, or evaluation conclusion changes; append one entry to `llm_wiki/log.md`.
- If a relevant task does not need a wiki update, say `wiki unchanged: <reason>` in the final response.

## Ignored, Private, And Runtime State

Do not edit these unless the user explicitly asks:

- Private/local files: `.env`, `todo.md`, `private/`, `CLAUDE.md`.
- Agent/runtime state: `.sessions/`, `.skills/`, `.tasks/`, `.team/`, `.transcripts/`.
- Agent tool state: `.agents/`, `.claude/`, `.codex/`.
- Generated/cache output: `.venv/`, `__pycache__/`, `.pytest_cache/`, build/dist artifacts, wheels, egg-info.

## Verification

- Preferred full check: `uv run python -m pytest -q`.
- If `uv` cache/setup is not usable but `.venv` already exists, use `.venv/bin/python -m pytest -q`.
- Manual CLI smoke test, only when useful and `.env` is configured: `uv run python -m my_claude_code`.
- Do not run network commands unless the user asks or approves.

## Working Rules

- Prefer elegant, minimal implementations that make the project easier to understand.
- Help the user understand the design; this is a learning and portfolio project, not just a code dump.
- Use `uv` for project commands.
- Ask focused questions when they would deepen the user's understanding or avoid a wrong design turn.
- Keep edits scoped. Preserve user changes, check the worktree before editing, and do not touch runtime/private/generated paths casually.
- Prefer `rg` and `sed` for inspection.
- Avoid flowcharts in direct TUI answers because they render poorly there. Flowcharts are fine when creating markdown files.
