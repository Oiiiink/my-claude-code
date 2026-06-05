# Project Overview

`my-claude-code` is a personal Coding Agent Engineering Harness inspired by
`learn-claude-code`, but its local direction is now broader than cloning. The
project is meant to study how LLM agents call tools, edit files, coordinate
helpers, preserve state, and eventually evaluate coding-task performance.

## Current Identity

The live implementation is the `src/my_claude_code/` package. The runnable entry
is `python -m my_claude_code`, wired through `__main__.py` and `cli.py`.
Packaging is declared in `pyproject.toml`.

The strategic goal comes from `internship-alignment-plan.md`: build a practical
portfolio artifact for coding-agent infrastructure, not a generic chatbot or
front-end product.

## Current Scope

The project currently centers on a CLI agent harness:

- one `Runtime.agent_loop` shared by lead, subagent, and teammate roles;
- structured tools routed through `tools/registry.py`;
- mutable state owned by managers under `managers/`;
- local runtime state under `.skills/`, `.tasks/`, `.team/`, and
  `.transcripts/`;
- compaction helpers under `compaction/`.

Source evidence: `src/my_claude_code/runtime.py`, `tools/registry.py`,
`managers/registry.py`, and `config.py`.

## Direction

The near-term direction is to make the package reliable and demonstrable before
adding larger systems features. Priority remains:

1. keep the runnable prototype stable;
2. tighten tool safety and runtime validation;
3. add tests and a coding feedback loop;
4. make multi-agent coordination deliberate rather than accidental;
5. add benchmark-style evaluation evidence;
6. add memory and trajectory modules after the core loop is trustworthy.

Root monolith files such as `main.py` or `s_full.py`, when present, should be
treated as historical snapshots rather than current behavior.
